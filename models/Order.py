from pydantic import BaseModel, Field
from typing import List
from .OrderItem import OrderItem
from datetime import datetime
import uuid

def generate_uuid_string():
    return str(uuid.uuid4())

class Order(BaseModel):
    order_id: str = Field(default_factory=generate_uuid_string)
    order_date: datetime = Field(default_factory=datetime.now)
    user_id: str | None = None
    first_name: str
    last_name: str
    email: str
    items: List[OrderItem]
    total_cost: float
    discount: float | None = None
    confirmed: bool = False