# Aurora DSQL Dialect for SQLAlchemy - Developer instructions

## Running integration tests

The following libraries are required to run the integration tests:

- boto3
- pytest

To run the test use the following:

```bash
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
