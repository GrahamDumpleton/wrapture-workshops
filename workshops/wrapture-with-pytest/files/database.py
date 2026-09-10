"""A stand-in for a database layer, with a repository on top.

Database.execute() answers three queries from a dict, so there is no
database to run. The repository's totals() lists the tenants with one
query and then issues one more query per tenant: the classic N+1
shape, which no assertion on its result can see.
"""


class Database:
    def __init__(self):
        self.orders = {"acme": [500, 700, 250], "globex": [120], "initech": [80, 90]}

    def execute(self, sql, *params):
        if sql.startswith("SELECT tenant, amount"):
            return [(tenant, amount) for tenant, amounts in self.orders.items() for amount in amounts]
        if sql.startswith("SELECT tenant"):
            return [(tenant,) for tenant in self.orders]
        if sql.startswith("SELECT amount"):
            return [(amount,) for amount in self.orders.get(params[0], [])]
        raise ValueError(f"unknown query: {sql}")


class Repository:
    def __init__(self, database):
        self.database = database

    def totals(self):
        totals = {}
        for (tenant,) in self.database.execute("SELECT tenant FROM tenants"):
            rows = self.database.execute("SELECT amount FROM orders WHERE tenant = ?", tenant)
            totals[tenant] = sum(amount for (amount,) in rows)
        return totals
