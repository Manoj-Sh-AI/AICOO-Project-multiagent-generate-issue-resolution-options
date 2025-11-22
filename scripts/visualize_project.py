import sys
from pathlib import Path
from datetime import datetime, date, timedelta
from typing import Optional
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.lines import Line2D
from matplotlib.dates import DateFormatter
import numpy as np

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from services.db import get_session, init_db
from crud.project import load_project_by_id, get_all_project_ids
from models.main import Project, Task, Mail

STATUS_COLORS = {
    "To Do": "#E0E0E0",
    "In Progress": "#2196F3",
    "Done": "#4CAF50",
    "Blocked": "#F44336",
    "Canceled": "#9E9E9E",
    "Paused": "#FF9800",
}


def visualize_project(project: Project, save_path: Optional[str] = None):
    fig = plt.figure(figsize=(16, 10))
    gs = fig.add_gridspec(2, 1, hspace=0.3, wspace=0.3)

    ax1 = fig.add_subplot(gs[0, :])
    ax2 = fig.add_subplot(gs[1, :])

    fig.suptitle(f"Project: {project.title}", fontsize=16, fontweight="bold")

    if project.description:
        fig.text(
            0.5,
            0.96,
            project.description,
            ha="center",
            fontsize=10,
            style="italic",
            alpha=0.7,
        )

    plot_gantt_chart(ax1, project)
    plot_mail_timeline(ax2, project)

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"Visualization saved to {save_path}")
    else:
        plt.show()


def plot_gantt_chart(ax, project: Project):
    if not project.tasks:
        ax.text(0.5, 0.5, "No tasks available", ha="center", va="center", fontsize=12)
        ax.set_title("Gantt Chart - Tasks Timeline", fontsize=12, fontweight="bold")
        return

    tasks = sorted(
        project.tasks,
        key=lambda t: (
            t.start_date or t.created_at.date()
            if hasattr(t.created_at, "date")
            else date.today()
        ),
        reverse=False,
    )

    task_id_to_index = {task.id: i for i, task in enumerate(tasks)}

    y_positions = np.arange(len(tasks))
    task_names = []
    start_dates = []
    end_dates = []
    colors = []

    min_date = None
    max_date = None

    for task in tasks:
        task_names.append(task.name[:30] + "..." if len(task.name) > 30 else task.name)

        if task.start_date:
            start = task.start_date
        else:
            start = (
                task.created_at.date()
                if hasattr(task.created_at, "date")
                else date.today()
            )

        if task.deadline:
            end = task.deadline
        else:
            end = start

        start_dates.append(start)
        end_dates.append(end)
        colors.append(STATUS_COLORS.get(task.status, "#CCCCCC"))

        if min_date is None or start < min_date:
            min_date = start
        if max_date is None or end > max_date:
            max_date = end

    if min_date and max_date:
        date_range = (max_date - min_date).days
        if date_range == 0:
            date_range = 1
            max_date = min_date + timedelta(days=1)

        for i, (task, start, end, color, name) in enumerate(
            zip(tasks, start_dates, end_dates, colors, task_names)
        ):
            start_days = (start - min_date).days
            duration = (end - start).days if end >= start else 1

            bar = ax.barh(
                i,
                duration,
                left=start_days,
                color=color,
                alpha=0.7,
                edgecolor="black",
                linewidth=0.5,
            )

            min_text_width = date_range * 0.08
            if duration > min_text_width:
                ax.text(
                    start_days + duration / 2,
                    i,
                    name,
                    ha="center",
                    va="center",
                    fontsize=7,
                    fontweight="bold",
                    color="black",
                )
            elif duration > date_range * 0.02:
                ax.text(
                    start_days + duration + date_range * 0.01,
                    i,
                    name,
                    ha="left",
                    va="center",
                    fontsize=7,
                    color="black",
                )

        for i, task in enumerate(tasks):
            if task.predecessor_task_ids:
                task_start_days = (start_dates[i] - min_date).days

                for pred_id in task.predecessor_task_ids:
                    if pred_id in task_id_to_index:
                        pred_idx = task_id_to_index[pred_id]
                        pred_end_days = (end_dates[pred_idx] - min_date).days

                        x_start = pred_end_days
                        y_start = pred_idx
                        x_end = task_start_days
                        y_end = i

                        arrow = FancyArrowPatch(
                            (x_start, y_start),
                            (x_end, y_end),
                            arrowstyle="->",
                            mutation_scale=15,
                            color="red",
                            linewidth=1.5,
                            alpha=0.6,
                            linestyle="--",
                            zorder=0,
                        )
                        ax.add_patch(arrow)

        ax.set_yticks(y_positions)
        ax.set_yticklabels(task_names, fontsize=9)
        ax.set_xlabel("Days from project start", fontsize=10)
        ax.set_title(
            "Gantt Chart - Tasks Timeline (with dependencies)",
            fontsize=12,
            fontweight="bold",
        )
        ax.grid(axis="x", alpha=0.3)
        ax.set_ylim(-0.5, len(tasks) - 0.5)
        ax.set_xlim(-date_range * 0.05, date_range * 1.1)

        legend_elements = [
            mpatches.Patch(color=color, label=status)
            for status, color in STATUS_COLORS.items()
        ]
        dependency_line = Line2D(
            [0], [0], color="red", label="Dependencies", linestyle="--", linewidth=1.5
        )
        legend_elements.append(dependency_line)
        ax.legend(handles=legend_elements, loc="upper right", fontsize=8)
    else:
        ax.text(
            0.5,
            0.5,
            "No date information available",
            ha="center",
            va="center",
            fontsize=12,
        )


