from sqlalchemy.dialects import registry

__version__ = "0.0.0.1"

registry.register("aurora_dsql.psycopg2", "aurora_dsql_sqlalchemy.psycopg2", "AuroraDSQLDialect_psycopg2")
registry.register("aurora_dsql.psycopg", "aurora_dsql_sqlalchemy.psycopg", "AuroraDSQLDialect_psycopg")

