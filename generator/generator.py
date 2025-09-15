from typing_extensions import Optional, List
import time
import asyncio

from utils.db_writer import DBWriter
from utils.models import User
from faker import Faker


class Generator:
    def __init__(self, user_count: int) -> None:
        self.user_count = user_count
        self.users: List[User] = []
        self.faker = Faker()

        self.db_writer = DBWriter()

    async def create_users(self):
        for _ in range(self.user_count):
            u = User.new(faker=self.faker)
            # TODO create user in database

    async def start(self):
        try:
            # create users,
            tasks = []
            create_user_task = asyncio.create_task(self.create_users())
            tasks.append(create_user_task)

            await asyncio.gather(*tasks)
        except Exception as e:
            print("error starting generator")


def run_simulation(user_count: int):
    generator = Generator(user_count=user_count)
    try:
        asyncio.run(generator.start())
    except KeyboardInterrupt as e:
        print("User exit triggered, stopping")
    except Exception as e:
        print(e)
