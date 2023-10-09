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

emails_sent = set({})
print("Email server listening..")

while True:
    for message in consumer:
        consumed_message = message.value
        customer_email = consumed_message['customer_email']

        print(f"Sending email to {customer_email}")
        emails_sent.add(customer_email)
        print(f'Total unique emails sent: {len(emails_sent)}')