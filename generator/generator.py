import asyncio

from utils import Database
from faker import Faker
from utils.models import User, Product, Event
import logging
import aiofiles
from aiocsv import AsyncReader
import traceback
from asyncpg import Record
from user_workflow_state_machine.workflow_sm import UserWorkflowStateMachine
from user_workflow_state_machine.state_handlers import UserStateHandlers
import uuid


class Generator:
    def __init__(
        self,
        user_count: int,
        schema: str,
        logger: logging.Logger,
        truncate_table: bool = False,
        rebuild_database: bool = False,
    ) -> None:
        self.user_count = user_count
        self.schema = schema

        self.faker = Faker()
        self.tables = [User, Product, Event]

        self.db_writer: Database | None = None
        self.logger: logging.Logger = logger
        self.truncate_table = truncate_table
        self.rebuild_database = rebuild_database

    async def run_ddl(self, db_writer: Database, rebuild_database: bool = False):
        if rebuild_database:
            await db_writer.drop_schema()

        # create schema first
        schema_str = f"CREATE SCHEMA IF NOT EXISTS {self.schema}"

        ddls = [table.ddl("test") for table in self.tables]
        await db_writer.create_tables(schema_str=schema_str, ddls=ddls)

    async def initialize(self, skip_init: bool = False):
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

            if skip_init:
                self.logger.warning("skipping creating database")
                return True

            # run ddl
            await self.run_ddl(self.db_writer, self.rebuild_database)

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
        return True

    async def truncate_tables(self, db_writer: Database):
        await db_writer.truncate_tables(
            table_names=[table.__name__ for table in self.tables]
        )

    async def create_users(self):
        users = []
        for _ in range(self.user_count):
            u = User.new(faker=self.faker)
            users.append(u)

        await self.db_writer.upsert(
            data=users, table="USER", conflict_keys=["username"]
        )

    async def create_products(self):
        async with aiofiles.open("static/products.csv", mode="r") as pfp:
            reader = AsyncReader(pfp)
            # skip header
            await anext(reader)
            products = []
            async for row in reader:
                try:
                    ratings = None if row[5] == "" else float(row[5])
                    no_of_ratings = (
                        None if row[6] == "" else int(row[6].replace(",", ""))
                    )
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

            await self.db_writer.upsert(
                data=products, table="PRODUCT", conflict_keys=["name"]
            )

    async def start(self, skip_init: bool = False):
        try:
            if await self.initialize(skip_init):
                await self.run()
            else:
                raise Exception("error initializing generator")
        except Exception as e:
            self.logger.error(f"error starting generator: {e}")
            raise e

    async def user_routine(self, semaphore: asyncio.Semaphore):
        async with semaphore:
            try:
                u = await self.db_writer.select(
                    columns=["username", "ip_address", "user_agent"],
                    table="USER",
                    limit=1,
                    order_by=["RANDOM()"],
                )
                username = u[0]["username"]
                user_ip = u[0]["ip_address"]
                user_agent = u[0]["user_agent"]

                # simulate user viewing products
                products: list[Record] = await self.db_writer.select(
                    table="PRODUCT", limit=10, order_by=["RANDOM()"]
                )

                usm = UserStateHandlers(
                    db=self.db_writer,
                    faker=self.faker,
                    products=products,
                    username=username,
                    ip_address=user_ip,
                    user_agent=user_agent,
                )
                user_workflow_sm = UserWorkflowStateMachine(handlers=usm)
                # each user is expected to perform actions
                for i in range(10):
                    # kick start state machine
                    await user_workflow_sm.handle()
                    self.logger.info(
                        f"completed iteration : {i + 1} sleeping user : {username}"
                    )

            except asyncio.CancelledError:
                self.logger.info(f"cancelling routine of {username}")
                raise
            finally:
                self.logger.info(f"{username} done!!!")

    async def run(self):
        # simulate x concurrent users
        semaphore = asyncio.Semaphore(50)
        try:
            while True:
                # create x users, but is limited by x limit in semaphore
                user_flow_tasks = [self.user_routine(semaphore) for _ in range(100)]
                await asyncio.gather(*user_flow_tasks)
                break

        except asyncio.CancelledError:
            self.logger.info("Runner cancelled, flushing buffer before exit...")
            raise
        finally:
            if self.db_writer:
                await self.db_writer.close()


def run_simulation(
    user_count: int,
    truncate_table: bool = False,
    rebuild_database: bool = False,
    skip_init: bool = False,
):
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(name="ecom_debezium")

    generator = Generator(
        user_count=user_count,
        schema="test",
        logger=logger,
        truncate_table=truncate_table,
        rebuild_database=rebuild_database,
    )
    try:
        asyncio.run(generator.start(skip_init))
    except KeyboardInterrupt as e:
        print(f"User exit triggered, stopping: {e}")
    except Exception as e:
        print(e)
