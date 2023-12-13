import json
from decouple import config
from kafka import KafkaConsumer
from kafka import KafkaProducer
from fastapi import FastAPI
from fastapi import HTTPException
from config.monogodb import mongo_client, UpdateOne
from config.logging import logging

KAFKA_BOOTSTRAP_SERVERS = config('KAFKA_BROKER_lOCAL_ENDPOINTS').split(',')
ORDER_KAFKA_TOPIC = config('ORDER_KAFKA_TOPIC')
ORDER_CONFIRMATION_KAFKA_TOPIC = config('ORDER_CONFIRMATION_KAFKA_TOPIC')

COUPON_CODES = {
    'entery10': 0.1,
    'nice15': 0.15,
    'super20': 0.2,
    'vip40': 0.4
}

logger = logging.getLogger("ORDER VALIDATION SERVICE")
# app = FastAPI()


transactions_db = mongo_client[config('MONGODB_DB')]['transactions']
items_db        = mongo_client[config('MONGODB_DB')]['items']
logger.info('Loaded relevant databases')


consumer = KafkaConsumer(
    ORDER_KAFKA_TOPIC,
    bootstrap_servers = KAFKA_BOOTSTRAP_SERVERS,
    value_deserializer = lambda x: json.loads(x.decode('utf-8'))
)

producer = KafkaProducer(
    bootstrap_servers = KAFKA_BOOTSTRAP_SERVERS,
    value_serializer = lambda x: json.dumps(x).encode('utf-8')
)
logger.info('Loading Kafka producers and consumers')


async def save_order_to_db(order: dict):
    res = {'status': False, 'message': 'Processing'}

    try:
        db = mongo_client['transactions']['orders']
        inserted_order = db.insert_one(order)

        res['status'] = True
        res['message'] = f'Order successfully saved to DB with id {inserted_order.inserted_id}'
    
    except Exception as e:
        res['message'] = str(e)
    
    finally:
        return res
    
async def calc_order_total_cost(order, cart_items):
    try:
        order_id    = order['order_id']
        coupon_code = order['coupon_code']
        discount = 0.0

        # Fetch prices from the database for the given item_ids
        item_data = list(items_db.find({"item_id": {"$in": list(cart_items.keys())}}, {"item_id": 1, "price": 1}))

        # Calculate total cost using list comprehension and sum
        total_price = sum(item_info['price'] * cart_items.get(item_info['item_id'], 0) for item_info in item_data)
        
        if coupon_code in COUPON_CODES:
            discount = COUPON_CODES[coupon_code]
            total_price *= 1 - discount
        
        return total_price, discount

    except Exception as e:
        raise e

async def update_items_in_db(order):
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

                    # Calc order total cost
                    order['total_cost'], order['discount'] = calc_order_total_cost(order, cart_items)
                    session.commit_transaction()

                    return order
                    
                except Exception as e:
                    if isinstance(e, ValueError):
                        logger.error(f'Order {order["order_id"]}: Some items not in DB or out of stock. Transaction validation failed.') 
                    
                    session.abort_transaction() 
                    raise e

    except Exception as e:
        raise e


async def validate_transaction(order):
    transaction_response = {"message": "Transaction successful.", 'validated': True, 'order_total_cost': 0.0}
    
    # Check Items DB to validate if there's enuogh of the Item left in order to fulfill the order.
    try:
        # Process the order object and perform transaction
        order = update_items_in_db(order)

        # Update response with details for further processing
        transaction_response['order_total_cost'] += order['total_cost']
        transaction_response['discount'] += order['discount']
        
        #TODO: Add Kafka Producer to send event so it updates the order record in the background in the background.

    except Exception as e:
        if isinstance(e, ValueError):
            transaction_response['message'] = f'Order {order["order_id"]}: Some items not in DB or out of stock. Transaction validation failed. Account not charged.'

        else:    
            logger.error(f'Order {order["order_id"]} - Error validating transaction: {e}')
            transaction_response['message'] = f'{e.__class__.__name__}: {e}'
        
        transaction_response['validated'] = False
        transaction_response['order_total_cost'] = 0

        raise e
    
    finally:
        logger.info(f'Order {order["order_id"]} transaction validation process ended')
        return transaction_response
    

logger.info("Listening for Orders to process")

async def main():
    while True:
        for message in consumer:
            try:
                logger.info(f"processing incoming order")

                order = message.value
                await save_order_to_db(order)
                await validate_transaction(order)

                print("Successful transaction")
                producer.send(
                    ORDER_CONFIRMATION_KAFKA_TOPIC,
                    value=order
                )
            
            except Exception as e:
                pass
            finally:
                pass

if __name__ == '__main__':
    main()