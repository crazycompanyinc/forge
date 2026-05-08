def get_user(cursor, name):
    cursor.execute("SELECT * FROM users WHERE name = '%s'" % name)
    return cursor.fetchone()
