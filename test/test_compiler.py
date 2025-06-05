from sqlalchemy import (
    Column,
    Index,
    Integer,
    MetaData,
    String,
    Table,
    schema,
)
from sqlalchemy.testing import fixtures
from sqlalchemy.testing.assertions import AssertsCompiledSQL

from auroradsql_sqlalchemy.psycopg2 import AuroraDSQLDialect_psycopg2


class CompileTest(fixtures.TestBase, AssertsCompiledSQL):
    __dialect__ = AuroraDSQLDialect_psycopg2()
    # __dialect__ = postgresql.dialect()

    def test_create_index_with_ops(self):
        m = MetaData()
        tbl = Table(
            "testtbl",
            m,
            Column("data", String),
            Column("data2", Integer, key="d2"),
        )

        idx = Index(
            "test_idx1",
            tbl.c.data,
            auroradsql_ops={"data": "text_pattern_ops"},
        )

        idx2 = Index(
            "test_idx2",
            tbl.c.data,
            tbl.c.d2,
            auroradsql_ops={"data": "text_pattern_ops", "d2": "int4_ops"},
        )

        self.assert_compile(
            schema.CreateIndex(idx),
            "CREATE INDEX ASYNC test_idx1 ON testtbl (data text_pattern_ops)",
            dialect=AuroraDSQLDialect_psycopg2(),
        )
        self.assert_compile(
            schema.CreateIndex(idx2),
            "CREATE INDEX ASYNC test_idx2 ON testtbl "
            "(data text_pattern_ops, data2 int4_ops)",
            dialect=AuroraDSQLDialect_psycopg2(),
        )


