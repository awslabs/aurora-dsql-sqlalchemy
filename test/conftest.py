import os

from sqlalchemy.dialects import registry
from sqlalchemy.testing import engines

from aurora_dsql_sqlalchemy import create_dsql_engine

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


def custom_testing_engine(url=None, options=None, *, asyncio=False):
    cluster_user = os.environ.get("CLUSTER_USER", None)
    assert cluster_user is not None, "CLUSTER_USER environment variable is not set"

    cluster_endpoint = os.environ.get("CLUSTER_ENDPOINT", None)
    assert (
        cluster_endpoint is not None
    ), "CLUSTER_ENDPOINT environment variable is not set"

    driver = os.environ.get("DRIVER", None)
    assert driver is not None, "DRIVER environment variable is not set"

    print(f"Creating DSQL engine for {cluster_endpoint} with driver {driver}")

    # Use the helper function to create the engine
    engine = create_dsql_engine(
        host=cluster_endpoint,
        user=cluster_user,
        driver=driver,
    )

    return engine


engines.testing_engine = custom_testing_engine

# Import SQLAlchemy testing components
from sqlalchemy.testing.plugin.pytestplugin import *  # noqa
