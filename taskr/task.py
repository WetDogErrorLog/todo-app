from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort
import datetime
from taskr.auth import login_required
from taskr.db import get_db
from sqlite3 import Connection
import logging

logging.basicConfig(level=logging.DEBUG)

bp = Blueprint("task", __name__)


def list_tasks(db: Connection):
    tasks = db.execute(
        "SELECT t.id, author_id, task_name, create_time, delete_time, u.username"
        " FROM task t JOIN user u ON t.author_id = u.id"
        " ORDER BY delete_time DESC NULLS FIRST, create_time DESC"
    ).fetchall()
    return tasks


@login_required
def create(db, task_name: str) -> int:
    logging.info(f"Creating a new task: {request.method}")
    task_name = request.form["task_name"]
    error = None

    if not task_name:
        error = "Task name is required"
    if error is not None:
        flash(error)
    task_id = db.execute(
        "INSERT INTO task (task_name, author_id) VALUES (?, ?) RETURNING id",
        (task_name, g.user["id"])
    ).fetchone()[0]
    
    flash("success")
    return  task_id

def get_task(id, check_author=True):
    task = (
        get_db()
        .execute(
            "SELECT t.id, task_name, create_time, delete_time, author_id, username"
            " FROM task t JOIN user u ON t.author_id = u.id"
            " WHERE t.id = ?",
            (id,),
        )
        .fetchone()
    )

    if task is None:
        abort(404, f"Post id {id} does not exist")
    if check_author and task["author_id"] != g.user["id"]:
        abort(403)

    return task


@bp.route("/<int:id>/update", methods=["GET", "POST"])
@login_required
def update(id):
    logging.info(f"Updating a task: {request.method}")
    task = get_task(id)

    if request.method == "POST":
        task_name = request.form["task_name"]
        set_delete = request.form["delete_task"]
        error = None
        delete_time = None
        if set_delete:
            delete_time = datetime.datetime.now()

        if not task_name:
            error = "Task name is required"

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "UPDATE task SET task_name = ?, delete_time = ?" " WHERE id = ?",
                (task_name, delete_time, id),
            )
            db.commit()
            return redirect(url_for("task_list.index"))

    return render_template("task_list/update.html", task=task)


@bp.route("/<int:id>/delete", methods=["POST"])
@login_required
def delete(id):
    logging.info("Deleting a task")
    get_task(id)
    db = get_db()
    db.execute("UPDATE task SET delete_time = DATETIME('now') WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("task_list.index"))
