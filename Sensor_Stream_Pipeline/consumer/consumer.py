"""
Consumes sensor readings from Kafka, stores them in MongoDB and raises an alert
document whenever a metric crosses its configured threshold.

Delivery guarantee: at-least-once from Kafka (offsets are committed only after a
successful write), combined with deterministic document IDs and upserts in
MongoDB. A message processed twice therefore overwrites itself instead of
creating a duplicate, which makes the pipeline effectively exactly-once from the
point of view of the stored data.
"""

import json
import logging
import os
import sys
import time

from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable
from pymongo import MongoClient, ASCENDING, UpdateOne
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "localhost:29092")
TOPIC = os.getenv("KAFKA_TOPIC", "sensor-readings")
GROUP_ID = os.getenv("KAFKA_GROUP_ID", "sensor-consumer-v2")
MONGO_URI = os.getenv(
    "MONGO_URI", "mongodb://sensor:sensorpass@localhost:27017/?authSource=admin"
)
MONGO_DB = os.getenv("MONGO_DB", "sensordata")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "100"))

# Derived from the 99th percentile of each metric in the source dataset, so that
# roughly the top one per cent of readings is treated as an exceedance.

THRESHOLDS_PATH = os.getenv(
    "THRESHOLDS_PATH",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "thresholds.json"),
)

with open(THRESHOLDS_PATH, encoding="utf-8-sig") as _f:
    _config = json.load(_f)
DEVICE_THRESHOLDS = _config["devices"]
DEFAULT_THRESHOLDS = _config["default"]

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logging.getLogger("kafka").setLevel(logging.WARNING)
log = logging.getLogger("consumer")


def reading_id(reading):
    """Deterministic ID: the same reading always maps to the same document."""
    return f"{reading['device']}_{reading['epoch']}"


def connect_mongo(retries=30, delay=2):
    for attempt in range(1, retries + 1):
        try:
            client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
            client.admin.command("ping")
            log.info("Connected to MongoDB")
            return client
        except (ConnectionFailure, ServerSelectionTimeoutError):
            log.warning("MongoDB not reachable (attempt %d/%d), retrying...", attempt, retries)
            time.sleep(delay)
    log.error("MongoDB unreachable after %d attempts", retries)
    sys.exit(1)


def connect_kafka(retries=30, delay=2):
    for attempt in range(1, retries + 1):
        try:
            consumer = KafkaConsumer(
                TOPIC,
                bootstrap_servers=BOOTSTRAP,
                group_id=GROUP_ID,
                value_deserializer=lambda v: json.loads(v.decode("utf-8")),
                auto_offset_reset="earliest",
                enable_auto_commit=False,  # commit only after a successful write
                max_poll_records=BATCH_SIZE,
                api_version=(2, 6, 0)                
            )
            log.info("Connected to Kafka at %s", BOOTSTRAP)
            return consumer
        except NoBrokersAvailable:
            log.warning("Kafka not reachable (attempt %d/%d), retrying...", attempt, retries)
            time.sleep(delay)
    log.error("Kafka unreachable after %d attempts", retries)
    sys.exit(1)


def setup_collections(db):
    db.readings.create_index([("device", ASCENDING), ("epoch", ASCENDING)])
    db.readings.create_index([("timestamp", ASCENDING)])
    db.alerts.create_index([("device", ASCENDING), ("timestamp", ASCENDING)])
    log.info("Indexes ensured on 'readings' and 'alerts'")


def find_breaches(reading):
    """Return one alert per metric exceeding this device's own threshold."""
    device = reading["device"]
    limits = DEVICE_THRESHOLDS.get(device, DEFAULT_THRESHOLDS)
    known = device in DEVICE_THRESHOLDS

    alerts = []
    for metric, limit in limits.items():
        value = reading.get(metric)
        if value is not None and value > limit:
            alerts.append({
                "_id": f"{reading_id(reading)}_{metric}",
                "device": device,
                "timestamp": reading["timestamp"],
                "epoch": reading["epoch"],
                "metric": metric,
                "value": value,
                "threshold": limit,
                "exceedance": round(value - limit, 6),
                "baseline": "device" if known else "default",
            })
    return alerts


def main():
    mongo = connect_mongo()
    db = mongo[MONGO_DB]
    setup_collections(db)

    consumer = connect_kafka()

    stored = 0
    raised = 0

    try:
        while True:
            batches = consumer.poll(timeout_ms=1000)
            if not batches:
                continue

            reading_ops = []
            alert_ops = []

            for records in batches.values():
                for record in records:
                    reading = record.value
                    reading["_id"] = reading_id(reading)
                    reading_ops.append(
                        UpdateOne({"_id": reading["_id"]}, {"$set": reading}, upsert=True)
                    )
                    for alert in find_breaches(reading):
                        alert_ops.append(
                            UpdateOne({"_id": alert["_id"]}, {"$set": alert}, upsert=True)
                        )

            if reading_ops:
                db.readings.bulk_write(reading_ops, ordered=False)
                stored += len(reading_ops)
            if alert_ops:
                db.alerts.bulk_write(alert_ops, ordered=False)
                raised += len(alert_ops)

            # Only now is it safe to advance the offsets.
            consumer.commit()

            if stored % 1000 < BATCH_SIZE:
                log.info("Stored %d readings, raised %d alerts", stored, raised)

    except KeyboardInterrupt:
        log.info("Stopping. Stored %d readings, raised %d alerts.", stored, raised)
    finally:
        consumer.close()
        mongo.close()


if __name__ == "__main__":
    main()