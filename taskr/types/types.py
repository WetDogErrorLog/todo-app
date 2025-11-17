from datetime import datetime
from typing import Optional
from dataclasses import dataclass

@dataclass
class Tag:
    tag_id: int
    tag_name: str

@dataclass
class Task:
    task_id: int
    author_id: str
    task_name: str
    create_time: datetime
    delete_time: Optional[datetime]
