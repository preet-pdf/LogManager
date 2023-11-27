from elasticsearch import Elasticsearch
from .logger import logger

# Elasticsearch instance with specified parameters
es = Elasticsearch("https://localhost:9200", verify_certs=False, http_auth=('elastic', 'Q3V9bNs-_lcRKfC=6Pe9'))

# Function to create an index if it does not exist
def create_index(index_name):
    if not es.indices.exists(index=index_name):
        logger.info(f"Creating index in Elasticsearch: {index_name}")
        es.indices.create(index=index_name)
