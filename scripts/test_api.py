import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Order(BaseModel):
    item: str
    quantity: int

@app.post('/confirm_order/')
async def confirm_order(order: Order):
    return {"order": order}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)