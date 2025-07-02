# Amazon Aurora DSQL dialect for SQLAlchemy

Amazon Aurora DSQL dialect for SQLAlchemy enables Python applications to connect to and interact with Aurora DSQL databases using the SQLAlchemy ORM.

## Prerequisites

- Python 3.9 or higher
- SQLAlchemy 2.0.0 or higher

### Drivers

psycopg2

- psycopg2-binary 2.9.0 or higher

psycopg (psycopg3)

- psycopg 3.2.0 or higher

## Installation

### Install the packages directly from the repository:

[TODO] to be removed once this package is pushed to pypi

```
pip install .

# driver installation
pip install '.[psycopg2]'

# psycopg (psycopg3)
pip install '.[psycopg]'

```

Install the packages

```
pip install aurora-dsql-sqlalchemy

# driver installation
pip install psycopg2-binary

# psycopg (psycopg3)
pip install psycopg-binary

```

## Usage

After installation, you can connect to an Aurora DSQL cluster using SQLAlchemy's create_engine:

```
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL

url = URL.create(
    "auroradsql+psycopg",
    username=admin,
    host=<CLUSTER_END_POINT>,
    password=<CLUSTER_TOKEN>,
    database='postgres',
    query={
        # (optional) If sslmode is 'verify-full' then use sslrootcert
        # variable to set the path to server root certificate
        # If no path is provided, the adapter looks into system certs
        # NOTE: Do not use it with 'sslmode': 'require'
        'sslmode': 'verify-full',
        'sslrootcert': '<ROOT_CERT_PATH>'
    }
)

engine = create_engine(url)
```

The connection string "auroradsql+psycopg" specifies to use the `auroradsql` dialect with the driver `psycopg` (psycopg3)
To use the driver `psycopg2` , change the connection string to "auroradsql+psycopg2".

Note: Each connection has a maximum duration limit. See the `Maximum connection duration` time limit in the [Cluster quotas and database limits in Amazon Aurora DSQL](https://docs.aws.amazon.com/aurora-dsql/latest/userguide/CHAP_quotas.html) page.

# Best Practices

### Primary Key Generation

SQLAlchemy applications connecting to Aurora DSQL should use UUID for the primary key column since auto-incrementing integer keys (sequences or serial) are not supported in DSQL. The following column definition can be used to define an UUID primary key column.

```
Column(
    "id",
    UUID(as_uuid=True),
    primary_key=True,
    default=text('gen_random_uuid()')
)
```

`gen_random_uuid()` returns UUID version 4 as the default value

# Dialect Features and Limitations

- Psycopg (psycopg3) Support: When connecting to DSQL using the default postgresql dialect with psycopg, an unsupported `SAVEPOINT` error occurs. The DSQL dialect addresses this issue by disabling the `SAVEPOINT` during connection.
- Index Creation: The DSQL dialect generates the correct syntax for index creation
  `CREATE INDEX ASYNC`

  The following parameters are used for customizing index creation

  - `auroradsql_include` - specifies which columns to includes in an index by using the `INCLUDE` clause

    ```
    Index(
        "include_index",
        table.c.id,
        auroradsql_include=['name', 'email']
    )

    # Generated SQL
     CREATE INDEX ASYNC include_index ON table (id) INCLUDE (name, email)
    ```

  - `auroradsql_nulls_not_distinct` - controls how NULL values are treated in unique indexes

    ```
    Index(
        "idx_name",
        table.c.column,
        unique=True,
        auroradsql_nulls_not_distinct=True
    )

    # Generated SQL
    CREATE UNIQUE INDEX idx_name ON table (column) NULLS NOT DISTINCT

    ```

    ### Index Interface Limitation

  - `NULLS FIRST | LAST` - SQLalchemy's Index() interface does not have a way to pass in the sort order of null and non-null columns. (Default: `NULLS LAST`). If `NULLS FIRST` is required, please refer to the syntax as specified in [Asynchronous indexes in Aurora DSQL](https://docs.aws.amazon.com/aurora-dsql/latest/userguide/working-with-create-index-async.html) and execute the corresponding SQL query directly in SQLAlchemy.

- Foreign Keys: DSQL does not support foreign key constraints. The dialect disables foreign key creation. Note that referential integrity must be maintained at the application level.
- Column Metadata: The dialect fixes an issue related to "datatype json not supported" when calling SQLAlchemy's metadata() API.

## Integration Tests

The following libraries are required to run the integration tests:

- boto3
- pytest

To run the test use the following:

```
# Clone the entire repository
git clone https://github.com/awslabs/aurora-dsql-sqlalchemy.git
cd aurora-dsql-sqlalchemy

# Download the Amazon root certificate from the official trust store:
wget https://www.amazontrust.com/repository/AmazonRootCA1.pem -O root.pem

pip install '.[test,psycopg]' # add psycopg2 if testing via psycopg2

export CLUSTER_ENDPOINT=<YOUR_CLUSTER_HOSTNAME>
export CLUSTER_USER=admin
export REGION=us-east-1
export DRIVER=psycopg # use 'psycopg' for psycopg3 and 'psycopg2' for psycopg2
pytest
```

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This project is licensed under the Apache-2.0 License.
