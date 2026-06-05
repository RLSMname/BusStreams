import threading
import time
from datetime import timedelta

from quixstreams import Application
from quixstreams.dataframe.windows import Collect

from constants import BROKER_ADDRESS, TOPIC_NAME, TICK_INTERVAL


class StopArrivalsConsumer:
    ARRIVAL_THRESHOLD = 60

    def __init__(self):
        self.app = Application(
            broker_address=BROKER_ADDRESS,
            consumer_group="stop-arrivals",
            auto_offset_reset="latest",
        )

    def is_arriving(self, msg):
        return int(msg["distance_left"].replace("m", "")) <= self.ARRIVAL_THRESHOLD

    def log(self, msg):
        print(f"[Arrivals]: Bus {msg['code']} on route {msg['route']} arriving at '{msg['next_stop']}' — {msg['distance_left']} away")

    def run(self):
        topic = self.app.topic(TOPIC_NAME, value_deserializer="json")
        sdf = self.app.dataframe(topic)
        sdf = sdf.filter(self.is_arriving).update(self.log)
        print("StopArrivalsConsumer starting...")
        self.app.run()

class CapacityAlertsConsumer:
    THRESHOLD = 0.8

    def __init__(self):
        self.app = Application(
            broker_address=BROKER_ADDRESS,
            consumer_group="capacity-alerts",
            auto_offset_reset="latest",
        )

    def is_overcrowded(self, msg):
        return msg["passenger_count"] / msg["capacity"] >= self.THRESHOLD

    def log(self, msg):
        pct = msg["passenger_count"] / msg["capacity"] * 100
        print(f"[Capacity] Bus {msg['code']} on route {msg['route']} is {pct:.0f}% full ({msg['passenger_count']}/{msg['capacity']}) — between {msg['current_stop']} and {msg['next_stop']}")

    def run(self):
        topic = self.app.topic(TOPIC_NAME, value_deserializer="json")
        sdf = self.app.dataframe(topic)
        sdf = sdf.filter(self.is_overcrowded).update(self.log)
        print("CapacityAlertsConsumer starting...")
        self.app.run()

class TrafficMonitorConsumer:
    MIN_MESSAGES = 3
    MAX_MESSAGES = 8
    WINDOW_SECONDS = MAX_MESSAGES * TICK_INTERVAL

    def __init__(self):
        self.app = Application(
            broker_address=BROKER_ADDRESS,
            consumer_group="traffic-monitor",
            auto_offset_reset="latest",
        )

    def is_slow(self, window_value, key, timestamp, headers):
        stops = window_value["stops"]
        if len(stops) < self.MIN_MESSAGES:
            return False
        unique_stops = set(stops)
        return len(unique_stops) <= 1

    def log(self, window_value, key, timestamp, headers):
        stop = window_value["stops"][0]
        print(
            f"[Arrivals]: Bus {key} has not reached next stop in {self.WINDOW_SECONDS:.0f}s. Last stop: {stop}")

    def run(self):
        topic = self.app.topic(TOPIC_NAME, value_deserializer="json")
        sdf = self.app.dataframe(topic)

        sdf = sdf.group_by("code")

        sdf = sdf[["current_stop"]]

        sdf = (
            sdf.tumbling_window(timedelta(seconds=self.WINDOW_SECONDS))
            .agg(stops=Collect(column="current_stop"))
            .final()
        )

        sdf = sdf.filter(self.is_slow, metadata=True)

        sdf = sdf.update(self.log, metadata=True)

        sdf = sdf.apply(lambda val: {
            "stop": val["stops"][0],
            "start": val["start"],
            "end": val["end"],
        })

        sdf.print(pretty=True, metadata=True)

        print("TrafficMonitorConsumer starting...")
        self.app.run()

class DummyConsumer:
    def __init__(self):
        self.app = Application(
            broker_address=BROKER_ADDRESS,
            consumer_group="dummy",
            auto_offset_reset="earliest"
        )

    def run(self):
        topic = self.app.topic(TOPIC_NAME, value_deserializer="json")
        sdf = self.app.dataframe(topic)
        sdf.print(pretty=True, metadata=True)
        print("DummyConsumer starting...")
        self.app.run()

if __name__ == "__main__":
    # dummy_consumer = DummyConsumer()
    # dummy_consumer.run()

    # stops_arrivals_consumer = StopArrivalsConsumer()
    # stops_arrivals_consumer.run()

    # capacity_alerts_consumer = CapacityAlertsConsumer()
    # capacity_alerts_consumer.run()

    # traffic_monitor_consumer = TrafficMonitorConsumer()
    # traffic_monitor_consumer.run()
    pass