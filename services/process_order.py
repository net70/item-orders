
import asyncio
import json
from decouple import config
from kafka import KafkaConsumer
from kafka import KafkaProducer
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
        inserted_order = transactions_db.insert_one(order)

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
        amount_paid = 0.0
        discount = 0.0

        # Fetch prices from the database for the given item_ids
        item_data = list(items_db.find({"item_id": {"$in": list(cart_items.keys())}}, {"item_id": 1, "price": 1}))

        # Calculate total cost using list comprehension and sum
        total_price = sum(item_info['price'] * cart_items.get(item_info['item_id'], 0) for item_info in item_data)
        

        if coupon_code in COUPON_CODES:
            discount = COUPON_CODES[coupon_code]
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
                    order['amount_paid'], order['total_cost'], order['discount'] = calc_order_costs(order, cart_items)

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


async def validate_transaction(order):
    transaction_response = await create_transaction_response()
    
    # Check Items DB to validate if there's enuogh of the Item left in order to fulfill the order.
    try:
        # Process the order object and perform transaction
        transaction_response = process_transaction(order)
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
        updated_order = transactions_db.update_one(
            {"order_id": order_id},
            {
                "$set": { key: val for key, val in transaction_response.items()}
            },
            upsert = False
        )

        res['status'] = True
        res['message'] = f'Order successfully saved to DB with id {updated_order.inserted_id}'
    
    except Exception as e:
        res['message'] = str(e)
    
    finally:
        return res

logger.info("Listening for Orders to process")

async def main():
    while True:
        for message in consumer:
            try:
                logger.info(f"processing incoming order")

                order = message.value
                transaction_response = await create_transaction_response()
                res = await save_order_to_db(order)

                if res['status']:
                    transaction_response = await validate_transaction(order)

                else:
                    transaction_response['transactions_details'] = "Error saving order to DB"
                
                await update_validated_order_details(order['order_id'], transaction_response)
                
                print("Successful transaction")
                producer.send(
                    ORDER_CONFIRMATION_KAFKA_TOPIC,
                    value=order
                )
            
            except Exception as e:
                logger.error(f'Error processing order{order["order_id"]}: {e}')
                transaction_response['transaction_response'] = f'{e}'

                return transaction_response
            
            finally:
                logger.info(f'Finished processing order{order["order_id"]}')
                return transaction_response

if __name__ == '__main__':
    asyncio.run(main())