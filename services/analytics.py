import json
from decouple import config
from kafka import KafkaConsumer

BOOTSTRAP_SERVERS = config('KAFKA_BROKER_ENDPOINTS').split(',')
ORDER_CONFIRMATION_KAFKA_TOPIC = config('ORDER_CONFIRMATION_KAFKA_TOPIC')

consumer = KafkaConsumer(
    ORDER_CONFIRMATION_KAFKA_TOPIC,
    bootstrap_server = BOOTSTRAP_SERVERS,
    value_deserializer = lambda x: json.loads(x.decode('utf-8'))
)

total_orders_count = 0
total_revenue = 0

print("Analytics Listening..")

while True:
    for message in consumer:
        print("Updating analytics...")
        consumed_message = message.value

        total_cost = float(consumed_message['total_cost'])

        total_orders_count += 1
        total_revenue += total_cost

        print(f"Total orders: {total_orders_count}")
        print(f"Total revenue: {total_revenue}")