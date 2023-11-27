import uvicorn
from fastapi import FastAPI
from .elasticsearch_utils import create_index
from .kafka_producer import kafka_producer_singleton
from .routes import router_injest, router_search
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from .logger import logger
from redis import asyncio as aioredis
from .config import index_name

# FastAPI app for ingestion
app_ingest = FastAPI()

# FastAPI app for search
app_search = FastAPI()
app_search.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create Elasticsearch index on startup
create_index(index_name)

# Include routers for ingestion and search apps
app_ingest.include_router(router_injest)
app_search.include_router(router_search)

# Run FastAPI apps using uvicorn if this module is executed directly
if __name__ == "__main__":
    logger.info("App is starting")
    uvicorn.run(app_ingest, host="127.0.0.1", port=3000, log_level="info")
    uvicorn.run(app_search, host="127.0.0.1", port=4000, log_level="info")

# Event handler for startup of the search app
@app_search.on_event("startup")
async def startup():
    logger.debug("On startup event")
    # Initialize FastAPI cache with Redis backend
    redis = aioredis.from_url("redis://localhost")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")

# Event handler for shutdown of the ingestion app
@app_ingest.on_event("shutdown")
async def shutdown_event():
    logger.debug("On closing event")
    # Stop the Kafka producer on app shutdown
    await kafka_producer_singleton.stop_producer()
