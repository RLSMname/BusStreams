from datetime import timedelta

from quixstreams import Application
from quixstreams.dataframe.windows import Collect

from constants import BROKER_ADDRESS, TOPIC_NAME, TICK_INTERVAL
from helpers import prRed, prGreen, prCyan, TickMonitor


class Runner:
    def __init__(self):
        self.app = Application(
            broker_address=BROKER_ADDRESS,
            consumer_group="all-v2",
            auto_offset_reset="latest",
        )
        self.clock = TickMonitor(TICK_INTERVAL)

        self.traffic_monitor = TrafficMonitorConsumer()
        self.stop_arrivals= StopArrivalsConsumer()
        self.capacity_alerts = CapacityAlertsConsumer()
        self.topic = self.app.topic(TOPIC_NAME, value_deserializer="json")
        self.alerts = self.app.topic("alerts", value_serializer="json")
        self.traffic = self.app.topic("traffic", value_serializer="json")
        self.capacity = self.app.topic("capacity", value_serializer="json")

    def run(self):
        self.clock.start()

        main_sdf = self.app.dataframe(self.topic)
        traffic_sdf = self.traffic_monitor.create_pipeline(main_sdf, self.traffic)
        arrivals_sdf = self.stop_arrivals.create_pipeline(main_sdf, self.alerts)
        capacity_sdf = self.capacity_alerts.create_pipeline(main_sdf, self.capacity)

        self.app.run()


class StopArrivalsConsumer:
    ARRIVAL_THRESHOLD = 60

    def is_arriving(self, msg):
        return int(msg["distance_left"].replace("m", "")) <= self.ARRIVAL_THRESHOLD

    def log(self, msg):
        prGreen(f"[Arrivals]: Bus {msg['code']} on route {msg['route']} arriving at '{msg['next_stop']}' — {msg['distance_left']} away")

    def create_pipeline(self, sdf, topic):
        print(f"Creating pipeline for {type(self)}")
        sdf = sdf.filter(self.is_arriving).update(self.log)
        sdf = sdf.to_topic(topic)

        return sdf

class CapacityAlertsConsumer:
    THRESHOLD = 0.8

    def is_overcrowded(self, msg):
        return msg["passenger_count"] / msg["capacity"] >= self.THRESHOLD

    def log(self, msg):
        pct = msg["passenger_count"] / msg["capacity"] * 100
        prCyan(f"[Capacity]: Bus {msg['code']} on route {msg['route']} is {pct:.0f}% full ({msg['passenger_count']}/{msg['capacity']}) — between {msg['current_stop']} and {msg['next_stop']}")

    def create_pipeline(self, sdf, topic):
        print(f"Creating pipeline for {type(self)}")
        sdf = sdf.filter(self.is_overcrowded).update(self.log)
        sdf = sdf.to_topic(topic)

        return sdf

class TrafficMonitorConsumer:
    MIN_MESSAGES = 3
    MAX_MESSAGES = 8
    WINDOW_SECONDS = MAX_MESSAGES * TICK_INTERVAL

    def is_slow(self, window_value, key, timestamp, headers):
        stops = window_value["stops"]
        if len(stops) < self.MIN_MESSAGES:
            return False
        unique_stops = set(stops)
        return len(unique_stops) <= 1

    def log(self, window_value, key, timestamp, headers):
        stop = window_value["stops"][0]
        prRed(f"[Traffic]: Bus {key} has not reached next stop in the last {self.WINDOW_SECONDS:.0f}s. Last stop: {stop}")

    def create_pipeline(self, sdf, topic):
        print(f"Creating pipeline for {type(self)}")

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

        sdf = sdf.to_topic(topic)

        return sdf

class DummyConsumer:
    def create_pipeline(self, sdf):
        sdf.print(pretty=True, metadata=True)

        return sdf

if __name__ == "__main__":
    runner = Runner()
    runner.run()