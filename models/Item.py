from pydantic import BaseModel

class Item(BaseModel):
    item_id: str
    name: str
    description: str
    price: float
    num_in_stock: int