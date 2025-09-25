import asyncio

from utils import Database
from faker import Faker
from utils.models import User, Product
import logging
import aiofiles
from aiocsv import AsyncReader
import traceback


class Generator:
    def __init__(self, user_count: int, schema: str, logger: logging.Logger, truncate_table: bool = False) -> None:
        self.user_count = user_count
        self.schema = schema

        self.faker = Faker()
        self.tables = [User, Product]

        self.db_writer: Database | None = None
        self.logger: logging.Logger = logger
        self.truncate_table = truncate_table

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
                logger=self.logger,
                schema=self.schema,
            )

            # run ddl
            await self.run_ddl(self.db_writer)

            if self.truncate_table:
                await self.truncate_tables(self.db_writer)

            # create users
            create_user_task = asyncio.create_task(self.create_users())
            tasks.append(create_user_task)

            # create products
            create_products_task = asyncio.create_task(self.create_products())
            tasks.append(create_products_task)

            await asyncio.gather(*tasks)
        except Exception as e:
            self.logger.error(f"error initializing generator: {e}")
            traceback.print_exc()
            return False
        finally:
            if self.db_writer:
                await self.db_writer.close()

        return True

    async def truncate_tables(self, db_writer: Database):
        await db_writer.truncate_tables(table_names= [table.__name__ for table in self.tables])

    async def create_users(self):
        users = []
        for _ in range(self.user_count):
            u = User.new(faker=self.faker)
            users.append(u)
        await self.db_writer.upsert(data=users, table="USER")

    async def create_products(self):
        async with aiofiles.open("static/products.csv", mode="r") as pfp:
            reader = AsyncReader(pfp)
            # skip header
            await anext(reader)
            products = []
            async for row in reader:
                try:
                    ratings = None if row[5] == "" else float(row[5])
                    no_of_ratings = None if row[6] == "" else int(
                        row[6].replace(",", ""))
                    discount_price = (
                        None
                        if row[7] == ""
                        else float(row[7].replace("₹", "").replace(",", ""))
                    )
                    actual_price = (
                        None
                        if row[8] == ""
                        else float(row[8].replace("₹", "").replace(",", ""))
                    )
                except Exception as e:
                    # original dataset has some issues, so skipping some values
                    self.logger.warning(e)
                    continue

                p = Product.new(
                    name=row[0],
                    main_category=row[1],
                    sub_category=row[2],
                    image=row[3],
                    link=row[4],
                    ratings=ratings,
                    no_of_ratings=no_of_ratings,
                    discount_price=discount_price,
                    actual_price=actual_price,
                )
                products.append(p)

            await self.db_writer.upsert(data=products, table="PRODUCT")

    async def start(self):
        try:
            if await self.initialize():
                await self.run()
            else:
                raise Exception("error initializing generator")
        except Exception as e:
            self.logger.error(f"error starting generator: {e}")
            raise e

    async def run(self):
        while True:
            # do stuff
            break


def run_simulation(user_count: int, truncate_table: bool = False):
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(name="ecom_debezium")

    generator = Generator(user_count=user_count, schema="test",
                          logger=logger, truncate_table=truncate_table)
    try:
        asyncio.run(generator.start())
    except KeyboardInterrupt as e:
        print(f"User exit triggered, stopping: {e}")
    except Exception as e:
        print(e)
