import sys
from pathlib import Path
import json

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from services.db import get_session, init_db
from crud.project import load_project_by_id, get_all_project_ids
from models.main import Project, Mail

def serialize_project(project: Project) -> dict:
    project_dict = project.model_dump(exclude_unset=False, exclude_defaults=False)
    
    if project.tasks:
        project_dict["tasks"] = [
            task.model_dump(exclude={"project"}, exclude_unset=False, exclude_defaults=False)
            for task in project.tasks
        ]
    
    if project.mails:
        project_dict["mails"] = [
            serialize_mail(mail)
            for mail in project.mails
        ]
    
    return project_dict

def serialize_mail(mail: Mail) -> dict:
    mail_dict = mail.model_dump(exclude={"project"}, exclude_unset=False, exclude_defaults=False)
    
    if mail.previous_mail:
        mail_dict["previous_mail"] = serialize_mail(mail.previous_mail)
    
    if mail.following_mails:
        mail_dict["following_mails"] = [
            serialize_mail(following_mail)
            for following_mail in mail.following_mails
        ]
    
    return mail_dict

init_db()
with get_session() as session:
    project_ids = get_all_project_ids(session=session)
    for project_id in project_ids:
        print("-"*100)
        project = load_project_by_id(session=session, project_id=project_id)
        project_dict = serialize_project(project)
        print(json.dumps(project_dict, indent=2, default=str))