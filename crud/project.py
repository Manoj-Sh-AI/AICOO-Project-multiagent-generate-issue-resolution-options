from sqlmodel import select, Session
from sqlalchemy.orm import selectinload
from models.projectplan import Project, Mail
import uuid
from typing import List

def load_project_by_id(*, session: Session, project_id: uuid.UUID) -> Project:
    statement = (
        select(Project)
        .where(Project.id == project_id)
        .options(
            selectinload(Project.tasks),
            selectinload(Project.mails).selectinload(Mail.previous_mail),
            selectinload(Project.mails).selectinload(Mail.following_mails)
        )
    )
    return session.exec(statement).first()

def get_all_project_ids(*, session: Session) -> List[uuid.UUID]:
    statement = select(Project.id)
    return list(session.exec(statement).all())