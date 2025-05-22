from sqlalchemy.dialects.postgresql.base import PGDialect
from sqlalchemy.dialects.postgresql.base import PGDDLCompiler
from sqlalchemy.sql import expression

from functools import lru_cache

class AuroraDSQLDDLCompiler(PGDDLCompiler):
     def visit_create_index(self, create, **kw):
            preparer = self.preparer
            index = create.element
            self._verify_index_table(index)
            text = "CREATE "
            if index.unique:
                text += "UNIQUE "

            text += "INDEX "

            if self.dialect._supports_create_index_async: 
                text += "ASYNC "

            if create.if_not_exists:
                text += "IF NOT EXISTS "

            text += "%s ON %s " % (
                self._prepared_index_name(index, include_schema=False),
                preparer.format_table(index.table),
            )

            using = index.dialect_options["postgresql"]["using"]
            if using:
                text += (
                    "USING %s "
                    % self.preparer.validate_sql_phrase(using, IDX_USING).lower()
                )

            ops = index.dialect_options["postgresql"]["ops"]
            text += "(%s)" % (
                ", ".join(
                    [
                        self.sql_compiler.process(
                            (
                                expr.self_group()
                                if not isinstance(expr, expression.ColumnClause)
                                else expr
                            ),
                            include_table=False,
                            literal_binds=True,
                        )
                        + (
                            (" " + ops[expr.key])
                            if hasattr(expr, "key") and expr.key in ops
                            else ""
                        )
                        for expr in index.expressions
                    ]
                )
            )

            includeclause = index.dialect_options["postgresql"]["include"]
            if includeclause:
                inclusions = [
                    index.table.c[col] if isinstance(col, str) else col
                    for col in includeclause
                ]
                text += " INCLUDE (%s)" % ", ".join(
                    [preparer.quote(c.name) for c in inclusions]
                )

            nulls_not_distinct = index.dialect_options["postgresql"][
                "nulls_not_distinct"
            ]
            if nulls_not_distinct is True:
                text += " NULLS NOT DISTINCT"
            elif nulls_not_distinct is False:
                text += " NULLS DISTINCT"

            withclause = index.dialect_options["postgresql"]["with"]
            if withclause:
                text += " WITH (%s)" % (
                    ", ".join(
                        [
                            "%s = %s" % storage_parameter
                            for storage_parameter in withclause.items()
                        ]
                    )
                )

            tablespace_name = index.dialect_options["postgresql"]["tablespace"]
            if tablespace_name:
                text += " TABLESPACE %s" % preparer.quote(tablespace_name)

            whereclause = index.dialect_options["postgresql"]["where"]
            if whereclause is not None:
                whereclause = coercions.expect(
                    roles.DDLExpressionRole, whereclause
                )

                where_compiled = self.sql_compiler.process(
                    whereclause, include_table=False, literal_binds=True
                )
                text += " WHERE " + where_compiled

            return text

