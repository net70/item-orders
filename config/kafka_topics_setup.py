from decouple import config
from kafka import KafkaAdminClient
from kafka.admin import NewTopic

BOOTSTRAP_SERVERS = config('KAFKA_BROKER_ENDPOINTS').split(',')

ORDER_KAFKA_TOPIC = config('ORDER_KAFKA_TOPIC')
ORDER_CONFIRMATION_KAFKA_TOPIC = config('ORDER_CONFIRMATION_KAFKA_TOPIC')
ITEM_SELECT_KAFKA_TOPIC = config('ITEM_SELECT_KAFKA_TOPIC')

def create_app_toics():
    # Create an AdminClient instance
    admin_client = KafkaAdminClient(bootstrap_servers=BOOTSTRAP_SERVERS)

    # Define the topic name you want to check or create
    topics = (
        ORDER_KAFKA_TOPIC,
        ORDER_CONFIRMATION_KAFKA_TOPIC,
        ITEM_SELECT_KAFKA_TOPIC
    )

    # Loop through topics and check if setup is needed
    for topic_name in topics:

        # Check if the topic already exists
        topic_exists = topic_name in admin_client.list_topics()

        if topic_exists:
            print(f"Topic '{topic_name}' already exists.")
        else:
            # Create the topic configuration (you can customize this)
            topic_config = {
                'cleanup.policy': 'delete',
                'retention.ms': '3600000',  # 1 hour  
            }

            # Define the number of partitions and replication factor for the topic
            num_partitions = 3
            replication_factor = 1

            # Create a NewTopic instance
            new_topic = NewTopic(
                name=topic_name,
                num_partitions=num_partitions,
                replication_factor=replication_factor,
                topic_configs=topic_config
            )

            # Create the topic
            admin_client.create_topics([new_topic])
            print(f"Topic '{topic_name}' has been created.")

    # Close the AdminClient
    admin_client.close()

if __name__ == "__main__":
    create_app_toics()