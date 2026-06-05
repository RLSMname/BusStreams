import time
from quixstreams import Application
from bus import BUSES
from constants import BROKER_ADDRESS, TOPIC_NAME, PUBLISH_EVERY, TICK_INTERVAL


def run_simulation():
    app = Application(broker_address=BROKER_ADDRESS)
    topic = app.topic(TOPIC_NAME, value_serializer="json")

    tick = 0
    print(f"Starting Cluj bus simulation on Topic '{TOPIC_NAME}'")

    with app.get_producer() as producer:
        try:
            while True:
                tick += 1

                for bus in BUSES:
                    bus.move()

                    if tick % PUBLISH_EVERY == 0:
                        msg = bus.to_message().to_dict()
                        msg_serialized = topic.serialize(key=msg["route"], value=msg)
                        producer.produce(
                            topic=topic.name,
                            key=msg_serialized.key,
                            value=msg_serialized.value,
                        )
                        print(
                            f"[Tick {tick}] BUS={msg['code']} ROUTE={msg['route']} FROM='{msg['current_stop']}' TO='{msg['next_stop']}' DIST_LEFT={msg['distance_left']} OCCUPANCY={msg['passenger_count']}/{msg['capacity']}"
                        )

                time.sleep(TICK_INTERVAL)
        except KeyboardInterrupt:
            print("\nShutting down — flushing producer...")


if __name__ == "__main__":
    run_simulation()
