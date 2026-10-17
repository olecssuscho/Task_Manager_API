from datetime import datetime,timezone
import uuid
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, Enum, ForeignKey, Uuid
from pgvector.sqlalchemy import Vector

class Base(DeclarativeBase):
    pass

class UserDB(Base):

    __tablename__ = "Users"

    id : Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email : Mapped[str]
    password : Mapped[str]
    fullname : Mapped[str]
    role : Mapped[str]
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
    project_id : Mapped[int] = mapped_column(ForeignKey("Projects.id", ondelete="CASCADE")) 
    user_id : Mapped[int] = mapped_column(ForeignKey("Users.id"))
    role : Mapped[str] = mapped_column(Enum("owner","editor","viewer",name = "role"), default = "viewer")
    joined_at : Mapped[datetime] = mapped_column(DateTime(timezone=True), default = lambda: datetime.now(timezone.utc))

class TaskDB(Base):

    __tablename__ = "Tasks"   

    id : Mapped[int] = mapped_column(primary_key=True, autoincrement=True)   
    title : Mapped[str]
    description : Mapped[str]
    status : Mapped[str] = mapped_column(Enum("todo","in_progress","review","done","overdue", name = "status"), default = "todo")  
    priority : Mapped[str] = mapped_column(Enum("low","medium","high",name = "priority"), default = "medium")   
    deadline : Mapped[datetime] = mapped_column(DateTime(timezone=True))
    project_id : Mapped[int] = mapped_column(ForeignKey("Projects.id", ondelete="CASCADE")) 
    assignee_id : Mapped[int] = mapped_column(ForeignKey("Users.id"),nullable=True) 
    created_by : Mapped[int] = mapped_column(ForeignKey("Users.id"))
    embedding : Mapped[list[float]] = mapped_column(Vector(1024),nullable=True)
    comments_summary : Mapped[str] = mapped_column(nullable=True)
    summary_updated_at : Mapped[datetime] = mapped_column(DateTime(timezone=True), default = lambda: datetime.now(timezone.utc), nullable=True)
    created_at : Mapped[datetime] = mapped_column(DateTime(timezone=True), default = lambda: datetime.now(timezone.utc))
    updated_at : Mapped[datetime] = mapped_column(DateTime(timezone=True), default = lambda: datetime.now(timezone.utc))  

class CommentDB(Base):

    __tablename__ = "Comments"
    
    id : Mapped[int] = mapped_column(primary_key=True, autoincrement=True)   
    text : Mapped[str]
    task_id : Mapped[int] = mapped_column(ForeignKey("Tasks.id", ondelete="CASCADE"))
    user_id : Mapped[int] = mapped_column(ForeignKey("Users.id"))
    created_at : Mapped[datetime] = mapped_column(DateTime(timezone=True), default = lambda: datetime.now(timezone.utc))

class AttachmentDB(Base):

    __tablename__ = "Attachments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    filename: Mapped[str]
    file_path: Mapped[str]
    content_type: Mapped[str]
    size_bytes: Mapped[int]
    task_id: Mapped[int] = mapped_column(ForeignKey("Tasks.id"))
    uploaded_by: Mapped[int] = mapped_column(ForeignKey("Users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default = lambda: datetime.now(timezone.utc))

class RefreshDB(Base):

    __tablename__ = "Tokens"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("Users.id",ondelete="CASCADE"), index=True)
    token_hash: Mapped[str] = mapped_column(unique=True)
    exp: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    family_id: Mapped[uuid.UUID] = mapped_column(Uuid, index=True)
    used: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    abs_edge: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    revoke_reason: Mapped[str | None] = mapped_column(Enum("Exit","Change password","repeat use","admin",name = "revoke_reason"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default = lambda: datetime.now(timezone.utc))