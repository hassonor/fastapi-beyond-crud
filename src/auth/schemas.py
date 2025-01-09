from datetime import datetime
import uuid

from pydantic import BaseModel, Field
from typing import List
from src.db.models import Book


class UserCreateModel(BaseModel):
    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)
    username: str = Field(max_length=8)
    email: str = Field(max_length=45)
    password: str = Field(min_length=7)


class UserModel(BaseModel):
    uid: uuid.UUID
    username: str
    email: str
    first_name: str
    last_name: str
    is_verified: bool
    password_hash: str = Field(exclude=True)
    created_at: datetime
    updated_at: datetime


class UserBooksModel(UserModel):
    books: List[Book]


class UserLoginModel(BaseModel):
    email: str = Field(max_length=45)
    password: str = Field(min_length=7)
