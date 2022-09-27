import json
import re
from datetime import timedelta
from functools import wraps

from flask import Flask, request, session, abort, render_template
from flask_cors import CORS

import db

app = Flask(__name__,
            static_url_path="",
            static_folder='build',
            template_folder='build')
app.secret_key = 'BAD_SECRET_KEY'
app.config['SESSION_COOKIE_SAMESITE'] = "None"
app.config['SESSION_COOKIE_SECURE'] = "true"
app.permanent_session_lifetime = timedelta(days=1)
CORS(app, supports_credentials=True)


def requires_auth(func):
    @wraps(func)
    def _f(*args, **kwargs):
        print(session)
        if db.is_admin(session.get("username")):
            return func(*args, **kwargs)
        else:
            abort(401)

    return _f


def validate_fields(fields):
    if not sum(map(lambda x: len(x.strip()) if isinstance(x, str) else 1 > 0, fields)):
        abort(400)


def validate_email(email):
    if not re.match(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+', email):
        abort(400)


@app.route("/")
def hello():
    return render_template("index.html")


@app.route('/api/login', methods=["POST", "GET"])
def login():
    if request.method == "POST":
        body = request.get_json()
        if db.get_user(body.get("username"), body.get("pwd")):
            session.permanent = True
            session["username"] = body.get("username")
            return {"isAdmin": True}
        return {"isAdmin": False}
    elif request.method == "GET":
        if not db.is_admin(session.get("username")):
            return {"isAdmin": False}
        return {"isAdmin": True}


@app.route('/api/logout', methods=["POST"])
@requires_auth
def logout():
    print(session)
    session.clear()
    return {"isAdmin": False}


@app.route('/api/update_task', methods=["POST"])
@requires_auth
def update_task():
    body = request.get_json()
    task = body.get("task")

    validate_fields(task.values())
    validate_email(task["email"])
    db.update_task(body.get("id"), task, body.get("redacted"))

    return {"success": True}


@app.route('/api/create_task', methods=["POST"])
def create_task():
    body = request.get_json()
    task = body.get("task")

    validate_fields(task.values())
    validate_email(task["email"])

    return {"id": db.create_task(task)}


@app.route('/api/tasks')
def tasks():
    return json.dumps(db.tasks())


if __name__ == '__main__':
    app.run(debug=True, port=5000, host="0.0.0.0")