def plot_mail_timeline(ax, project: Project):
    if not project.mails:
        ax.text(0.5, 0.5, "No mails available", ha="center", va="center", fontsize=12)
        ax.set_title("Mail Timeline", fontsize=12, fontweight="bold")
        return

    mails = sorted(project.mails, key=lambda m: m.written_at or m.created_at)

    mail_dates = []
    mail_subjects = []

    for mail in mails:
        if mail.written_at:
            mail_dates.append(mail.written_at)
        else:
            mail_dates.append(mail.created_at)
        mail_subjects.append(
            mail.subject[:40] + "..." if len(mail.subject) > 40 else mail.subject
        )

    if mail_dates:
        y_positions = np.arange(len(mails))

        ax.scatter(
            mail_dates,
            y_positions,
            s=100,
            alpha=0.6,
            color="blue",
            edgecolors="black",
            linewidths=1,
        )

        for i, (date_val, subject) in enumerate(zip(mail_dates, mail_subjects)):
            ax.annotate(
                subject,
                xy=(date_val, i),
                xytext=(5, 0),
                textcoords="offset points",
                fontsize=8,
                va="center",
            )

        ax.set_yticks(y_positions)
        ax.set_yticklabels([f"Mail {i+1}" for i in range(len(mails))], fontsize=9)
        ax.set_xlabel("Date", fontsize=10)
        ax.set_title("Mail Timeline", fontsize=12, fontweight="bold")
        ax.grid(axis="x", alpha=0.3)

        ax.xaxis.set_major_formatter(DateFormatter("%Y-%m-%d %H:%M"))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha="right")


def plot_task_status_pie(ax, project: Project):
    if not project.tasks:
        ax.text(0.5, 0.5, "No tasks available", ha="center", va="center", fontsize=12)
        ax.set_title("Task Status Distribution", fontsize=12, fontweight="bold")
        return

    status_counts = {}
    for task in project.tasks:
        status = task.status
        status_counts[status] = status_counts.get(status, 0) + 1

    if status_counts:
        labels = list(status_counts.keys())
        sizes = list(status_counts.values())
        colors_list = [STATUS_COLORS.get(status, "#CCCCCC") for status in labels]

        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=labels,
            colors=colors_list,
            autopct="%1.1f%%",
            startangle=90,
            textprops={"fontsize": 9},
        )

        for autotext in autotexts:
            autotext.set_color("white")
            autotext.set_fontweight("bold")

        ax.set_title("Task Status Distribution", fontsize=12, fontweight="bold")


def plot_task_dependencies(ax, project: Project):
    if not project.tasks:
        ax.text(0.5, 0.5, "No tasks available", ha="center", va="center", fontsize=12)
        ax.set_title("Task Dependencies", fontsize=12, fontweight="bold")
        return

    task_dict = {task.id: task for task in project.tasks}
    has_dependencies = any(task.predecessor_task_ids for task in project.tasks)

    if not has_dependencies:
        ax.text(0.5, 0.5, "No task dependencies", ha="center", va="center", fontsize=12)
        ax.set_title("Task Dependencies", fontsize=12, fontweight="bold")
        return

    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_title("Task Dependencies", fontsize=12, fontweight="bold")

    task_positions = {}
    tasks_with_deps = [t for t in project.tasks if t.predecessor_task_ids]

    if not tasks_with_deps:
        return

    positions = np.linspace(1, 9, len(tasks_with_deps))

    for i, task in enumerate(tasks_with_deps):
        y_pos = positions[i]
        task_positions[task.id] = (5, y_pos)

        box = FancyBboxPatch(
            (4, y_pos - 0.3),
            2,
            0.6,
            boxstyle="round,pad=0.1",
            facecolor=STATUS_COLORS.get(task.status, "#CCCCCC"),
            edgecolor="black",
            linewidth=1,
        )
        ax.add_patch(box)

        task_name = task.name[:15] + "..." if len(task.name) > 15 else task.name
        ax.text(
            5, y_pos, task_name, ha="center", va="center", fontsize=8, fontweight="bold"
        )

        for pred_id in task.predecessor_task_ids:
            if pred_id in task_positions:
                pred_pos = task_positions[pred_id]
                arrow = FancyArrowPatch(
                    pred_pos,
                    (5, y_pos),
                    arrowstyle="->",
                    mutation_scale=20,
                    color="gray",
                    linewidth=1.5,
                    alpha=0.6,
                )
                ax.add_patch(arrow)


if __name__ == "__main__":
    init_db()
    with get_session() as session:
        project_ids = get_all_project_ids(session=session)
        for project_id in project_ids:
            project = load_project_by_id(session=session, project_id=project_id)
            visualize_project(project, save_path=f"project_{project_id}.png")
            break
