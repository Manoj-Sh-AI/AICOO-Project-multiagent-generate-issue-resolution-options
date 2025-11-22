from typing import List, Optional
from datetime import datetime, date
from sqlmodel import SQLModel, Field, Relationship, Column, Date, Text, JSON
from sqlalchemy.dialects.postgresql import UUID as SQLAlchemyUUID, ARRAY
import uuid
from datetime import UTC


class Project(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(max_length=255, description="Title of the project")
    description: str = Field(default="", description="Description of the project")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    tasks: List["Task"] = Relationship(back_populates="project")
    mails: List["Mail"] = Relationship(back_populates="project")

class Task(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255, description="Name of the task")
    description: str = Field(default="", description="Description of the task")
    project_id: uuid.UUID = Field(foreign_key="project.id")
    project: "Project" = Relationship(back_populates="tasks")
    status: str = Field(default="To Do", description="Status of the task (To Do, In Progress, Done, Blocked, Canceled, Paused)")
    deadline: Optional[date] = Field(default=None, sa_column=Column(Date, nullable=True), description="Deadline of the task")
    assignee_emails: List[str] = Field(default=[], sa_column=Column(ARRAY(Text)), description="List of assignee emails")
    predecessor_task_ids: List[uuid.UUID] = Field(default=[], sa_column=Column(ARRAY(SQLAlchemyUUID(as_uuid=True))), description="List of predecessor task IDs")
    start_date: Optional[date] = Field(default=None, sa_column=Column(Date, nullable=True), description="Start date of the task")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

class Mail(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    project_id: uuid.UUID = Field(foreign_key="project.id")
    project: "Project" = Relationship(back_populates="mails")

    previous_mail_id: Optional[uuid.UUID] = Field(default=None, foreign_key="mail.id")
    previous_mail: Optional["Mail"] = Relationship(
        back_populates="following_mails",
        sa_relationship_kwargs={"remote_side": "Mail.id"},
    )
    following_mails: List["Mail"] = Relationship(back_populates="previous_mail")

    written_at: Optional[datetime] = None
    sender: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    to_recipients: Optional[List[dict]] = Field(default=None, sa_column=Column(JSON))
    cc_recipients: Optional[List[dict]] = Field(default=None, sa_column=Column(JSON))
    subject: str
    body: str

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


# PART TO CONCENTRATE ON RESOLUTION OPTIONS
# here the models you will use to store your resolution options/actions/proposals-mails/...
# class Options():
#     # what you do....
