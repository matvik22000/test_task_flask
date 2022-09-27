import psycopg2

conn = psycopg2.connect(
    database="beejee",
    user="beejee",
    password="beejee",
    host="192.168.86.164",
    port=5432
)


def requires_connection(func):
    def inner(*args, **kwargs):
        cur = conn.cursor()
        try:
            res = func(cur, *args, **kwargs)
            conn.commit()
            return res
        except Exception as e:
            conn.rollback()
            raise e

    return inner


@requires_connection
def tasks(cur):
    cur.execute("""SELECT * FROM tasks""")
    res = [{k: v.strip() if isinstance(v, str) else v for k, v in
            zip(["id", "email", "name", "description", "completed", "redacted"], row)} for row in cur.fetchall()]
    return res


@requires_connection
def is_admin(cur, username):
    cur.execute("""SELECT is_admin FROM users where username = %s""", (
        username,
    ))
    fetched = cur.fetchall()
    if fetched:
        return fetched[0][0]
    return False


@requires_connection
def get_user(cur, username, pwd):
    cur.execute("""SELECT is_admin FROM users where username = %s and password = %s""", (
        username, pwd
    ))
    fetched = cur.fetchall()
    if fetched:
        return fetched[0][0]
    return False


@requires_connection
def update_task(cur, id, task, redacted):
    if not redacted:
        cur.execute("""UPDATE tasks set description = %s, completed = %s where id = %s""", (
            task["description"], task["completed"], id
        ))
    else:
        cur.execute("""UPDATE tasks set description = %s, completed = %s, redacted = %s where id = %s""", (
            task["description"], task["completed"], redacted, id
        ))


@requires_connection
def create_task(cur, task):
    cur.execute("""INSERT INTO tasks (email, name, description, completed) VALUES (%s, %s, %s, %s) returning id""", (
        task["email"], task["name"], task["description"], task["completed"]
    ))
    return cur.fetchone()[0]
