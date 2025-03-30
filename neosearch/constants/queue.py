USE_QUEUE = True
QUEUE_TYPE = "redis"  # "redis" or "kafka"

# redis
REDIS_URL = "redis://localhost:6379"
REDIS_DB = "redis"

# kafka
KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
KAFKA_REQUEST_TIMEOUT_MS = 3000
KAFKA_MAX_IDLE_MS = 540000
KAFKA_COMPRESSION_TYPE = "zstd"  # 'gzip', 'snappy', 'lz4', 'zstd'
