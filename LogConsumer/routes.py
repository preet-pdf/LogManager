# routes.py
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from .kafka_producer import kafka_producer_singleton
from .elasticsearch_utils import es
from fastapi_cache.decorator import cache
import json
from .config import topic, index_name
from .logger import logger

# Router for log ingestion
router_injest = APIRouter()

# Router for log search
router_search = APIRouter()

# Ingest log endpoint
@router_injest.post("/")
async def ingest_log(log_data: dict):
    log_data['timestamp'] = datetime.now().isoformat()
    logger.info(f"Ingesting log to topic {topic}")

    producer = await kafka_producer_singleton.get_producer()
    await producer.send_and_wait(topic, json.dumps(log_data).encode())
    
    logger.info(f"Ingesting log to topic {topic} completed")
    return {"message": "Log ingested successfully"}

# Search logs endpoint
@router_search.get("/search/")
@cache(expire=60)
async def search_logs(
    level: Optional[str] = Query(None),
    message: Optional[str] = Query(None),
    resourceId: Optional[str] = Query(None),
    timestamp_from: Optional[datetime] = Query(None),
    timestamp_to: Optional[datetime] = Query(None),
    traceId: Optional[str] = Query(None),
    spanId: Optional[str] = Query(None),
    commit: Optional[str] = Query(None),
    parentResourceId: Optional[str] = Query(None),
    full_text: Optional[str] = Query(None),
):
    validate_dates(timestamp_from, timestamp_to)

    # Build Elasticsearch query based on query parameters
    must_conditions = [
        {"match": {"level": level}} if level else None,
        {"match": {"message": message}} if message else None,
        {"match": {"resourceId": resourceId}} if resourceId else None,
        {"range": {"timestamp": {"gte": timestamp_from, "lte": timestamp_to}}} if timestamp_from or timestamp_to else None,
        {"match": {"traceId": traceId}} if traceId else None,
        {"match": {"spanId": spanId}} if spanId else None,
        {"match": {"commit": commit}} if commit else None,
        {"match": {"metadata.parentResourceId": parentResourceId}} if parentResourceId else None,
        {"query_string": {"query": f"*{full_text}*"}} if full_text else None,
    ]

    # Remove None values from conditions
    must_conditions = [condition for condition in must_conditions if condition is not None]

    # Build the final query
    query = {"query": {"bool": {"must": must_conditions}}}

    logger.info(f"Hitting query to Elasticsearch: {query}")
    response = es.search(index=index_name, body=query)
    logger.info("Sending back the response")
    return response["hits"]["hits"]

# Function to validate timestamp_from and timestamp_to
def validate_dates(timestamp_from, timestamp_to):
    logger.info("Validating the dates")
    if timestamp_from and timestamp_to and timestamp_from > timestamp_to:
        logger.error("timestamp_from must be less than or equal to timestamp_to")
        raise HTTPException(status_code=400, detail="timestamp_from must be less than or equal to timestamp_to")
