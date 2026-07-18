import json

from confluent_kafka import Consumer

from notification_context.handlers import handle_assignment_managers, handle_enterprise, handle_vehicle_models
from notifications.services import notify_enterprise_managers
from notifications.handlers import handle_vehicles

KAFKA_GROUP_ID = "vk-bot-notification"

KAFKA_TOPICS = [
    "taxi_manager.enterprises",
    "taxi_manager.assignment_managers",
    "taxi_manager.vehicle_models",
    "taxi_manager.vehicles"
]


def start_listener_kafka(kafka_bootstrap_servers: str, vk_bot_client) -> None:
    consumer = Consumer(
        {
            "bootstrap.servers": kafka_bootstrap_servers,
            "group.id": KAFKA_GROUP_ID,
            "auto.offset.reset": "earliest",
        }
    )

    consumer.subscribe(KAFKA_TOPICS)

    print("listener_kafka работает")

    try:
        while True:
            message = consumer.poll(timeout=1.0)

            if message is None:
                continue

            if message.error():
                print(f"Ошибка Kafka: {message.error()}")
                continue

            value_b = message.value()

            if value_b is None:
                continue

            topic = message.topic()
            value_dict = json.loads(value_b.decode("utf-8"))

            if topic == "taxi_manager.enterprises":
                handle_enterprise(value_dict)
                continue 

            if topic == "taxi_manager.assignment_managers":
                handle_assignment_managers(value_dict)
                continue     

            if topic == "taxi_manager.vehicle_models":
                handle_vehicle_models(value_dict)
                continue  

            if topic == "taxi_manager.vehicles":
                before = value_dict.get("before")
                after = value_dict.get("after")

                enterprise_uuids = {
                    vehicle["enterprise_uuid"]
                    for vehicle in (before, after)
                    if vehicle and vehicle.get("enterprise_uuid")
                }

                notify_text = handle_vehicles(value_dict)

                if not notify_text:
                    continue

                for enterprise_uuid in enterprise_uuids:
                    notify_enterprise_managers(
                        enterprise_uuid,
                        notify_text,
                        vk_bot_client,
                    )

                continue 

            
            print(f"Необработанный топик: {topic}")
            print(value_dict)


    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()