import os

import boto3
from sqlalchemy import event
from sqlalchemy.dialects import registry
from sqlalchemy.engine import URL
from sqlalchemy.testing import engines

# Register your dialect
registry.register(
    "auroradsql",
    "auroradsql_sqlalchemy.psycopg2",
    "AuroraDSQLDialect_psycopg2",
)
registry.register(
    "auroradsql.psycopg2",
    "auroradsql_sqlalchemy.psycopg2",
    "AuroraDSQLDialect_psycopg2",
)

registry.register(
    "auroradsql.psycopg",
    "auroradsql_sqlalchemy.psycopg",
    "AuroraDSQLDialect_psycopg",
)


original_testing_engine = engines.testing_engine


def custom_testing_engine(
    url=None,
    options=None,
    asyncio=False,
    transfer_staticpool=False,
    share_pool=False,
    _sqlite_savepoint=False,
):
    cluster_user = os.environ.get("CLUSTER_USER", None)
    assert cluster_user is not None, "CLUSTER_USER environment variable is not set"

    cluster_endpoint = os.environ.get("CLUSTER_ENDPOINT", None)
    assert (
        cluster_endpoint is not None
    ), "CLUSTER_ENDPOINT environment variable is not set"

    region = os.environ.get("REGION", None)
    assert region is not None, "REGION environment variable is not set"

    client = boto3.client("dsql", region_name=region)

    url = URL.create(
        "auroradsql+psycopg2",
        username=cluster_user,
        host=cluster_endpoint,
        database="postgres",
        query={"sslmode": "verify-full", "sslrootcert": "./root.pem"},
    )
    print(f"Using custom URL from environment: {url}")

    options = {}
    engine = original_testing_engine(
        url, options, asyncio, transfer_staticpool, share_pool, _sqlite_savepoint
    )

    @event.listens_for(engine, "do_connect")
    def add_token_to_params(dialect, conn_rec, cargs, cparams):
        # Generate a fresh token for this connection
        fresh_token = client.generate_db_connect_admin_auth_token(
            cluster_endpoint, region
        )
        # Update the password in connection parameters
        cparams["password"] = fresh_token

    return engine


engines.testing_engine = custom_testing_engine

# Import SQLAlchemy testing components
from sqlalchemy.testing.plugin.pytestplugin import *  # noqa
