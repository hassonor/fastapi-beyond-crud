from datetime import datetime, date, timezone
import sqlalchemy.dialects.postgresql as pg
from sqlmodel import SQLModel, Field, Column

import uuid


class Book(SQLModel, table=True):
    __tablename__ = "books"

    uid: uuid.UUID = Field(sa_column=Column(
        pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4()))
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP(timezone=True), default=datetime.now(timezone.utc)))
    updated_at: datetime = Field(
        sa_column=Column(
            pg.TIMESTAMP(timezone=True),
            nullable=False,
            default=lambda: datetime.now(timezone.utc),
            onupdate=lambda: datetime.now(timezone.utc),
        )
    )

    def __repr__(self):
        return f"<Book {self.title}>"
