from sqlalchemy.dialects.postgresql.psycopg import PGDialect_psycopg

from .base import AuroraDSQLDialect


class AuroraDSQLDialect_psycopg(PGDialect_psycopg, AuroraDSQLDialect):
    driver = "psycopg"  # driver name
    supports_statement_cache = True

    # This disables the native hstore support. When enabled, this feature
    # checks if the hstore feature is available. During this check, a savepoint
    # is created which causes an error in DSQL.
    def __init__(self, **kwargs):
        kwargs.setdefault("use_native_hstore", False)
        super().__init__(**kwargs)
