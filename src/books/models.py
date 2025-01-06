from datetime import datetime, date, timezone
from typing import Optional
import sqlalchemy.dialects.postgresql as pg
from sqlmodel import SQLModel, Field, Column, Relationship

import uuid

from src.auth import models


class Book(SQLModel, table=True):
    __tablename__ = "books"

    uid: uuid.UUID = Field(
        primary_key=True,
        default_factory=uuid.uuid4
    )
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str
    user_uid: Optional[uuid.UUID] = Field(default=None, foreign_key="users.uid")
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP(timezone=True), default=datetime.now(timezone.utc)))
    updated_at: datetime = Field(
        sa_column=Column(
            pg.TIMESTAMP(timezone=True),
            nullable=False,
            default=lambda: datetime.now(timezone.utc),
            onupdate=lambda: datetime.now(timezone.utc),
        )
    )
    user: Optional["models.User"] = Relationship(back_populates="books")

    def __repr__(self):
        return f"<Book {self.title}>"
