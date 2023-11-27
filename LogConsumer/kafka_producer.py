from aiokafka import AIOKafkaProducer
import asyncio
from .config import bootstrap_servers
from .logger import logger

class KafkaProducerSingleton:
    _instance = None

    # Singleton pattern to ensure only one instance is created
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._producer = None
        return cls._instance

    # Asynchronous method to get the Kafka producer instance
    async def get_producer(self):
        if not self._producer:
            logger.info("Creating a new Kafka producer object")
            self._producer = AIOKafkaProducer(
                bootstrap_servers=bootstrap_servers,
                loop=asyncio.get_event_loop()
            )
            await self._producer.start()
        return self._producer

    # Asynchronous method to stop the Kafka producer
    async def stop_producer(self):
        logger.info("Stopping the Kafka producer object")
        if self._producer:
            await self._producer.stop()

# Singleton instance of the KafkaProducerSingleton class
kafka_producer_singleton = KafkaProducerSingleton()