"""

    @testing.combinations(
        (
            lambda tbl: schema.CreateIndex(
                Index(
                    "test_idx1",
                    tbl.c.data,
                    unique=True,
                    postgresql_nulls_not_distinct=True,
                )
            ),
            "CREATE UNIQUE INDEX test_idx1 ON test_tbl " "(data) NULLS NOT DISTINCT",
        ),
        (
            lambda tbl: schema.CreateIndex(
                Index(
                    "test_idx2",
                    tbl.c.data2,
                    unique=True,
                    postgresql_nulls_not_distinct=False,
                )
            ),
            "CREATE UNIQUE INDEX test_idx2 ON test_tbl " "(data2) NULLS DISTINCT",
        ),
        (
            lambda tbl: schema.CreateIndex(
                Index(
                    "test_idx3",
                    tbl.c.data3,
                    unique=True,
                )
            ),
            "CREATE UNIQUE INDEX test_idx3 ON test_tbl (data3)",
        ),
    )
    def test_create_index_with_labeled_ops(self):
        m = MetaData()
        tbl = Table(
            "testtbl",
            m,
            Column("data", String),
            Column("data2", Integer, key="d2"),
        )

        idx = Index(
            "test_idx1",
            func.lower(tbl.c.data).label("data_lower"),
            postgresql_ops={"data_lower": "text_pattern_ops"},
        )

        idx2 = Index(
            "test_idx2",
            (func.xyz(tbl.c.data) + tbl.c.d2).label("bar"),
            tbl.c.d2.label("foo"),
            postgresql_ops={"bar": "text_pattern_ops", "foo": "int4_ops"},
        )

        self.assert_compile(
            schema.CreateIndex(idx),
            "CREATE INDEX test_idx1 ON testtbl " "(lower(data) text_pattern_ops)",
            dialect=postgresql.dialect(),
        )
        self.assert_compile(
            schema.CreateIndex(idx2),
            "CREATE INDEX test_idx2 ON testtbl "
            "((xyz(data) + data2) text_pattern_ops, "
            "data2 int4_ops)",
            dialect=postgresql.dialect(),
        )

    def test_create_index_with_text_or_composite(self):
        m = MetaData()
        tbl = Table("testtbl", m, Column("d1", String), Column("d2", Integer))

        idx = Index("test_idx1", text("x"))
        tbl.append_constraint(idx)

        idx2 = Index("test_idx2", text("y"), tbl.c.d2)

        idx3 = Index(
            "test_idx2",
            tbl.c.d1,
            text("y"),
            tbl.c.d2,
            postgresql_ops={"d1": "x1", "d2": "x2"},
        )

        idx4 = Index(
            "test_idx2",
            tbl.c.d1,
            tbl.c.d2 > 5,
            text("q"),
            postgresql_ops={"d1": "x1", "d2": "x2"},
        )

        idx5 = Index(
            "test_idx2",
            tbl.c.d1,
            (tbl.c.d2 > 5).label("g"),
            text("q"),
            postgresql_ops={"d1": "x1", "g": "x2"},
        )

        self.assert_compile(
            schema.CreateIndex(idx), "CREATE INDEX test_idx1 ON testtbl (x)"
        )
        self.assert_compile(
            schema.CreateIndex(idx2),
            "CREATE INDEX test_idx2 ON testtbl (y, d2)",
        )
        self.assert_compile(
            schema.CreateIndex(idx3),
            "CREATE INDEX test_idx2 ON testtbl (d1 x1, y, d2 x2)",
        )

        # note that at the moment we do not expect the 'd2' op to
        # pick up on the "d2 > 5" expression
        self.assert_compile(
            schema.CreateIndex(idx4),
            "CREATE INDEX test_idx2 ON testtbl (d1 x1, (d2 > 5), q)",
        )

        # however it does work if we label!
        self.assert_compile(
            schema.CreateIndex(idx5),
            "CREATE INDEX test_idx2 ON testtbl (d1 x1, (d2 > 5) x2, q)",
        )

    def test_create_index_expr_gets_parens(self):
        m = MetaData()
        tbl = Table("testtbl", m, Column("x", Integer), Column("y", Integer))

        idx1 = Index("test_idx1", 5 // (tbl.c.x + tbl.c.y))
        self.assert_compile(
            schema.CreateIndex(idx1),
            "CREATE INDEX test_idx1 ON testtbl ((5 / (x + y)))",
        )

    def test_create_index_literals(self):
        m = MetaData()
        tbl = Table("testtbl", m, Column("data", Integer))

        idx1 = Index("test_idx1", tbl.c.data + 5)
        self.assert_compile(
            schema.CreateIndex(idx1),
            "CREATE INDEX test_idx1 ON testtbl ((data + 5))",
        )

    # Create one similar for ASYNC
    def test_create_index_concurrently(self):
        m = MetaData()
        tbl = Table("testtbl", m, Column("data", Integer))

        idx1 = Index("test_idx1", tbl.c.data, postgresql_concurrently=True)
        self.assert_compile(
            schema.CreateIndex(idx1),
            "CREATE INDEX CONCURRENTLY test_idx1 ON testtbl (data)",
        )

        dialect_8_1 = postgresql.dialect()
        dialect_8_1._supports_create_index_concurrently = False
        self.assert_compile(
            schema.CreateIndex(idx1),
            "CREATE INDEX test_idx1 ON testtbl (data)",
            dialect=dialect_8_1,
        )

    # Create one similar for ASYNC
    def test_drop_index_concurrently(self):
        m = MetaData()
        tbl = Table("testtbl", m, Column("data", Integer))

        idx1 = Index("test_idx1", tbl.c.data, postgresql_concurrently=True)
        self.assert_compile(schema.DropIndex(idx1), "DROP INDEX CONCURRENTLY test_idx1")

        dialect_9_1 = postgresql.dialect()
        dialect_9_1._supports_drop_index_concurrently = False
        self.assert_compile(
            schema.DropIndex(idx1), "DROP INDEX test_idx1", dialect=dialect_9_1
        )

    def test_index_extra_include_1(self):
        metadata = MetaData()
        tbl = Table(
            "test",
            metadata,
            Column("x", Integer),
            Column("y", Integer),
            Column("z", Integer),
        )
        idx = Index("foo", tbl.c.x, postgresql_include=["y"])
        self.assert_compile(
            schema.CreateIndex(idx), "CREATE INDEX foo ON test (x) INCLUDE (y)"
        )

    def test_index_extra_include_2(self):
        metadata = MetaData()
        tbl = Table(
            "test",
            metadata,
            Column("x", Integer),
            Column("y", Integer),
            Column("z", Integer),
        )
        idx = Index("foo", tbl.c.x, postgresql_include=[tbl.c.y])
        self.assert_compile(
            schema.CreateIndex(idx), "CREATE INDEX foo ON test (x) INCLUDE (y)"
        )
"""
