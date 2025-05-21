import setuptools

setuptools.setup(     
     name="aurora-dsql-sqlalchemy",     
     version="0.0.1",
     python_requires=">=3.9",   
     packages=["aurora_dsql_sqlalchemy"],
     entry_points={
        "sqlalchemy.dialects": [
            "aurora_dsql = aurora_dsql_sqlalchemy.psycopg2:AuroraDSQLDialect_psycopg2",
            "aurora_dsql.psycopg2 = aurora_dsql_sqlalchemy.psycopg2:AuroraDSQLDialect_psycopg2"
        ],
    },
)