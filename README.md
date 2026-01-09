# Amazon Aurora DSQL dialect for SQLAlchemy

[![GitHub](https://img.shields.io/badge/github-awslabs/aurora--dsql--sqlalchemy-blue?logo=github)](https://github.com/awslabs/aurora-dsql-sqlalchemy)
[![License](https://img.shields.io/badge/license-Apache--2.0-brightgreen)](https://github.com/awslabs/aurora-dsql-sqlalchemy/blob/main/LICENSE)
[![PyPI - Version](https://img.shields.io/pypi/v/aurora-dsql-sqlalchemy)](https://pypi.org/project/aurora-dsql-sqlalchemy)
[![Discord chat](https://img.shields.io/discord/1435027294837276802.svg?logo=discord)](https://discord.com/invite/nEF6ksFWru)

## Introduction

The Aurora DSQL dialect for SQLAlchemy provides integration between SQLAlchemy ORM and Aurora DSQL. This dialect enables
Python applications to leverage SQLAlchemy's powerful object-relational mapping capabilities while taking advantage of
Aurora DSQL's distributed architecture and high availability.

## Sample Application

There is an included sample application in [examples/pet-clinic-app](https://github.com/awslabs/aurora-dsql-sqlalchemy/tree/main/examples/pet-clinic-app) that shows how to use Aurora DSQL
with SQLAlchemy. To run the included example please refer to the [sample README](https://github.com/awslabs/aurora-dsql-sqlalchemy/tree/main/examples/pet-clinic-app#readme).

## Prerequisites

- Python 3.10 or higher
- SQLAlchemy 2.0.0 or higher
- One of the following drivers:
  - psycopg 3.2.0 or higher
  - psycopg2 2.9.0 or higher

## Installation

Install the packages using the commands below:

```bash
pip install aurora-dsql-sqlalchemy

# driver installation (in case you opt for psycopg)
# DO NOT use pip install psycopg-binary
pip install "psycopg[binary]"

# driver installation (in case you opt for psycopg2)
pip install psycopg2-binary
```

## Dialect Configuration

After installation, you can connect to an Aurora DSQL cluster using SQLAlchemy's `create_engine` with the Aurora DSQL Python Connector.

The connection parameter `auroradsql+psycopg` specifies to use the `auroradsql` dialect with the driver `psycopg` (psycopg3).
To use the driver `psycopg2`, change the connection parameter to `auroradsql+psycopg2`.

```python
import aurora_dsql_psycopg as dsql_connector  # or aurora_dsql_psycopg2
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL

# Create a connection factory using the connector
# The connector handles IAM authentication automatically
def creator():
    return dsql_connector.DSQLConnection.connect(  # use dsql_connector.connect() for psycopg2
        host="<CLUSTER_ENDPOINT>",
        user="<CLUSTER_USER>",
        dbname="postgres",
        sslmode="verify-full",
        sslrootcert="<ROOT_CERT_PATH>",  # or "system" to use system CA store
        application_name="sqlalchemy",
    )

url = URL.create(
    "auroradsql+psycopg",  # or "auroradsql+psycopg2"
    username="<CLUSTER_USER>",
    host="<CLUSTER_ENDPOINT>",
    database="postgres",
)

engine = create_engine(url, creator=creator, pool_size=5, max_overflow=10)
```

**Note:** Each connection has a maximum duration limit. See the `Maximum connection duration` time limit in the [Cluster quotas and database limits in Amazon Aurora DSQL](https://docs.aws.amazon.com/aurora-dsql/latest/userguide/CHAP_quotas.html) page.

## Best Practices

### Primary Key Generation

SQLAlchemy applications connecting to Aurora DSQL should use UUID for the primary key column since auto-incrementing integer keys (sequences or serial) are not supported in DSQL. The following column definition can be used to define an UUID primary key column.

```python
Column(
    "id",
    UUID(as_uuid=True),
    primary_key=True,
    default=text('gen_random_uuid()')
)
```

`gen_random_uuid()` returns an UUID version 4 as the default value.

## Dialect Features and Limitations

- **Column Metadata**: The dialect fixes an issue related to `"datatype json not supported"` when calling SQLAlchemy's metadata() API.
- **Foreign Keys**: Aurora DSQL does not support foreign key constraints. The dialect disables these constraints, but be aware that referential integrity must be maintained at the application level.
- **Index Creation**: Aurora DSQL does not support `CREATE INDEX` or `CREATE UNIQUE INDEX` commands. The dialect instead uses `CREATE INDEX ASYNC` and `CREATE UNIQUE INDEX ASYNC` commands. See the [Asynchronous indexes in Aurora DSQL](https://docs.aws.amazon.com/aurora-dsql/latest/userguide/working-with-create-index-async.html) page for more information.

  The following parameters are used for customizing index creation

  - `auroradsql_include` - specifies which columns to includes in an index by using the `INCLUDE` clause:

    ```python
    Index(
        "include_index",
        table.c.id,
        auroradsql_include=['name', 'email']
    )
    ```

    Generated SQL output:

    ```sql
    CREATE INDEX ASYNC include_index ON table (id) INCLUDE (name, email)
    ```

  - `auroradsql_nulls_not_distinct` - controls how `NULL` values are treated in unique indexes:

    ```python
    Index(
        "idx_name",
        table.c.column,
        unique=True,
        auroradsql_nulls_not_distinct=True
    )
    ```

    Generated SQL output:

    ```sql
    CREATE UNIQUE INDEX idx_name ON table (column) NULLS NOT DISTINCT
    ```

- **Index Interface Limitation**: `NULLS FIRST | LAST` - SQLalchemy's Index() interface does not have a way to pass in the sort order of null and non-null columns. (Default: `NULLS LAST`). If `NULLS FIRST` is required, please refer to the syntax as specified in [Asynchronous indexes in Aurora DSQL](https://docs.aws.amazon.com/aurora-dsql/latest/userguide/working-with-create-index-async.html) and execute the corresponding SQL query directly in SQLAlchemy.
- **Psycopg (psycopg3) support**: When connecting to DSQL using the default postgresql dialect with psycopg, an unsupported `SAVEPOINT` error occurs. The DSQL dialect addresses this issue by disabling the `SAVEPOINT` during connection.

## Developer instructions

Instructions on how to build and test the dialect are available in the [Developer Instructions](https://github.com/awslabs/aurora-dsql-sqlalchemy/tree/main/aurora_dsql_sqlalchemy#readme).

## Security

See [CONTRIBUTING](https://github.com/awslabs/aurora-dsql-sqlalchemy/blob/main/CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This project is licensed under the Apache-2.0 License.
