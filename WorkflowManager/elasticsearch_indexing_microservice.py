from elasticsearch import Elasticsearch
from logger import logger

#Main function to create elastic object
async def main():
    logger.info("Creating object of elastic")
    es = Elasticsearch("https://localhost:9200", verify_certs=False, http_auth=('elastic', 'Q3V9bNs-_lcRKfC=6Pe9'))
    return es
