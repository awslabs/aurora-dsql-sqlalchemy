# Amazon Aurora DSQL dialect for SQLAlchemy

Amazon Aurora DSQL dialect for SQLAlchemy enables Python applications to connect to and interact with Aurora DSQL databases using the SQLAlchemy ORM.

## Prerequisites

- Python 3.9 or higher
- SQLAlchemy 2.0.0 or higher
- psycopg2-binary 2.9.0 or higher
- psycopg 3.2.0 or higher

## Installation

Install the packages directly from the repository:

```
pip install -e .
```

## Usage

After installation, you can connect to an Aurora DSQL cluster using SQLAlchemy's create_engine:

```
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL

url = URL.create(
    "auroradsql+psycopg2",
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

The connection string "auroradsql+psycopg2" specifies to use the `auroradsql` dialect with the driver `psycopg2`
To use the driver `psycopg` (psycopg3) , change the connection string to "auroradsql+psycopg".

## Integration Tests

The following libraries are required to run the integration tests:

- boto3
- pytest

To run the test use the following:

```
pip install -e '.[test]'
wget https://www.amazontrust.com/repository/AmazonRootCA1.pem -O root.pem
export CLUSTER_ENDPOINT=<YOUR_CLUSTER_HOSTNAME>
export CLUSTER_USER=admin
export REGION=us-east-1
pytest
```

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This project is licensed under the Apache-2.0 License.
