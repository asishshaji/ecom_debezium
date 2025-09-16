from typing_extensions import Optional, List
import time
import asyncio

from utils import Database
from utils.models import Product, User, Event
from faker import Faker


class Generator:
    def __init__(self, user_count: int, schema: str) -> None:
        self.user_count = user_count
        self.schema = schema

        self.users: List[User] = []
        self.ip_addresses: List[str] = []

        self.faker = Faker()
        self.tables = [User]

        self.db_writer: Optional[Database] = None

    async def run_ddl(self, db_writer: Database):
        # create schema first
        schema_str = f"CREATE SCHEMA IF NOT EXISTS {self.schema}"

        ddls = [table.ddl("test") for table in self.tables]
        await db_writer.create_tables(schema_str=schema_str, ddls=ddls)

    async def initialize(self):
        tasks = []
        try:
            # create database writer
            self.db_writer = await Database.create(
                user="postgres",
                database="test_database",
                password="test_password",
                port=5432,
                host="localhost",
            )

            # run ddl
            await self.run_ddl(self.db_writer)

            # create users
            create_user_task = asyncio.create_task(self.create_users())
            tasks.append(create_user_task)

            # create products
            # create fulfillment centers

            await asyncio.gather(*tasks)
        except Exception as e:
            print(f"error initializing generator: {e}")
            return False
        finally:
            if self.db_writer:
                await self.db_writer.close()

        return True

    async def create_users(self):
        for _ in range(self.user_count):
            u = User.new(faker=self.faker)
            self.users.append(u)
            self.ip_addresses.append(u.ip_address)

    async def start(self):
        try:
            if await self.initialize():
                await self.run()
            else:
                raise Exception("error initializing generator")
        except Exception as e:
            print(f"error starting generator: {e}")
            raise e

    async def run(self):
        while True:
            # do stuff
            break


def run_simulation(user_count: int):
    generator = Generator(user_count=user_count, schema="test")
    try:
        asyncio.run(generator.start())
    except KeyboardInterrupt as e:
        print("User exit triggered, stopping")
    except Exception as e:
        print(e)
