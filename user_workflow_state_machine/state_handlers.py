from utils import Database
from utils.models import Product
from faker import Faker
from utils.models import Event
from utils.models import EventType
import random


class UserStateHandlers:
    def __init__(
        self,
        db: Database,
        faker: Faker,
        products: list[Product],
        username: str,
        ip_address: str,
        user_agent:str,
        user_buffer_limit: int = 5,
    ):
        self.db: Database = db
        self.username = username
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.user_buffer_limit = user_buffer_limit
        self.user_buffer = []
        self.faker = faker
        self.products = products

    async def _buffer_event(self, event: Event):
        self.user_buffer.append(event)
        if len(self.user_buffer) >= self.user_buffer_limit:
            await self.db.upsert(table="EVENT", data=self.user_buffer)
            self.user_buffer.clear()

    async def _force_flush(self):
        if not self.user_buffer:
            return
        await self.db.upsert(table="EVENT", data=self.user_buffer)
        self.user_buffer.clear()

    async def on_process_entry(self, context_id: str):
        event = Event.new(
            user_agent = self.user_agent,
            user_name=self.username,
            event_type=EventType.ENTRY,
            context_id=context_id,
            ip_address=self.ip_address,
        )
        await self._buffer_event(event)

    async def on_process_authenticate(self, context_id: str):
        event = Event.new(
            user_agent = self.user_agent,
            user_name=self.username,
            event_type=EventType.LOGIN,
            context_id=context_id,
            ip_address=self.ip_address,
        )
        await self._buffer_event(event)

    async def on_process_browsing(self, context_id: str):
        event = Event.new(
            user_agent = self.user_agent,
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
            user_agent = self.user_agent,
            user_name=self.username,
            event_type=EventType.LOGOUT,
            context_id=context_id,
            ip_address=self.ip_address,
        )
        await self._buffer_event(event)

    async def on_process_terminal(self, context_id: str):
        # on termination flush the buffer
        event = Event.new(
            user_agent = self.user_agent,
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
            user_agent = self.user_agent,
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
            user_agent = self.user_agent,
            event_type=EventType.ADD_TO_CART,
            context_id=context_id,
            ip_address=self.ip_address,
        )
        await self._buffer_event(event)

    async def on_process_remove_from_cart(self, context_id: str):
        event = Event.new(
            user_name=self.username,
            user_agent = self.user_agent,
            event_type=EventType.REMOVE_FROM_CART,
            context_id=context_id,
            ip_address=self.ip_address,
        )
        await self._buffer_event(event)
