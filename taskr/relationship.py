from flask import Blueprint
from sqlite3 import Connection
from typing import List

import logging

logging.basicConfig(level=logging.DEBUG)

bp = Blueprint("relationship", __name__)


def create_task_to_tags(db: Connection, task_id: int, tag_ids: List[int]) -> List[int]:
    ids = []
    for tag_id in tag_ids:
        relationship_id = db.execute(
            "INSERT INTO task_tag_link (task_id, tag_id)"
            "VALUES(?, ?) RETURNING id",
            (task_id, tag_id),
        ).fetchone()[0]
        ids.append(relationship_id)
    return ids
