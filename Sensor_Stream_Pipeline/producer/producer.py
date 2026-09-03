import csv
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone

from kafka import KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import NoBrokersAvailable, TopicAlreadyExistsError

BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "localhost:29092")
TOPIC = os.getenv("KAFKA_TOPIC", "sensor-readings")
PARTITIONS = int(os.getenv("TOPIC_PARTITIONS", "3"))
CSV_PATH = os.getenv(
    "CSV_PATH",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "iot_telemetry_data.csv"),
)
SPEED_FACTOR = float(os.getenv("SPEED_FACTOR", "1000"))
MAX_SLEEP = float(os.getenv("MAX_SLEEP", "2.0"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
log = logging.getLogger("producer")


def to_bool(value):
    """The CSV stores booleans as the strings 'true'/'false'.

    bool('false') is True in Python, so this must be explicit.
    """
    return str(value).strip().lower() == "true"


def parse_row(row):
    """Convert one raw CSV row into a typed reading."""
    epoch = float(row["ts"])  # written in scientific notation, e.g. 1.59451209E9
    return {
        "timestamp": datetime.fromtimestamp(epoch, tz=timezone.utc).isoformat(),
        "epoch": epoch,
        "device": row["device"],
        "co": float(row["co"]),
        "humidity": round(float(row["humidity"]), 2),
        "lpg": float(row["lpg"]),
        "smoke": float(row["smoke"]),
        "temperature": round(float(row["temp"]), 2),  # float32 artefacts in source
        "light": to_bool(row["light"]),
        "motion": to_bool(row["motion"]),
    }


def wait_for_broker(retries=30, delay=2):
    """Kafka may still be starting when this container does. Retry, don't crash."""
    for attempt in range(1, retries + 1):
        try:
            admin = KafkaAdminClient(bootstrap_servers=BOOTSTRAP)
            log.info("Connected to Kafka at %s", BOOTSTRAP)
            return admin
        except NoBrokersAvailable:
            log.warning("Kafka not reachable (attempt %d/%d), retrying...", attempt, retries)
            time.sleep(delay)
    log.error("Kafka unreachable at %s after %d attempts", BOOTSTRAP, retries)
    sys.exit(1)


def ensure_topic(admin):
    """Create the topic if it does not exist, so a fresh clone runs unattended."""
    try:
        admin.create_topics([
            NewTopic(name=TOPIC, num_partitions=PARTITIONS, replication_factor=1)
        ])
        log.info("Created topic '%s' with %d partitions", TOPIC, PARTITIONS)
    except TopicAlreadyExistsError:
        log.info("Topic '%s' already exists", TOPIC)


def main():
    admin = wait_for_broker()
    ensure_topic(admin)
    admin.close()

    producer = KafkaProducer(
        bootstrap_servers=BOOTSTRAP,
        key_serializer=lambda k: k.encode("utf-8"),
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        acks="all",   # wait for the broker to confirm the write
        retries=5,
        max_in_flight_requests_per_connection=1,  # keep order when a retry fires
        linger_ms=50,
    )

    if not os.path.exists(CSV_PATH):
        log.error("Dataset not found at %s", CSV_PATH)
        sys.exit(1)

    sent = 0
    previous_epoch = None

    with open(CSV_PATH, newline="") as handle:
        for row in csv.DictReader(handle):
            try:
                reading = parse_row(row)
            except (ValueError, KeyError) as exc:
                log.warning("Skipping malformed row: %s", exc)
                continue

            if previous_epoch is not None:
                gap = (reading["epoch"] - previous_epoch) / SPEED_FACTOR
                if gap > 0:
                    time.sleep(min(gap, MAX_SLEEP))
            previous_epoch = reading["epoch"]

            producer.send(TOPIC, key=reading["device"], value=reading)
            sent += 1

            if sent % 1000 == 0:
                log.info("Published %d readings", sent)

    producer.flush()
    producer.close()
    log.info("Finished. Published %d readings in total.", sent)


if __name__ == "__main__":
    main()
