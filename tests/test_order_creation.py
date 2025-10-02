import pytest
from utils import Database
import logging
from utils.models import OrderLine, Order


@pytest.mark.asyncio
async def test_create_order():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(name="testing_logger")

    db = await Database.create(
        user="postgres",
        database="test_database",
        password="test_password",
        port=5432,
        host="localhost",
        logger=logger,
        schema="test",
    )

    user = await db.select(table="user", columns=["id"], limit=1, order_by=["RANDOM()"])
    user = user[0]

    # create the order
    order = Order.new(u_id=user["id"])
    await db.upsert(table="order", data=[order])

    product = await db.select(
        table="product", columns=["id"], limit=1, order_by=["RANDOM()"]
    )
    product_id = product[0]["id"]

    order_lines = []
    for i in range(4):
        order_lines.append(
            OrderLine.new(
                order_id=order.id,
                product_id=product_id,
                quantity=12.3,
            )
        )

    await db.upsert(table="orderline", data=order_lines)
