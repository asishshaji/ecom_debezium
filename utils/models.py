from dataclasses import dataclass
import random
from datetime import datetime
from faker import Faker
import uuid


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
            id=faker.uuid4(),
            username=faker.user_name(),
            first_name=first_name,
            last_name=last_name,
            address=faker.address(),
            created_at=datetime.now(),
            updated_at=datetime.now(),
            gender=gender,
            ip_address=faker.ipv4_public(),
        )

    @classmethod
    def ddl(cls, schema):
        return f"""
            CREATE TABLE IF NOT EXISTS {schema}.{cls.__name__} (
                id UUID PRIMARY KEY,
                username VARCHAR(40) NOT NULL,
                first_name VARCHAR(40) NOT NULL,
                last_name VARCHAR(40) NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_DATE,
                updated_at  TIMESTAMPTZ NOT NULL DEFAULT CURRENT_DATE,
                address VARCHAR(100),
                gender VARCHAR(1) NOT NULL CHECK(gender IN ('M', 'F', 'O')),
                ip_address cidr NOT NULL
            )
        """


@dataclass
class Product:
    id: str
    name: str
    main_category: str
    sub_category: str
    image: str
    link: str
    ratings: float
    no_of_ratings: int
    discount_price: float
    actual_price: float

    @classmethod
    def new(
        cls,
        name: str,
        main_category: str,
        sub_category: str,
        image: str,
        link: str,
        ratings: float,
        no_of_ratings: int,
        discount_price: float,
        actual_price: float,
    ):
        return Product(
            id=str(uuid.uuid4()),
            name=name,
            main_category=main_category,
            sub_category=sub_category,
            image=image,
            link=link,
            ratings=ratings,
            no_of_ratings=no_of_ratings,
            discount_price=discount_price,
            actual_price=actual_price,
        )

    @classmethod
    def ddl(cls, schema):
        return f"""
            CREATE TABLE IF NOT EXISTS {schema}.{cls.__name__} (
            id UUID PRIMARY KEY,
            name TEXT NOT NULL,
            main_category VARCHAR(50) NOT NULL,
            sub_category VARCHAR(50) NOT NULL,
            image TEXT,
            link TEXT NOT NULL,
            ratings REAL,
            no_of_ratings NUMERIC,
            discount_price REAL,
            actual_price REAL
            )
        """


@dataclass
class Event:
    pass
