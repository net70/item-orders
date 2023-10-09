from pydantic import BaseModel

class OrderItem(BaseModel):
    item_id: str
    quantity: int