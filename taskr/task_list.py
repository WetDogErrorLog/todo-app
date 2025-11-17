from flask import Blueprint, render_template, request, redirect, url_for
from taskr.auth import login_required
from taskr.db import get_db
import taskr.tag as Tag
import taskr.relationship as Relationship
import taskr.task as Task


import logging

logging.basicConfig(level=logging.DEBUG)

bp = Blueprint("task_list", __name__)


@bp.route("/")
def index():
    db = get_db()
    tasks = Task.list_tasks(db)
    tags = Tag.list_tags(db)
    return render_template("task_list/index.html", tasks=tasks, tags=tags)


@bp.route("/create_task_with_tags", methods=['POST'])
@login_required
def create_task_with_tags():
    db = get_db()
    task_name = request.form["task_name"]
    target_tag_ids = request.form.getlist("selected_tags")
    task_id = Task.create(db=db, task_name=task_name)
    Relationship.create_task_to_tags(db, task_id, target_tag_ids)
    db.commit()
    return redirect(url_for("task_list.index"))
