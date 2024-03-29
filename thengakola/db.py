import mysql.connector
import click

from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    if "db" not in g:
        g.db = mysql.connector.connect(user="python")
        g.db.cursor().execute("create database if not exists thengakola")
        g.db.commit()
        g.db = mysql.connector.connect(user="python", database="thengakola")

    return g.db


def close_db(e=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()
    crs = db.cursor(dictionary=True)

    with current_app.open_resource("schema.sql") as f:
        try:
            for _ in crs.execute(f.read(), multi=True):
                pass
        except RuntimeError:
            pass
        db.commit()


@click.command("init-db")
@with_appcontext
def init_db_command():
    # Clear existing data and create new tables
    init_db()
    click.echo("Initialized database")


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
