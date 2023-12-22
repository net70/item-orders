
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
    value_serializer = lambda x: json.dumps(x).encode('utf-8'),
    acks='all'
)
logger.info('Loading Kafka producers and consumers')


logger.info("Listening for Orders to process")

async def main():
    while True:
        for message in consumer:
            try:
                logger.info(f"processing incoming order")

            except Exception as e:
                logger.error(f'Error processing order{order["order_id"]}: {e}')
                transaction_response['transaction_response'] = f'{e}'
            
            finally:
                # Send the order confirmation status forward in the order pipelines
                producer.send(
                    ORDER_CONFIRMATION_KAFKA_TOPIC,
                    value=order.update(transaction_response)
                )
                
                logger.info(f'Finished processing order{order["order_id"]}')

if __name__ == '__main__':
    asyncio.run(main())