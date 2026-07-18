from confluent_kafka import Consumer


KAFKA_GROUP_ID = "vk-bot-notification"

KAFKA_TOPICS = [
    "taxi_manager.enterprises",
    "taxi_manager.assignment_managers",
]


def start_listener_kafka(kafka_bootstrap_servers: str) -> None:
    consumer = Consumer(
        {
            "bootstrap.servers": kafka_bootstrap_servers,
            "group.id": KAFKA_GROUP_ID,
            "auto.offset.reset": "earliest",
        }
    )

    consumer.subscribe(KAFKA_TOPICS)

    try:
        while True:
            message = consumer.poll(timeout=1.0)

            if message is None:
                continue

            if message.error():
                print(f"Ошибка Kafka: {message.error()}")
                continue

            value = message.value()

            if value is not None:
                print(value.decode("utf-8"))

    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()