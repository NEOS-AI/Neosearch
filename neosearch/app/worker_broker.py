from faststream.kafka import KafkaBroker
from faststream.redis import RedisBroker

# custom modules
from neosearch.constants.queue import USE_QUEUE, QUEUE_TYPE


# global singleton
_my_broker = None


def get_worker_broker():
    global _my_broker
    if _my_broker is not None:
        return _my_broker

    if not USE_QUEUE:
        raise Exception("Queue is not enabled")

    if QUEUE_TYPE == "redis":
        from neosearch.constants.queue import REDIS_URL, REDIS_DB

        broker = RedisBroker(
            url=REDIS_URL, db=REDIS_DB
        )
    elif QUEUE_TYPE == "kafka":
        from neosearch.constants.queue import (
            KAFKA_BOOTSTRAP_SERVERS,
            KAFKA_REQUEST_TIMEOUT_MS,
            KAFKA_MAX_IDLE_MS,
            KAFKA_COMPRESSION_TYPE,
        )

        broker = KafkaBroker(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            request_timeout_ms=KAFKA_REQUEST_TIMEOUT_MS,
            connections_max_idle_ms=KAFKA_MAX_IDLE_MS,
            compression_type=KAFKA_COMPRESSION_TYPE,
        )

    else:
        raise Exception("Invalid queue type")

    _my_broker = broker
    return broker
