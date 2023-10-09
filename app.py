from decouple import config
from config.logging import logging
from routes.order import order
from routes.item_selection import item_selection
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

logger = logging.getLogger("APP")

app = FastAPI()
app.mount("/templates", StaticFiles(directory="templates"))

logger.info("FastAPI started")

app.include_router(order)
logger.info("order route added to app")

app.include_router(item_selection)
logger.info("item_selection route added to app")