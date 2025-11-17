from flask import Blueprint, flash, redirect, render_template, request, url_for
from werkzeug.exceptions import abort
from taskr.auth import login_required
from taskr.db import get_db
from sqlite3 import Connection
from .types import types
from typing import List

import logging

logging.basicConfig(level=logging.DEBUG)

bp = Blueprint("tag", __name__)


@bp.route("/tag/")
def index():
    db = get_db()
    tags = list_tags(db)
    return render_template("tag/index.html", tags=tags)

def _localize(tag) -> types.Tag:
    return types.Tag(
        tag_id=tag['id'],
        tag_name=tag['tag_name']
    )

def list_tags(db: Connection) -> List[types.Tag]:
    tags = db.execute("SELECT id, tag_name FROM task_tag ORDER BY tag_name").fetchall()
    types_tags = []
    for tag in tags:
        types_tags.append(_localize(tag))
    return tags


@bp.route("/tag/create", methods=["POST"])
@login_required
def create() -> id:
    if request.method == "POST":
        tag_name = request.form['tag_name']
        if not tag_name:
            flash("Tag name is required")
            return
        else:
            db = get_db()
            db.execute("INSERT INTO task_tag (tag_name) VALUES (?)", (tag_name,))
            db.commit()
    return redirect(url_for("tag.index"))

def get_tag(id) -> types.Tag:
    tag = (
        get_db()
        .execute("SELECT id, tag_name FROM task_tag WHERE id = ?", (id,))
        .fetchone()
    )

    if tag is None:
        abort(404, f"Tag id {id} does not exist")

    return _localize(tag)


@bp.route("/tag/<int:id>/update", methods=("POST",))
@login_required
def update(id):
    logging.info(f"Updating tag id: {id}")
    tag = get_tag(id)

    tag_name = request.form["tag_name"]
    error = None

    if not tag_name:
        error = "Tag name is required"
    if error is not None:
        flash(error)
    else:
        db = get_db()
        db.execute("UPDATE task_tag SET tag_name = ? WHERE id = ?", (tag_name, id))
        db.commit()
        flash("Tag updated successfully")
        return redirect(url_for("tag.index"))

    return redirect(url_for("tag.index"))


@bp.route("/tag/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    logging.info(f"Deleting tag id: {id}")
    get_tag(id)
    db = get_db()
    db.execute("DELETE FROM task_tag WHERE id = ?", (id,))
    db.execute("DELETE FROM task_tag_link WHERE tag_id = ?", (id,))
    db.commit()
    flash("Tag deleted successfully")
    return redirect(url_for("tag.index"))
