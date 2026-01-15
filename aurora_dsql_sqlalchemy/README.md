# Aurora DSQL Dialect for SQLAlchemy - Developer instructions

## Clone the repository

```bash
git clone https://github.com/awslabs/aurora-dsql-sqlalchemy.git
cd aurora-dsql-sqlalchemy
```

## Install `uv`

Install `uv` using the [official installation guide](https://docs.astral.sh/uv/getting-started/installation/) or via [mise](https://mise.jdx.dev/).

## Download Amazon root certificate

Download the Amazon root certificate to verify DSQL connections.

```bash
wget https://www.amazontrust.com/repository/AmazonRootCA1.pem -O root.pem
```

## Install dependencies

```bash
uv sync --extra test --extra psycopg
```

Use the `psycopg2` extra when testing against the `psycopg2` driver.

## Configure environment variables

Set the following variables to connect to your cluster:

```bash
export CLUSTER_ENDPOINT=<YOUR_CLUSTER_HOSTNAME>
export CLUSTER_USER=admin
export DRIVER=psycopg
```

Use `DRIVER=psycopg2` when testing against the `psycopg2` driver.

## Running integration tests

```bash
uv run pytest
```
