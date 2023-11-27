import asyncio
from kafka_consumer_microservice import consume_and_index_logs, main as kafka_main
from elasticsearch_indexing_microservice import main as es_main
from logger import logger

# Asynchronous main function
async def main():
    logger.info(f"Creating task to perform asynchronously")

    # Start Kafka consumer and Elasticsearch instances
    kafka_consumer = await kafka_main()
    es_instance = await es_main()

    # Create tasks for consuming and indexing logs
    tasks = [
        consume_and_index_logs(kafka_consumer, es_instance),
        consume_and_index_logs(kafka_consumer, es_instance),
    ]

    # Wait for all tasks to complete
    await asyncio.gather(*tasks)

# Entry point
if __name__ == "__main__":
    logger.info(f"Starting main function asynchronously")
    asyncio.run(main())
