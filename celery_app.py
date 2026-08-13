from celery import Celery
from celery.schedules import crontab
from datetime import datetime,timezone
from schemas.dbmodels import TaskDB
from config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(settings.DB_URL_SYNC)

session = sessionmaker(bind=engine, autoflush=False, autocommit=False)

c_app = Celery("celery_app",broker="redis://localhost:6379/0")

@c_app.task
def task_deadline():
    db = session()
    try:
        tasks = db.query(TaskDB).filter(TaskDB.deadline<=datetime.now(timezone.utc),TaskDB.status != "overdue").all()
        for task in tasks:
            task.status = "overdue"
        db.commit()
    finally:
        db.close()

c_app.conf.beat_schedule = {
    "check-deadlines-daily": {
        "task": "celery_app.task_deadline",
        "schedule": crontab(hour=1,minute=0),
    },
}