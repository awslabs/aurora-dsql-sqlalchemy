from sqlalchemy.dialects.postgresql.psycopg2 import PGDialect_psycopg2

from .base import AuroraDSQLDialect


class AuroraDSQLDialect_psycopg2(PGDialect_psycopg2, AuroraDSQLDialect):
    driver = "psycopg2"  # driver name
    supports_statement_cache = True
