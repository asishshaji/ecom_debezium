from typing_extensions import Optional
import asyncpg
from asyncpg import Connection


class Database:
    def __init__(self, conn: Optional[Connection]):
        self.conn: Optional[Connection] = conn

    @classmethod
    async def create(
        cls,
        user: str,
        database: str,
        password: str,
        port: int,
        host: str,
    ):
        conn = await asyncpg.connect(
            user=user,
            database=database,
            password=password,
            port=port,
            host=host,
        )
        return cls(conn)

    def select(self):
        pass

    def upsert(self):
        pass

    async def create_tables(self, schema_str, ddls):
        if not self.conn:
            # log error
            return
        await self.conn.execute(schema_str)
        for ddl in ddls:
            await self.conn.execute(ddl)

    async def close(self):
        if self.conn:
            await self.conn.close()
