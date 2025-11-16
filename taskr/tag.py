from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
import datetime
from taskr.auth import login_required
from taskr.db import get_db

import logging
logging.basicConfig(level=logging.DEBUG)

bp = Blueprint('tag', __name__)

@bp.route('/tag/')
def index():
    db = get_db()
    tags = db.execute(
        'SELECT id, tag_name FROM task_tag ORDER BY tag_name'
    ).fetchall()
    return render_template('tag/index.html', tags=tags)

@bp.route('/tag/create', methods=('GET', 'POST'))
@login_required
def create():
    logging.info(f"Creating a new tag: {request.method}")
    if request.method == 'POST':
        tag_name = request.form['tag_name']
        error = None

        if not tag_name:
            error = 'Tag name is required'
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO task_tag (tag_name)'
                ' VALUES (?)',
                (tag_name,)
            )
            db.commit()
            flash("Tag created successfully")
            return redirect(url_for('tag.index'))

    return render_template('tag/create.html')

def get_tag(id):
    tag = get_db().execute(
        'SELECT id, tag_name'
        ' FROM task_tag'
        ' WHERE id = ?',
        (id,)
    ).fetchone()

    if tag is None:
        abort(404, f'Tag id {id} does not exist')
    
    return tag

@bp.route('/tag/<int:id>/update', methods=('POST',))
@login_required
def update(id):
    logging.info(f"Updating tag id: {id}")
    tag = get_tag(id)

    tag_name = request.form['tag_name']
    error = None

    if not tag_name:
        error = 'Tag name is required'
    if error is not None:
        flash(error)
    else:
        db = get_db()
        db.execute(
            'UPDATE task_tag SET tag_name = ? WHERE id = ?',
            (tag_name, id)
        )
        db.commit()
        flash("Tag updated successfully")
        return redirect(url_for('tag.index'))

    return render_template('tag/update.html', tag=tag)

@bp.route('/tag/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    logging.info(f"Deleting tag id: {id}")
    get_tag(id)
    db = get_db()
    db.execute('DELETE FROM task_tag WHERE id = ?', (id,))
    db.execute('DELETE FROM task_tag_link WHERE tag_id = ?', (id,))
    db.commit()
    flash("Tag deleted successfully")
    return redirect(url_for('tag.index'))