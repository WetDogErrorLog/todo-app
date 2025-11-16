import os

from flask import Flask
from flask.cli import with_appcontext
import click
import logging
logger = logging.getLogger(__name__)

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flask.sqlite')
    )

    if test_config is None:
        app.config.from_pyfile('conig.py', silent=True)
    else:
        app.config.from_mapping(test_config)
    
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/hello')
    def hello():
        return 'Welcome to the ToDo app'

    # Instantiate database
    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import task_list
    app.register_blueprint(task_list.bp)
    app.add_url_rule('/', endpoint='index')

    from . import tag
    app.register_blueprint(tag.bp)
    app.add_url_rule('/tag/', endpoint='tag.index')

    # Add a db shell
    # Run with: flask db-shell
    # bd_conn.execute("<SQL STATEMENT>")
    @app.cli.command('db-shell')
    @with_appcontext
    def db_shell():
        """Open a database shell."""
        logger.info("Opening database shell")
        db_conn = db.get_db()
        import code
        code.interact(local=dict(globals(), **locals()))
    
    return app