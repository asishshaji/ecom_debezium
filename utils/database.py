import dataclasses
from typing import Protocol, TypeVar
import asyncpg
from asyncpg import Connection
from logging import Logger
from typing import Any
import json


class DataclassProtocol(Protocol):
    __dataclass_fields__: dict


T = TypeVar("T", bound=DataclassProtocol)


class Database:
    def __init__(self, logger: Logger, schema: str, conn: Connection | None = None):
        self.conn: Connection | None = conn
        self.logger: Logger = logger
        self.schema = schema

    @classmethod
    async def create(
        cls,
        user: str,
        database: str,
        password: str,
        port: int,
        host: str,
        schema: str,
        logger: Logger,
    ):
        pool = await asyncpg.create_pool(
            user=user,
            database=database,
            password=password,
            port=port,
            host=host,
        )
        return cls(logger=logger, conn=pool, schema=schema)

    async def select(
        self,
        table: str,
        columns: list[str] | None = None,
        where_clause: dict[str, Any] | None = None,
        order_by: list[str] | None = None,
        limit: int | None = None,
    ):
        """
        select columns.... from schema.table where .... order by .... limit ....
        """
        columns_placeholder = ""
        if not columns:
            columns_placeholder = "*"
        else:
            columns_placeholder = ",".join(columns)

        temp_where_placeholder = ""
        if where_clause:
            temp_where_placeholder = " AND ".join(
                [f"{key} = {value}" for key, value in where_clause.items()]
            )
        where_placeholder = ""
        if temp_where_placeholder:
            where_placeholder = f"WHERE {temp_where_placeholder}"

        order_by_placeholder = ""
        if order_by:
            order_by_placeholder = ", ".join(order_by)
            order_by_placeholder = f"ORDER BY {order_by_placeholder}"

        limit_placeholder = ""
        if limit:
            limit_placeholder = f"LIMIT {limit}"

        query = f"SELECT {columns_placeholder} from {self.schema}.{table} {where_placeholder} {order_by_placeholder} {limit_placeholder}"
        res = await self.conn.fetch(query)
        return res

    async def upsert(
        self,
        table: str,
        data: list[dict | T],
        conflict_keys: list[str] | None = None,
        update_fields: list[str] | None = None,
    ) -> None:
        if conflict_keys == None:
            conflict_keys = []

        norm = self._normalize(data)
        columns = list(norm[0].keys())
        columns_str = ", ".join(columns)

        insert_placeholders = ", ".join(f"${i + 1}" for i in range(len(columns)))

        if not update_fields:
            update_placeholders = ", ".join(
                [
                    f"{col} = EXCLUDED.{col}"
                    for col in columns
                    if col not in conflict_keys
                ]
            )
        else:
            update_placeholders = ", ".join(
                [f"{field} = EXCLUDED.{field}" for field in update_fields]
            )

        conflict_placeholders = ",".join(conflict_keys)

        if conflict_placeholders == "":
            query = f"INSERT INTO {self.schema}.{table} ({columns_str}) VALUES ({insert_placeholders})"
        else:
            query = f"INSERT INTO {self.schema}.{table} ({columns_str}) VALUES ({insert_placeholders}) ON CONFLICT ({conflict_placeholders}) DO UPDATE SET {update_placeholders}"

        # values = [tuple(row.get(col) for col in columns) for row in norm]
        values = []
        for row in norm:
            items = []
            for col in columns:
                item = row.get(col)
                if isinstance(item, dict):
                    item = json.dumps(item)
                items.append(item)
            values.append(tuple(items))

        await self.conn.executemany(query, values)

    async def truncate_tables(self, table_names):
        if not table_names:
            return

        query_input = [f"{self.schema}.{table_name}" for table_name in table_names]
        query = f"TRUNCATE {','.join(query_input)}"

        await self.conn.execute(query)

    def _normalize(self, data: list[dict | T]):
        if len(data) == 0:
            return []
        if dataclasses.is_dataclass(data[0]):
            return [dataclasses.asdict(d) for d in data]
        elif isinstance(data[0], dict):
            return data

    async def create_tables(self, schema_str, ddls):
        if not self.conn:
            raise Exception("no db connection found")
        await self.conn.execute(schema_str)
        for ddl in ddls:
            await self.conn.execute(ddl)

    async def drop_schema(self):
        query = f"DROP SCHEMA IF EXISTS {self.schema} CASCADE"
        await self.conn.execute(query)

    async def close(self):
        if self.conn:
            await self.conn.close()
