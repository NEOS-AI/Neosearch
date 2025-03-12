from faststream.kafka import KafkaBroker
from faststream.redis import RedisBroker

# custom modules
from neosearch.constants.queue import USE_QUEUE


# global singleton
_my_broker = None


def get_worker_broker():
    global _my_broker
    if _my_broker is not None:
        return _my_broker

    if USE_QUEUE == "redis":
        from neosearch.constants.queue import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD

        broker = RedisBroker(
            host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD
        )
    elif USE_QUEUE == "kafka":
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
