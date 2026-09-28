import json
from celery import Celery
from celery.schedules import crontab
from datetime import datetime,timezone
from schemas.dbmodels import TaskDB,CommentDB
from config import settings
from sqlalchemy import create_engine,or_
from sqlalchemy.orm import sessionmaker
import redis as sync_redis
from config import settings
import logging
from services.ai_client import resumes

logger = logging.getLogger(__name__)

redis_client = sync_redis.Redis.from_url(settings.REDIS_URL)
engine = create_engine(settings.DB_URL_SYNC)

session = sessionmaker(bind=engine, autoflush=False, autocommit=False)

c_app = Celery("celery_app",broker=settings.REDIS_URL)

@c_app.task
def task_deadline():
    db = session()
    try:
        tasks = db.query(TaskDB).filter(TaskDB.deadline<=datetime.now(timezone.utc),TaskDB.status != "overdue").all()
        projects=[]
        for task in tasks:
            task.status = "overdue"
            projects.append((task.project_id,task.title))
        db.commit()
        logger.info(f"Marked {len(tasks)} tasks as overdue")
    except Exception:
        logger.exception("Failed to process overdue tasks")
        db.rollback()
        return
    finally:
        db.close()
    
    for project_id, title in projects:
        try:
            redis_client.publish("task_update", json.dumps({"project_id": project_id, "message": f"Task {title} is overdue"}))
        except Exception:
            logger.exception(f"Failed to publish update for project {project_id}")
    
c_app.conf.beat_schedule = {
    "check-deadlines-daily": {
        "task": "celery_app.task_deadline",
        "schedule": crontab(hour=1,minute=0),
    },
}

@c_app.task
def make_resume():
    db = session()
    projects = []
    try:
        tasks = db.query(TaskDB).join(CommentDB, TaskDB.id == CommentDB.task_id).filter(
            or_(TaskDB.summary_updated_at.is_(None), TaskDB.summary_updated_at < CommentDB.created_at)
        ).distinct().all()

        for task in tasks:
            comments = db.query(CommentDB.text).filter(CommentDB.task_id == task.id).all()
            comment_texts = [c.text for c in comments]

            summary = resumes(comment_texts)

            task.comments_summary = summary
            task.summary_updated_at = datetime.now(timezone.utc)

            projects.append((task.project_id, task.title))

        db.commit()
        logger.info(f"Updated summary for {len(tasks)} tasks")
    except Exception:
        logger.exception("Failed to process summary comment")
        return
    finally:
        db.close()

    for project_id, title in projects:
        try:
            redis_client.publish("task_update", json.dumps({"project_id": project_id, "message": f"Task {title} summary was updated"}))
        except Exception:
            logger.exception(f"Failed to publish update for project {project_id}")

c_app.conf.beat_schedule = {
    "check_summary_tasks":{
        "task": "celery_app.make_resume",
        "schedule": crontab(hour=1, minute=1),
    },
}