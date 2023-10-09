import json
from decouple import config
from kafka import KafkaConsumer
from kafka import KafkaProducer
from fastapi import FastAPI
from fastapi import HTTPException
from config.monogodb import mongo_client

KAFKA_BOOTSTRAP_SERVERS = config('KAFKA_BROKER_lOCAL_ENDPOINTS').split(',')
ORDER_KAFKA_TOPIC = config('ORDER_KAFKA_TOPIC')
ORDER_CONFIRMATION_KAFKA_TOPIC = config('ORDER_CONFIRMATION_KAFKA_TOPIC')

app = FastAPI()

transactions_collection = mongo_client[config('MONGODB_DB')]['transactions']

consumer = KafkaConsumer(
    ORDER_KAFKA_TOPIC,
    bootstrap_servers = KAFKA_BOOTSTRAP_SERVERS,
    value_deserializer = lambda x: json.loads(x.decode('utf-8'))
)

producer = KafkaProducer(
    bootstrap_servers = KAFKA_BOOTSTRAP_SERVERS,
    value_serializer = lambda x: json.dumps(x).encode('utf-8')
)

print("Transaction start listening..")

while True:
    for message in consumer:
        print("Ongoing Transaction..")
        consumed_message = message.value

        data = {
            "customer_id":    consumed_message['user_id'],
            "customer_email": f"{consumed_message['user_id']}@gmail.com",
            "total_cost":     consumed_message['total_cost']
        }

        print("Successful transaction")
        producer.send(
            ORDER_CONFIRMATION_KAFKA_TOPIC,
            value=data
        )


async def save_order_to_db(order: Order):
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

async def validate_transaction(order: Order):
    transaction_response = {"message": "Transaction successful.", 'validated': True, 'order_total_cost': 0.0}

    try:
        # Check Items DB to validate if there's enuogh of the Item left in order to fulfill the order.
        db = mongo_client['transactions']['items']

        db_items     = []
        out_of_stock = []

        for item in order.items:
            # Query the database for the item
            db_item = db.find_one({"item_id": item.item_id})
            
            # Item not found or quantity ordered exceeds quantity in stock
            if not db_item or db_item.get("num_in_stock", 0) < item.quantity:
                out_of_stock.append(item.item_id)

                if 'db_items' in locals() or 'db_items' in globals():
                    del(db_items)
            else:
                if 'db_items' in locals() or 'db_items' in globals():
                    db_items.append((db_item, item.quantity))

        # If all items are available
        if len(out_of_stock) == 0 and len(db_items) > 0:
            for db_item in db_items:
                # Update quantity in stock
                new_quantity = db_item[0]["num_in_stock"] - db_item[1]
                db.update_one({"_id": db_item[0]['_id']}, {"$set": {"num_in_stock": new_quantity}})

                # Update order total cost
                transaction_response['order_total_cost'] += db_item[0]['price']

            # Apply discount if valid
            transaction_response['order_total_cost'] *= order.discount

            #TODO: Add Kafka Producer to send event so it updates the order record in the background in the background.

        else:
            transaction_response['validated'] = False
            transaction_response['message'] = f"Transaction failed. The following items were out of stock: {out_of_stock}"

    except Exception as e:
        print(f'Error validating transaction: {e}')

    finally:
        print('Order transaction validation process ended')
        return transaction_response