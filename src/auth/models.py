from typing import List
from sqlmodel import SQLModel, Field, Column, Relationship
import sqlalchemy.dialects.postgresql as pg
from datetime import datetime, timezone
import uuid

from src.books import models


class User(SQLModel, table=True):
    __tablename__ = 'users'

    uid: uuid.UUID = Field(
        primary_key=True,
        default_factory=uuid.uuid4
    )
    username: str
    email: str
    password_hash: str = Field(exclude=True)
    first_name: str
    last_name: str
    role: str = Field(sa_column=Column(pg.VARCHAR, nullable=False, server_default="user"))
    is_verified: bool = Field(default=False)
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP(timezone=True), default=datetime.now(timezone.utc)))
    updated_at: datetime = Field(
        sa_column=Column(
            pg.TIMESTAMP(timezone=True),
            nullable=False,
            default=lambda: datetime.now(timezone.utc),
            onupdate=lambda: datetime.now(timezone.utc),
        )
    )
    books: List["models.Book"] = Relationship(back_populates="user", sa_relationship_kwargs={'lazy': 'selectin'})

    def __repr__(self):
        return f"<User {self.username}>"
