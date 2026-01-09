import os

from sqlalchemy.dialects import registry
from sqlalchemy.engine import URL
from sqlalchemy.testing import engines

# Register your dialect
registry.register(
    "auroradsql",
    "aurora_dsql_sqlalchemy.psycopg2",
    "AuroraDSQLDialect_psycopg2",
)
registry.register(
    "auroradsql.psycopg2",
    "aurora_dsql_sqlalchemy.psycopg2",
    "AuroraDSQLDialect_psycopg2",
)

registry.register(
    "auroradsql.psycopg",
    "aurora_dsql_sqlalchemy.psycopg",
    "AuroraDSQLDialect_psycopg",
)


original_testing_engine = engines.testing_engine


def custom_testing_engine(url=None, options=None, *, asyncio=False):
    cluster_user = os.environ.get("CLUSTER_USER", None)
    assert cluster_user is not None, "CLUSTER_USER environment variable is not set"

    cluster_endpoint = os.environ.get("CLUSTER_ENDPOINT", None)
    assert (
        cluster_endpoint is not None
    ), "CLUSTER_ENDPOINT environment variable is not set"

    driver = os.environ.get("DRIVER", None)
    assert driver is not None, "DRIVER environment variable is not set"

    # Connection params are the same for both drivers
    conn_params = {
        "host": cluster_endpoint,
        "user": cluster_user,
        "dbname": "postgres",
        "sslmode": "verify-full",
        "sslrootcert": "./root.pem",
        "application_name": "sqlalchemy",
    }

    # Import the appropriate connector based on driver
    if driver == "psycopg":
        import aurora_dsql_psycopg as dsql_connector

        def creator():
            return dsql_connector.DSQLConnection.connect(**conn_params)
    else:
        import aurora_dsql_psycopg2 as dsql_connector

        def creator():
            return dsql_connector.connect(**conn_params)

    url = URL.create(
        f"auroradsql+{driver}",
        username=cluster_user,
        host=cluster_endpoint,
        database="postgres",
    )
    print(f"Using custom URL from environment: {url}")

    options = {"creator": creator}
    engine = original_testing_engine(url, options, asyncio=asyncio)

    return engine


engines.testing_engine = custom_testing_engine

# Import SQLAlchemy testing components
from sqlalchemy.testing.plugin.pytestplugin import *  # noqa
