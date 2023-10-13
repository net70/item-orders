from decouple import config
from config.logging import logging
from config.SessionManager import session_manager, COUPON_CODES
from routes.order import order
from routes.item_selection import item_selection
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

logger = logging.getLogger("APP")
app = FastAPI()
app.mount("/templates", StaticFiles(directory="templates"))
logger.info("FastAPI started")

@app.on_event("startup")
async def startup_event():
    await session_manager.set_session_data('coupon_codes', COUPON_CODES)
    logger.info('SessionManager Initialized')

@app.on_event("shutdown")
async def shutdown_event():
    await session_manager.cleanup()
    logger.info("SessionManager Closed")

app.include_router(order)
logger.info("order route added to app")

app.include_router(item_selection)
logger.info("item_selection route added to app")