import asyncio

from utils import Database
from faker import Faker
from utils.models import User, Product, Event
import logging
import aiofiles
from aiocsv import AsyncReader
import traceback
from asyncpg import Record
from utils.models import EventType
import random
from utils.utils import timeit


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
        user_buffer = []
        user_buffer_limit = 50
        async with semaphore:
            try:
                u = await self.db_writer.select(
                    table="USER", limit=1, order_by=["RANDOM()"]
                )
                username = u[0]["username"]

                # simulate user viewing products
                products: list[Record] = await self.db_writer.select(
                    table="PRODUCT", limit=10, order_by=["RANDOM()"]
                )

                # each user is expected to perform actions
                for _ in range(100):
                    event_type: EventType = random.choice(list(EventType))
                    self.logger.info(f"{username} doing {event_type}")
                    event = Event.new(
                        faker=self.faker,
                        user_name=username,
                        event_type=event_type,
                    )

                    product = random.choice(products)
                    if event_type == EventType.PURCHASE:
                        # TODO create order
                        # update event with product information
                        qty = random.randint(1, 10)

                        event.metadata = {
                            "product_id": str(product["id"]),
                            "quantity": qty,
                            "actual_price": product["actual_price"],
                            "discount_price": product["discount_price"],
                            "currency": random.choice(["INR", "USD", "EUR"]),
                            "payment_method": random.choice(
                                ["CARD", "UPI", "COD", "WALLET"]
                            ),
                        }
                    elif event_type == EventType.SCROLL:
                        event.metadata = {
                            "page": random.choice(
                                ["home", "search", "product", "cart", "checkout"]
                            ),
                            "scroll_depth": random.randint(0, 1),
                            "duration_ms": random.randint(0, 4000),
                        }
                    elif event_type == EventType.CLICK:
                        event.metadata = {
                            "element_type": random.choice(
                                ["button", "link", "image", "add_to_cart", "checkout"]
                            ),
                            "element_id": f"el-{random.randint(1000, 9999)}",
                            "page": random.choice(
                                ["home", "product", "cart", "search"]
                            ),
                            "target_url": self.faker.uri_path(),
                        }
                    elif event_type == EventType.VIEW_PRODUCT:
                        event.metadata = {
                            "product_id": str(product["id"]),
                            "main_category": product["main_category"],
                            "sub_category": product["sub_category"],
                            "referrer": random.choice(
                                ["home", "search", "recommendation"]
                            ),
                            "duration_ms": random.randint(1000, 30000),
                        }
                    elif event_type == EventType.CANCEL:
                        event.metadata = {
                            # "order_id": str(faker.uuid4()),
                            "reason": random.choice(
                                [
                                    "changed_mind",
                                    "found_cheaper",
                                    "delivery_delay",
                                    "other",
                                ]
                            ),
                            # "time_since_purchase_min": random.randint(1, 1440),
                        }

                    if len(user_buffer) < user_buffer_limit:
                        user_buffer.append(event)
                    else:
                        await self.db_writer.upsert(table="EVENT", data=user_buffer)
                        user_buffer.clear()

                    # simulate delay between events
                    await asyncio.sleep(random.uniform(0, 1))

                # if buffer is not empty, force flush
                if len(user_buffer) != 0:
                    await self.db_writer.upsert(table="EVENT", data=user_buffer)

            except asyncio.CancelledError:
                self.logger.info(f"cancelling routine of {username}")
                await self.db_writer.upsert(table="EVENT", data=user_buffer)
                raise
            finally:
                self.logger.info(f"{username} done!!!")

    async def run(self):
        # simulate x concurrent users
        semaphore = asyncio.Semaphore(5)
        try:
            while True:
                # create x users, but is limited by x limit in semaphore
                user_flow_tasks = [self.user_routine(semaphore) for _ in range(10)]
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
