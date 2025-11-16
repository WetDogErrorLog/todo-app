from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
import datetime
from taskr.auth import login_required
from taskr.db import get_db

import logging
logging.basicConfig(level=logging.DEBUG)

bp = Blueprint('task_list', __name__)

@bp.route('/')
def index():
    logging.info("Fetching task list")
    db = get_db()
    tasks = db.execute(
        'SELECT t.id, author_id, task_name, create_time, delete_time, u.username'
        ' FROM task t JOIN user u ON t.author_id = u.id'
        ' ORDER BY delete_time DESC NULLS FIRST, create_time DESC'
    ).fetchall()
    logging.info('about to flash task count')
    flash(len(tasks))
    i = []
    for task in tasks:
        logging.info(f"Task retrieved: {task['task_name']} by {task['username']}")
        i.append(task)
    logging.info(f"Retrieved {len(i)} tasks")
    return render_template('task_list/index.html', tasks=tasks)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    logging.info(f"Creating a new task: {request.method}")
    if request.method == 'POST':
        task_name = request.form['task_name']
        error = None

        if not task_name:
            error = 'Task name is required'
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO task (task_name, author_id)'
                ' VALUES (?, ?)',
                (task_name, g.user['id'])
            )
            db.commit()
            flash("success")
            return redirect(url_for('task_list.index'))

    return render_template('task_list/create.html')

def get_task(id, check_author=True):
    task = get_db().execute(
        'SELECT t.id, task_name, create_time, delete_time, author_id, username'
        ' FROM task t JOIN user u ON t.author_id = u.id'
        ' WHERE t.id = ?',
        (id,)
    ).fetchone()

    if task is None:
        abort(404, f'Post id {id} does not exist')
    if check_author and task['author_id'] != g.user['id']:
        abort(403)
    
    return task

@bp.route('/<int:id>/update', methods=['GET', 'POST'])
@login_required
def update(id):
    logging.info(f"Updating a task: {request.method}")
    task = get_task(id)

    if request.method == 'POST':    
        task_name = request.form['task_name']
        set_delete = request.form['delete_task']
        error = None
        delete_time = None
        if set_delete:
            delete_time = datetime.datetime.now()

        if not task_name:
            error = 'Task name is required'
        
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE task SET task_name = ?, delete_time = ?'
                ' WHERE id = ?',
                (task_name, delete_time, id)
            )
            db.commit()
            return redirect(url_for('task_list.index'))
        
    return render_template('task_list/update.html', task=task)

@bp.route('/<int:id>/delete', methods=['POST'])


@login_required
def delete(id):
    logging.info(f"Deleting a task")
    get_task(id)
    db = get_db()
    db.execute("UPDATE task SET delete_time = DATETIME('now') WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for('task_list.index'))