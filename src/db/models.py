from typing import List, Optional
from sqlmodel import SQLModel, Field, Column, Relationship
import sqlalchemy.dialects.postgresql as pg
from datetime import datetime, timezone, date
import uuid

from src.books.schemas import Book


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
    books: List["Book"] = Relationship(back_populates="user", sa_relationship_kwargs={'lazy': 'selectin'})

    def __repr__(self):
        return f"<User {self.username}>"


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
    user: Optional[User] = Relationship(back_populates="books")

    def __repr__(self):
        return f"<Book {self.title}>"
