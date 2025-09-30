from enum import Enum
from dataclasses import dataclass
import random
from datetime import datetime
from faker import Faker
import uuid
from typing import Any


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
    user_agent: str

    @classmethod
    def new(cls, faker: Faker):
        gender: str = random.choice(["M", "F", "O"])
        if gender == "M":
            first_name = faker.first_name_male()
            last_name = faker.last_name_male()
        else:
            first_name = faker.first_name_female()
            last_name = faker.last_name_female()

        return User(
            id=str(uuid.uuid4()),
            username=faker.user_name(),
            first_name=first_name,
            last_name=last_name,
            address=faker.address(),
            created_at=datetime.now(),
            updated_at=datetime.now(),
            gender=gender,
            ip_address=faker.ipv4(),
            user_agent=faker.user_agent(),
        )

    @classmethod
    def ddl(cls, schema):
        return f"""
            CREATE TABLE IF NOT EXISTS {schema}.{cls.__name__} (
                id UUID PRIMARY KEY,
                username VARCHAR(40) NOT NULL UNIQUE,
                first_name VARCHAR(40) NOT NULL,
                last_name VARCHAR(40) NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_DATE,
                updated_at  TIMESTAMPTZ NOT NULL DEFAULT CURRENT_DATE,
                address VARCHAR(100),
                gender VARCHAR(1) NOT NULL CHECK(gender IN ('M', 'F', 'O')),
                ip_address CIDR NOT NULL,
                user_agent TEXT NOT NULL
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
            name TEXT NOT NULL UNIQUE,
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


class EventType(Enum):
    PURCHASE = "PURCHASE"
    CANCEL = "CANCEL"
    SCROLL = "SCROLL"
    CLICK = "CLICK"
    VIEW_PRODUCT = "VIEW"


@dataclass
class Event:
    id: str
    ip_address: str
    user_name: str | None
    user_agent: str
    event_type: str
    created_at: datetime
    metadata: dict[str, Any]

    @classmethod
    def new(
        cls,
        faker: Faker,
        user_name: str,
        event_type: EventType,
        metadata: dict[str, Any] | None = None,
    ):
        return Event(
            id=str(uuid.uuid4()),
            ip_address=faker.ipv4(),
            user_name=user_name,
            user_agent=faker.user_agent(),
            event_type=event_type.value,
            created_at=datetime.now(),
            metadata=metadata,
        )

    @classmethod
    def ddl(cls, schema):
        return f"""
            CREATE TABLE IF NOT EXISTS {schema}.{cls.__name__} (
                id UUID PRIMARY KEY,
                event_type VARCHAR(20) NOT NULL,
                ip_address CIDR NOT NULL,
                user_name VARCHAR(40),
                created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_DATE,
                user_agent TEXT,
                metadata JSONB
            )
        """
