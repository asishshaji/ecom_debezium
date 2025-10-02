from utils import Database
from faker import Faker
from utils.models import EventType, Order, Event, OrderLine, Product
import random
from random import randint


class UserStateHandlers:
    def __init__(
        self,
        db: Database,
        faker: Faker,
        products: list[Product],
        username: str,
        user_id: str,
        ip_address: str,
        user_agent: str,
        event_buffer_limit: int = 5,
    ):
        self.db: Database = db
        self.username = username
        self.user_id = user_id
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.event_buffer_limit = event_buffer_limit
        self.event_buffer = []
        self.faker = faker
        self.products = products

    async def _buffer_event(self, event: Event):
        self.event_buffer.append(event)
        if len(self.event_buffer) >= self.event_buffer_limit:
            await self.db.upsert(table="EVENT", data=self.event_buffer)
            self.event_buffer.clear()

    async def _force_flush(self):
        if not self.event_buffer:
            return
        await self.db.upsert(table="EVENT", data=self.event_buffer)
        self.event_buffer.clear()

    async def on_process_entry(self, context_id: str):
        event = Event.new(
            user_agent=self.user_agent,
            user_name=self.username,
            event_type=EventType.ENTRY,
            context_id=context_id,
            ip_address=self.ip_address,
        )
        await self._buffer_event(event)

    async def on_process_authenticate(self, context_id: str):
        event = Event.new(
            user_agent=self.user_agent,
            user_name=self.username,
            event_type=EventType.LOGIN,
            context_id=context_id,
            ip_address=self.ip_address,
        )
        await self._buffer_event(event)

    async def on_process_browsing(self, context_id: str):
        event = Event.new(
            user_agent=self.user_agent,
            user_name=self.username,
            event_type=EventType.BROWSING,
            context_id=context_id,
            ip_address=self.ip_address,
        )
        event.metadata = {
            "page": random.choice(["home", "search", "product", "cart", "checkout"]),
            "scroll_depth": random.randint(0, 1),
            "duration_ms": random.randint(0, 4000),
        }
        await self._buffer_event(event)

    async def on_process_unauthenticated(self, context_id: str):
        event = Event.new(
            user_agent=self.user_agent,
            user_name=self.username,
            event_type=EventType.LOGOUT,
            context_id=context_id,
            ip_address=self.ip_address,
        )
        await self._buffer_event(event)

    async def on_process_terminal(self, context_id: str):
        # on termination flush the buffer
        event = Event.new(
            user_agent=self.user_agent,
            user_name=self.username,
            event_type=EventType.EXIT,
            context_id=context_id,
            ip_address=self.ip_address,
        )
        await self._buffer_event(event)
        await self._force_flush()

    async def on_process_view_product(self, context_id: str):
        product = random.choice(self.products)
        event = Event.new(
            user_agent=self.user_agent,
            user_name=self.username,
            event_type=EventType.VIEW_PRODUCT,
            context_id=context_id,
            ip_address=self.ip_address,
        )
        event.metadata = {
            "product_id": str(product["id"]),
            "main_category": product["main_category"],
            "sub_category": product["sub_category"],
            "referrer": random.choice(["home", "search", "recommendation"]),
            "duration_ms": random.randint(1000, 30000),
        }
        await self._buffer_event(event)

    async def on_process_add_to_cart(self, context_id: str):
        event = Event.new(
            user_name=self.username,
            user_agent=self.user_agent,
            event_type=EventType.ADD_TO_CART,
            context_id=context_id,
            ip_address=self.ip_address,
        )
        await self._buffer_event(event)

    async def on_process_remove_from_cart(self, context_id: str):
        event = Event.new(
            user_name=self.username,
            user_agent=self.user_agent,
            event_type=EventType.REMOVE_FROM_CART,
            context_id=context_id,
            ip_address=self.ip_address,
        )
        await self._buffer_event(event)

    async def on_process_place_order(self, context_id):
        event = Event.new(
            user_name=self.username,
            user_agent=self.user_agent,
            event_type=EventType.PLACE_ORDER,
            context_id=context_id,
            ip_address=self.ip_address,
        )
        await self._buffer_event(event)
        # create order
        order = Order.new(u_id=self.user_id)
        await self.db.upsert(table="order", data=[order])

        order_lines = []
        products = random.choices(self.products, k=random.randint(1, 5))

        for prod in products:
            order_lines.append(
                OrderLine.new(
                    order_id=order.id,
                    product_id=prod["id"],
                    quantity=random.randint(1, 20),
                )
            )
        await self.db.upsert(table="orderline", data=order_lines)
