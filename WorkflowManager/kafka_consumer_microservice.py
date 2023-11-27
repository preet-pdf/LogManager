import asyncio
from datetime import datetime
import json
from aiokafka import AIOKafkaConsumer
from elasticsearch import helpers
from config import topic, bootstrap_servers, auto_offset_reset, group_id, bulk_size, bulk_timeout_seconds, index_name
from logger import logger

# Function to perform bulk indexing of logs in Elasticsearch
async def bulk_index(es, bulk_actions):
    logger.info("Adding logs in bulk")
    try:
        success, failed = helpers.bulk(es, bulk_actions, raise_on_error=True)
        logger.info(f"Bulk indexing successful: {success} documents, failed: {failed} documents")
    except Exception as e:
        logger.info(f"Error during bulk indexing: {e}")

# Function to consume Kafka logs and index them in Elasticsearch
async def consume_and_index_logs(consumer, es):
    logger.info("Consuming logs and adding in elastic")
    bulk_actions = []
    last_bulk_time = datetime.now()
    
    try:
        async for msg in consumer:
            log_data = json.loads(msg.value.decode())
            
            bulk_actions.append({
                "_op_type": "index",
                "_index": index_name,
                "_source": log_data
            })
            
            elapsed_time = (datetime.now() - last_bulk_time).total_seconds()
            if len(bulk_actions) >= bulk_size or elapsed_time >= bulk_timeout_seconds:
                logger.info("Bulk updating of size", len(bulk_actions))
                await bulk_index(es, bulk_actions)
                # Clearing bulk_actions after performing bulk indexing
                bulk_actions.clear()
                last_bulk_time = datetime.now()

    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received. Handling remaining messages.")
        
        if bulk_actions:
            logger.info("Not enough bulk operation ", len(bulk_actions), bulk_actions)
            await bulk_index(es, bulk_actions)
            bulk_actions.clear()

    
    finally:
        # Cancelling the periodic task and stopping the Kafka consumer
        periodic_task.cancel()
        await consumer.stop()
        # Clearing bulk_actions at the end
        bulk_actions = []

# Main function to start the Kafka consumer
async def main():
    logger.info("Starting main function")
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id=group_id,
        auto_offset_reset=auto_offset_reset,
        enable_auto_commit=True,
    )

    await consumer.start()
    logger.info("consumer started")

    return consumer
