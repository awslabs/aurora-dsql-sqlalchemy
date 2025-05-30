# Amazon Aurora DSQL dialect for SQLAlchemy

## Prerequisites

The following libraries are required to connect to Aurora DSQL:

- sqlalchemy
- psycopg2-binary

To install these libraries use the following:

```
    pip install -e .

```

After the aurora dsql dialect installation, you should be able to connect to the cluster via create_engine

```
     url = URL.create(
        "aurora_dsql+psycopg2",
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

"aurora_dsql+psycopg2" specifies to use the `aurora_dsql` dialect with the driver `psycopg2`

## Integration Tests

The following libraries are required to run the integration tests:

- boto3
- pytest

To run the test use the following:

```
    pip install -e '.[test]'
    export CLUSTER_ENDPOINT=<YOUR_CLUSTER_HOSTNAME>
    export CLUSTER_USER=admin
    export REGION=us-east-1
    pytest
```

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This project is licensed under the Apache-2.0 License.
