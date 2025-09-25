import dataclasses
from typing import Protocol, TypeVar
import asyncpg
from asyncpg import Connection
from logging import Logger
from typing import Any


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
        conn = await asyncpg.create_pool(
            user=user,
            database=database,
            password=password,
            port=port,
            host=host,
        )
        return cls(logger=logger, conn=conn, schema=schema)

    def select(
        self,
        table: str,
        columns: list[str],
        where_clause: dict[str, Any] | None = None,
        order_by: list[str] | None = None,
        limit: list[str] | None = None,
    ):
        """
        select columns.... from schema.table where .... order by .... limit ....
        """
        pass

    async def upsert(
        self, table: str, data: list[dict | T], conflict_keys: list[str] | None = None
    ) -> None:
        norm = self._normalize(data)
        columns = list(norm[0].keys())
        columns_str = ", ".join(columns)

        placeholders = ", ".join(f"${i + 1}" for i in range(len(columns)))
        # TODO add ON CONFLICT, update clause
        query = (
            f"INSERT INTO {self.schema}.{
                table} ({columns_str}) VALUES ({placeholders})"
        )

        values = [tuple(row.get(col) for col in columns) for row in norm]
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

    async def close(self):
        if self.conn:
            await self.conn.close()
