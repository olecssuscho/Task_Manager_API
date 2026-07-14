from datetime import datetime,timezone

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, Enum, ForeignKey

class Base(DeclarativeBase):
    pass

class UserDB(Base):

    __tablename__ = "Users"

    id : Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email : Mapped[str]
    password : Mapped[str]
    fulname : Mapped[str]
    role : Mapped[str]
    refresh_token : Mapped[str]
    created_at : Mapped[datetime] = mapped_column(DateTime(timezone=True), default = lambda: datetime.now(timezone.utc))

class ProjectDB(Base):

    __tablename__ = "Projects"

    id : Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name : Mapped[str]
    description : Mapped[str]
    owner_id : Mapped[int] = mapped_column(ForeignKey("Users.id"))
    created_at : Mapped[datetime] = mapped_column(DateTime(timezone=True), default = lambda: datetime.now(timezone.utc))

class ProjectMemberDB(Base):

    __tablename__ = "ProjectMembers"

    id : Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    project_id : Mapped[int] = mapped_column(ForeignKey("Projects.id")) 
    user_id : Mapped[int] = mapped_column(ForeignKey("Users.id"))
    role : Mapped[str] = mapped_column(Enum("owner","editor","viewer",name = "role"), default = "viewer")
    joined_at : Mapped[datetime] = mapped_column(DateTime(timezone=True), default = lambda: datetime.now(timezone.utc))

class TaskDB(Base):

    __tablename__ = "Tasks"   

    id : Mapped[int] = mapped_column(primary_key=True, autoincrement=True)   
    title : Mapped[str]
    description : Mapped[str]
    status : Mapped[str] = mapped_column(Enum("todo","in_progress","review","done", name = "status"), default = "todo")  
    priority : Mapped[str] = mapped_column(Enum("low","medium","high",name = "priority"), default = "medium")   
    deadline : Mapped[datetime]
    project_id : Mapped[int] = mapped_column(ForeignKey("Projects.id")) 
    assignee_id : Mapped[int] = mapped_column(ForeignKey("Users.id"),nullable=True) 
    created_by : Mapped[int] = mapped_column(ForeignKey("Users.id"))
    created_at : Mapped[datetime] = mapped_column(DateTime(timezone=True), default = lambda: datetime.now(timezone.utc))
    updated_at : Mapped[datetime] = mapped_column(DateTime(timezone=True), default = lambda: datetime.now(timezone.utc))  