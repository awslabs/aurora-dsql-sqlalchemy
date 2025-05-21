# Aurora DSQL dialect for SQLAlchemy

## Prerequisites

The following libraries are required to connect to Aurora DSQL

- sqlalchemy
- psycopg2-binary

To install these libraries use the following:

```
    pip install sqlalchemy
    pip install pscycopg2-binary
```

## Install and usage

- Get a copy of the repo
- run the following inside the root directory of the

```
    pip install <full_path_to_repo_root>
```

After the aurora dsql dialect installation, you should be able to connect by creating the sqlalchemy create_engine. Please refer to the sample.py for a simple connection test.

## File Descriptions

- `/aurora_dsql_sqlalchemy/__init__.py` - a file that is executed when imported by python. In this file, the dialect is registered into the sqlalchemy system.
- `/aurora_dsql_sqlalchemy/base.py` - the base implementation of the dialect for the aurora dsql database
  - notice there is a `_supports_create_index_async` flag to indicate whether the keyword ASYNC should be added or not inside a CREATE INDEX sql statement.
- `/aurora_dsql_sqlalchemy/psycopg2.py` - configures which driver sqlalchemy uses
- `/sample.py` - a sqlalchemy quick connect sample using the `aurora_dsql+psycopg2` dialect
- `/setup.py` - a file that manages the information required by pip install and automatically register the aurora dsql dialect into sqlalchemy without explicitly importing the dialect itself as defined in `entry_points`.
  - Note there is a syntax difference between the registration and the usage in sqlalchemy for e.g.
    When regisetering the dialect, the name ` aurora_dsql.psycopg2` is used, but inside sqlalchemy the corresponding dialect becomes `aurora_dsql+psycopg2`

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This project is licensed under the Apache-2.0 License.
