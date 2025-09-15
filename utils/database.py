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

    def create_tables(self, ddls):
        pass

    async def close(self):
        if self.conn:
            await self.conn.close()
