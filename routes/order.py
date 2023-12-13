from decouple import config
from config.logging import logging
import json
from kafka import KafkaProducer
from models.Order import Order
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import ValidationError

# TODO: Add a logging message convention of {original log format} - order id {order_id} - {Success\Error} - message - additional info

logger = logging.getLogger("ORDER ENDPOINT")
order = APIRouter()

ORDER_KAFKA_TOPIC = config('ORDER_KAFKA_TOPIC')
KAFKA_BOOTSTRAP_SERVERS = config('KAFKA_BROKER_ENDPOINTS').split(',')

producer = KafkaProducer(
    bootstrap_servers = KAFKA_BOOTSTRAP_SERVERS,
    value_serializer = lambda x: json.dumps(x).encode('utf-8'),
    acks='all'
)

logger.info("order endpoint initiated")

def validate_transaction(order: dict):
    # Send order to transaction validation 
    logger.debug(f"order {order['order_id']} to be sent to topic {ORDER_KAFKA_TOPIC}")
    res = True

    try:
        producer.send(ORDER_KAFKA_TOPIC, value=order)
        logger.info(f"order {order['order_id']} sent to topic {ORDER_KAFKA_TOPIC}")

    except Exception as e:
        logger.error(f"failed to send order {order['order_id']} to Kafka for  transaction validation - Error: {e}")
        res = False
        raise e
    
    finally:
        logger.info(f"send order to validation function ended")
        return res


def validate_order(order: dict) -> bool:
    try:
        logger.info(f"validating order {order['order_id']}")
        return type(Order(**order)) is Order
    except ValidationError as e:
        logger.error(f"order {order['order_id']} invalid")
        return False

@order.post('/confirm_order/')
async def confirm_order(order: Order):
    logger.info('/confirm_order/ started')
    try:
        res = {"status": True, "message": f"Order {order.order_id} received", "order_id": order.order_id}
        status_code = 200

        order_id = order.order_id
        order = order.dict()

        # Validate order
        order_validation_result = validate_order(order)
        if order_validation_result == False:
            raise HTTPException(status_code=400, detail='Invalid order schema')
        logger.info(f"order {order_id} structure validated")
        
        # Send order to transaction validation services
        order['order_date'] = order['order_date'].isoformat()
        if validate_transaction(order):
            logger.info(f"order {order_id} sent to transaction validation")
        else:
            raise Exception(f"Failed to send order {order_id} for transacion validation")

    except Exception as e:
        logger.error(f'Error {e.__class__.__name__}: {str(e)}. order {order_id}')

        res["status"] = False
        res["message"] = f"couldn't confirm order {order_id}"
        res["error"] = f"{e.__class__.__name__}: {str(e)}"
        status_code = 400
    
    finally:
        logger.info(f'order {order_id} confirmation process ended')
        return JSONResponse(content=res, status_code=status_code)