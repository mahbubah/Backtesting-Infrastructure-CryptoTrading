from fastapi import FastAPI
from kafka import KafkaProducer, KafkaConsumer
import threading
import json
import logging

app = FastAPI()

KAFKA_BROKER_URL = "kafka:9092"

# Kafka Producer
producer = KafkaProducer(
    bootstrap_servers=['kafka:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def consume_messages():
    logging.basicConfig(level=logging.INFO)
    try:
        consumer = KafkaConsumer(
            'fastapi_topic',
            bootstrap_servers=['kafka:9092'],
            auto_offset_reset='earliest',
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        logging.info("Kafka Consumer has started listening")
        for message in consumer:
            logging.info(f"Consumed message: {message.value}")
    except Exception as e:
        logging.error(f"Error in Kafka consumer: {e}")



# Add an endpoint to your FastAPI application that publishes messages to a Kafka topic.
@app.post("/produce/")
async def produce_message(message: dict):
    producer.send('fastapi_topic', value=message)
    producer.flush()
    return {"message": "Produced to Kafka", "data": message}


# To run the Kafka consumer concurrently with your FastAPI application, you can use asyncio to create a background task. 
# However, since KafkaConsumer from kafka-python is not inherently asynchronous, you might run it in a separate thread or process, or use an asynchronous Kafka client like aiokafka.
# For simplicity, here's how you might start the consumer in a separate thread:

def start_consumer():
    thread = threading.Thread(target=consume_messages)
    thread.daemon = True
    thread.start()

start_consumer()