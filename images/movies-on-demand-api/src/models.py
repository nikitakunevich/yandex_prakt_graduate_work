from datetime import datetime
from enum import Enum
from typing import Dict
from uuid import UUID

from pydantic import BaseModel


class MovieIDRequest(BaseModel):
    id: UUID


class Movie(BaseModel):
    id: UUID
    name: str
    file_name: str
    is_premium: bool
