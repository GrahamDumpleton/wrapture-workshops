"""A pooled resource and a repository that uses it.

Database.connect() mints a Connection, and a connection answers queries
until close() sets its closed flag. The repository is the code under
test: count() releases its connection on every path out, and find()
releases only when a row was found.
"""


class Connection:
    def __init__(self, number):
        self.number = number
        self.closed = False

    def execute(self, sql):
        if self.closed:
            raise RuntimeError("connection is closed")
        return [(1, "widget")] if "id = 1" in sql else []

    def close(self):
        self.closed = True

    def __repr__(self):
        return f"<Connection {self.number}>"


class Database:
    def __init__(self):
        self.issued = 0

    def connect(self):
        self.issued += 1
        return Connection(self.issued)


class Repository:
    def __init__(self, database):
        self.database = database

    def count(self, table):
        connection = self.database.connect()
        try:
            return len(connection.execute(f"SELECT * FROM {table}"))
        finally:
            connection.close()

    def find(self, table, key):
        connection = self.database.connect()
        rows = connection.execute(f"SELECT * FROM {table} WHERE id = {key}")
        if not rows:
            return None
        connection.close()
        return rows[0]


def report(repository, keys):
    found = [repository.find("products", key) for key in keys]
    return repository.count("products"), [row for row in found if row]
