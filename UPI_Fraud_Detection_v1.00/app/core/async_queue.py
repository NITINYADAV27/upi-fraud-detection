import queue

# Global in-memory queue (Kafka-like)
transaction_queue = queue.Queue(maxsize=10000)
