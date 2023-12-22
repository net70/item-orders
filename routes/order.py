from decouple import config
from config.logging import logging
import json
from kafka import KafkaProducer
from models.Order import Order
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from config.monogodb import mongo_client, UpdateOne

# TODO: Add a logging message convention of {original log format} - order id {order_id} - {Success\Error} - message - additional info

logger = logging.getLogger("ORDER ENDPOINT")
order = APIRouter()

#ORDER_KAFKA_TOPIC = config('ORDER_KAFKA_TOPIC')
KAFKA_BOOTSTRAP_SERVERS = config('KAFKA_BROKER_ENDPOINTS').split(',')
topics = [
    config('ORDER_KAFKA_TOPIC'),
    config('ORDER_CONFIRMATION_KAFKA_TOPIC'),
]

producer = KafkaProducer(
    bootstrap_servers = KAFKA_BOOTSTRAP_SERVERS,
    value_serializer = lambda x: json.dumps(x).encode('utf-8'),
    acks='all'
)

db = mongo_client[config('MONGODB_DB')]
orders_db = db['orders']
items_db  = db['items']

logger.info("order endpoint initiated")

async def create_transaction_response(
        transactions_details ="Transaction Failed",
        confirmed = False,
        total_cost = 0.0,
        discount = 0.0,
        amount_paid = 0.0
) -> dict:

    return {
        "transactions_details": transactions_details, 
        'confirmed':   confirmed,
        'total_cost':  total_cost,
        'discount':    discount,
        'amount_paid': amount_paid
    }


async def save_order_to_db(order: dict):
    res = {'status': False, 'message': 'Processing'}

    try:
        inserted_order = orders_db.insert_one(order)

        res['status'] = True
        res['message'] = f'Order successfully saved to DB with id {inserted_order.inserted_id}'
    
    except Exception as e:
        res['message'] = str(e)
    
    finally:
        return res

async def calc_order_costs(order, cart_items):
    try:
        order_id    = order['order_id']
        coupon_code = order['coupon_code']
        discount    = order['discount']
        amount_paid = 0.0

        # Fetch prices from the database for the given item_ids
        item_data = list(items_db.find({"item_id": {"$in": list(cart_items.keys())}}, {"item_id": 1, "price": 1}))

        # Calculate total cost using list comprehension and sum
        total_price = sum(item_info['price'] * cart_items.get(item_info['item_id'], 0) for item_info in item_data)
        
        # The discount\coupon code should be validated via items\selection endpoint
        if coupon_code:
            amount_paid = total_price * (1 - discount)
        
        return amount_paid, total_price, discount

    except Exception as e:
        logger.error(f'Error with order {order_id} - {e.__class__.__name__}: {e}')
        raise e


async def process_transaction(order):
    try:
        with mongo_client.start_session() as session:
            with session.start_transaction():
                try:
                    # Convert list of items to dict of items
                    cart_items = {item['item_id']: item['quantity'] for item in order['cart']}
                    
                    update_operations = []
                    
                    for item_id in cart_items.keys():
                        update_operations.append(UpdateOne(
                            {
                                "item_id": item_id,
                                "num_in_stock": {"$gte": cart_items[item_id]}
                            },
                            {
                                "$inc": {"num_in_stock": -1 * cart_items[item_id]}
                            },
                            upsert = False
                        ))
                        
                    result = items_db.bulk_write(update_operations, ordered=False, session=session, bypass_document_validation=True)

                    # Check if any item's quantity becomes less than 0
                    if result.modified_count != len(cart_items):
                        raise ValueError(f"Error Order {order['order_id']}: Some items were not found in the database")

                    # Calc order costs
                    order['amount_paid'], order['total_cost'], order['discount'] = await calc_order_costs(order, cart_items)

                    # Create response dict
                    transaction_response = await create_transaction_response(
                        "Transaction Successful",
                        True,
                        order['total_cost'],
                        order['discount'],
                        order['amount_paid']
                    )                  

                    session.commit_transaction()

                    return transaction_response
                    
                except Exception as e:
                    if isinstance(e, ValueError):
                        logger.error(f'Order {order["order_id"]}: Some items not in DB or out of stock. Transaction validation failed.') 
                    
                    session.abort_transaction() 
                    raise e

    except Exception as e:
        raise e

async def validate_transaction(order: dict):
    transaction_response = await create_transaction_response()
    
    # Check Items DB to validate if there's enuogh of the Item left in order to fulfill the order.
    try:
        # Process the order object and perform transaction
        transaction_response = await process_transaction(order)
        return transaction_response

    except Exception as e:
        if isinstance(e, ValueError):
            transaction_response['transactions_details'] = f'Order {order["order_id"]}: Some items not in DB or out of stock. Transaction validation failed. Account not charged.'

        else:    
            logger.error(f'Order {order["order_id"]} - Error validating transaction: {e}')
            transaction_response['transactions_details'] = f'{e.__class__.__name__}: {e}'

        raise e
    
    finally:
        logger.info(f'Order {order["order_id"]} transaction validation process ended')
        return transaction_response


async def update_validated_order_details(order_id: str, transaction_response: dict):
    res = {'status': False, 'message': 'Processing'}

    try:
        updated_order = orders_db.update_one(
            {"order_id": order_id},
            {
                "$set": { key: val for key, val in transaction_response.items()}
            },
            upsert = False
        )

        res['status'] = True
        res['message'] = f'Order successfully saved to DB with id {order_id}'

    except Exception as e:
        res['message'] = str(e)
    
    finally:
        return res


async def validate_order(order: dict) -> bool:
    try:
        transaction_response = await create_transaction_response()
        
        # Save order incoming order to DB
        res = await save_order_to_db(order)

        # Try to validate the transaction if the order was successfully saved to DB
        if res['status']:
            transaction_response = await validate_transaction(order)


            # Update order in DB based on transaction validation result 
            res = await update_validated_order_details(order['order_id'], transaction_response)
            if not res['status']: raise Exception("Could not update succseful order")

        else:
            raise Exception(f"Error saving order to DB - {res['message']}")

    except Exception as e:
        logger.error(f'Error processing order {order["order_id"]}: {e}')
        transaction_response['transaction_response'] = f'{e}'

    finally:
        # Send the order confirmation status forward in the order pipelines
        
        for topic in topics:
            order['_id'] = str(order['_id'])
            order.update(transaction_response)

            producer.send(
                topic,
                value=order
            )
        
        logger.info(f'Finished processing order{order["order_id"]}')
        return transaction_response

@order.post('/confirm_order/')
async def confirm_order(order: Order):
    logger.info('/confirm_order/ started')
    try:
        logger.info(f"processing incoming order {order.order_id}")
        # Order validation setup
        res = {"status": True, "message": f"Order {order.order_id} received", "order_id": order.order_id}
        status_code = 200
        order_id = order.order_id
        order = order.dict()
        order['order_date'] = order['order_date'].isoformat()

        # Send order to transaction validation services
        tranasaction_response = await validate_order(order)

        if tranasaction_response['confirmed']:
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