import json
from kafka import KafkaConsumer, TopicPartition
from pymongo import MongoClient
from datetime import datetime

KAFKA_BROKER = "kafka:9092"
TOPIC = "file-events-json"
PARTITION = 0
MONGO_URI = "mongodb://mongo:27017"

mongo_client = MongoClient(MONGO_URI)
db = mongo_client["ztipe"]
collection = db["raw_events"]

consumer = KafkaConsumer(
    bootstrap_servers=KAFKA_BROKER,
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)
tp = TopicPartition(TOPIC, PARTITION)
consumer.assign([tp])
consumer.seek_to_beginning(tp)

print("✅ Consumer started and listening to Kafka...")
for msg in consumer:
    event = msg.value
    event["_kafka_offset"] = msg.offset
    event["_ingested_at"] = datetime.utcnow().isoformat()
    collection.insert_one(event)
    print(f"📥 Inserted: {event}")