class AuroraDSQLDialect(PGDialect):
    
    name = "aurora_dsql"
    default_schema_name = "public"

    ddl_compiler = AuroraDSQLDDLCompiler
    
    supports_sequences = False
    supports_alter = False #  supports ALTER TABLE - used only for generating foreign key constraints in certain circumstances
    supports_native_enum = False


    _supports_create_index_async = True


    @lru_cache()
    def _columns_query(self, schema, has_filter_names, scope, kind):
        # NOTE: the query with the default and identity options scalarx
        # subquery is faster than trying to use outer joins for them
        generated = (
            pg_catalog.pg_attribute.c.attgenerated.label("generated")
            if self.server_version_info >= (12,)
            else sql.null().label("generated")
        )

        # the following uses json_build_object which is not supported by DSQL 
        '''if self.server_version_info >= (10,):
            # join lateral performs worse (~2x slower) than a scalar_subquery
            identity = (
                select(
                    sql.func.json_build_object(
                        "always",
                        pg_catalog.pg_attribute.c.attidentity == "a",
                        "start",
                        pg_catalog.pg_sequence.c.seqstart,
                        "increment",
                        pg_catalog.pg_sequence.c.seqincrement,
                        "minvalue",
                        pg_catalog.pg_sequence.c.seqmin,
                        "maxvalue",
                        pg_catalog.pg_sequence.c.seqmax,
                        "cache",
                        pg_catalog.pg_sequence.c.seqcache,
                        "cycle",
                        pg_catalog.pg_sequence.c.seqcycle,
                    )
                )
                .select_from(pg_catalog.pg_sequence)
                .where(
                    # attidentity != '' is required or it will reflect also
                    # serial columns as identity.
                    pg_catalog.pg_attribute.c.attidentity != "",
                    pg_catalog.pg_sequence.c.seqrelid
                    == sql.cast(
                        sql.cast(
                            pg_catalog.pg_get_serial_sequence(
                                sql.cast(
                                    sql.cast(
                                        pg_catalog.pg_attribute.c.attrelid,
                                        REGCLASS,
                                    ),
                                    TEXT,
                                ),
                                pg_catalog.pg_attribute.c.attname,
                            ),
                            REGCLASS,
                        ),
                        OID,
                    ),
                )
                .correlate(pg_catalog.pg_attribute)
                .scalar_subquery()
                .label("identity_options")
            )
        else:'''
        identity = sql.null().label("identity_options")

        # join lateral performs the same as scalar_subquery here
        default = (
            select(
                pg_catalog.pg_get_expr(
                    pg_catalog.pg_attrdef.c.adbin,
                    pg_catalog.pg_attrdef.c.adrelid,
                )
            )
            .select_from(pg_catalog.pg_attrdef)
            .where(
                pg_catalog.pg_attrdef.c.adrelid
                == pg_catalog.pg_attribute.c.attrelid,
                pg_catalog.pg_attrdef.c.adnum
                == pg_catalog.pg_attribute.c.attnum,
                pg_catalog.pg_attribute.c.atthasdef,
            )
            .correlate(pg_catalog.pg_attribute)
            .scalar_subquery()
            .label("default")
        )
        relkinds = self._kind_to_relkinds(kind)
        query = (
            select(
                pg_catalog.pg_attribute.c.attname.label("name"),
                pg_catalog.format_type(
                    pg_catalog.pg_attribute.c.atttypid,
                    pg_catalog.pg_attribute.c.atttypmod,
                ).label("format_type"),
                default,
                pg_catalog.pg_attribute.c.attnotnull.label("not_null"),
                pg_catalog.pg_class.c.relname.label("table_name"),
                pg_catalog.pg_description.c.description.label("comment"),
                generated,
                identity,
            )
            .select_from(pg_catalog.pg_class)
            # NOTE: postgresql support table with no user column, meaning
            # there is no row with pg_attribute.attnum > 0. use a left outer
            # join to avoid filtering these tables.
            .outerjoin(
                pg_catalog.pg_attribute,
                sql.and_(
                    pg_catalog.pg_class.c.oid
                    == pg_catalog.pg_attribute.c.attrelid,
                    pg_catalog.pg_attribute.c.attnum > 0,
                    ~pg_catalog.pg_attribute.c.attisdropped,
                ),
            )
            .outerjoin(
                pg_catalog.pg_description,
                sql.and_(
                    pg_catalog.pg_description.c.objoid
                    == pg_catalog.pg_attribute.c.attrelid,
                    pg_catalog.pg_description.c.objsubid
                    == pg_catalog.pg_attribute.c.attnum,
                ),
            )
            .where(self._pg_class_relkind_condition(relkinds))
            .order_by(
                pg_catalog.pg_class.c.relname, pg_catalog.pg_attribute.c.attnum
            )
        )
        query = self._pg_class_filter_scope_schema(query, schema, scope=scope)
        if has_filter_names:
            query = query.where(
                pg_catalog.pg_class.c.relname.in_(bindparam("filter_names"))
            )
        return query
