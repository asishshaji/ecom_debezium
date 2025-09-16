from dataclasses import dataclass
import random
from datetime import datetime
from faker import Faker


@dataclass
class User:
    id: str
    username: str
    first_name: str
    last_name: str
    created_at: datetime
    updated_at: datetime
    address: str
    gender: str
    ip_address: str

    @classmethod
    def new(cls, faker: Faker):
        gender: str = random.choice(["M", "F"])
        if gender == "M":
            first_name = faker.first_name_male()
            last_name = faker.last_name_male()
        else:
            first_name = faker.first_name_female()
            last_name = faker.last_name_female()

        return User(
            id=str(faker.uuid4()),
            username=faker.user_name(),
            first_name=first_name,
            last_name=last_name,
            address=faker.address(),
            created_at=datetime.now(),
            updated_at=datetime.now(),
            gender=gender,
            ip_address=faker.ipv4_public(),
        )

    @staticmethod
    def ddl(schema):
        return f"""
            CREATE TABLE IF NOT EXISTS {schema}.USER (
                id SERIAL PRIMARY KEY,
                username VARCHAR(40) NOT NULL,
                first_name VARCHAR(40) NOT NULL,
                last_name VARCHAR(40) NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_DATE,
                updated_at  TIMESTAMPTZ NOT NULL DEFAULT CURRENT_DATE,
                address VARCHAR(50),
                gender VARCHAR(1) NOT NULL CHECK(gender IN ('M', 'F', 'O')),
                ip_address cidr NOT NULL
            )
        """


@dataclass
class Product:
    pass


@dataclass
class Event:
    pass
