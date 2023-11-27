# LogManager

LogManager, is structured into three primary components: LogConsumer, WebApp, and WorkflowManager. Each service plays a distinct role in the overall log management workflow.


## Project Structure


```bash
LogManager/
|-- LogConsumer/
|   |-- __init__.py
|   |-- config.py
|   |-- elasticsearch_utils.py
|   |-- kafka_producer.py
|   |-- logger.py
|   |-- main.py
|   |-- routes.py
|-- WebApp/
|   |-- index.html
|-- WorkflowManager/
|   |-- __init__.py
|   |-- config.py
|   |-- elasticsearch_indexing_microservice.py
|   |-- kafka_consumer_microservice.py
|   |-- logger.py
|   |-- orchestrator.py
|-- __init__.py
|-- getting_started.ini
|-- requirements.txt
|-- docker-compose.yml
```

## Descriptions of each service:

### 1. LogConsumer:

- **Description:** The `LogConsumer` service is responsible for ingesting logs. It exposes two endpoints (`app_ingest` and `app_search`) for log ingestion and searching, respectively.

- **Endpoints:**
  - **Ingest Logs:** `python3 -m uvicorn LogConsumer.main:app_ingest --host 127.0.0.1 --port 3000 --log-level info`
  - **Search Logs:** `python3 -m uvicorn LogConsumer.main:app_search --host 127.0.0.1 --port 4000 --log-level info`
  
- **Functionality:**
  - Ingests JSON logs.
  - Produces messages to Kafka.
  - Kafka topics are consumed, and logs are indexed in Elasticsearch.

### 2. WebApp:

- **Description:** The `WebApp` service provides a simple HTML interface (`index.html`) for users to interact with and search logs. It relies on the `LogConsumer` service for log searching.

- **Access:**
  - Open `index.html` in a web browser.

- **Functionality:**
  - Allows users to search logs using the `LogConsumer` service.

### 3. WorkflowManager:

- **Description:** The `WorkflowManager` service orchestrates the log indexing workflow. It consumes logs from Kafka, performs bulk indexing in Elasticsearch, and manages periodic updates.

- **Functionality:**
  - Consumes logs from Kafka.
  - Performs bulk indexing in Elasticsearch based on configured conditions.
  - Periodically updates Elasticsearch in bulk to enhance efficiency.

## Setting Up the Project:

### 1. Dependencies:
Install all dependencies listed in `requirements.txt` by running:
```bash
pip install -r requirements.txt 
```
## Infrastructure Setup

### Set up the following services:
**Note: For this project configuring Kafka, Elastic Search, and Redis locally is highly preferable and that's what we have done in this project. but I have given the docker compose file if someone don't want to set it up locally**

1. **Utilize the demo `docker-compose.yml` file to set up the necessary services (Kafka, Elasticsearch, and Redis).**

2. **Kafka:**
   - Configure `bootstrap.servers`, `group.id`, and `auto.offset.reset` in `LogConsumer/config.py` and `getting_started.ini`.

3. **Elasticsearch/Kibana:**
   - Configure `https://localhost:9200`, and authentication details like username and password in `LogConsumer/elasticsearch_indexing_microservice.py` and `WorkflowManager/elasticsearch_utils.py`.

4. **Configure the services in `LogConsumer/config.py`, `getting_started.ini` and `WorkflowManager/config.py` based on your environment.**

5. **Redis:**
   - Update the link (default: `redis://localhost`) in LogConsumer/main.py.


## Running the Project

### To start the project, execute the following commands:

1. Start the LogConsumer service (ingest and search) using two separate commands:

    ```bash
    python3 -m uvicorn LogConsumer.main:app_ingest --host 127.0.0.1 --port 3000 --log-level info
    ```

    ```bash
    python3 -m uvicorn LogConsumer.main:app_search --host 127.0.0.1 --port 4000 --log-level info
    ```

2. Start the WorkflowManager orchestrator:

    ```bash
    python3 WorkflowManager/orchestrator.py
    ```

## Configuring the Project

Update the configuration in `LogConsumer/config.py`, `WorkflowManager/config.py` and `getting_started.ini` according to your needs. Modify the Kafka, Elasticsearch, and Redis settings based on your environment.

## Project Flow

### Log Ingestion and Management

### Log Ingestion

1. Use the LogConsumer service (port 3000) to post JSON logs.
2. Kafka produces the messages in the configured topic (topic in LogConsumer/config.py).
3. The WorkflowManager consumes the Kafka topic, indexing the logs in Elasticsearch.

### Bulk Indexing

- To enhance efficiency, bulk updates are performed in Elasticsearch.
- Bulk updates occur when the number of logs exceeds a configured threshold (`bulk_size`), or a specified time (`bulk_timeout_seconds`) has passed.

## Log Searching

- Utilize the LogConsumer service (port 4000) or the `index.html` frontend to search logs.
- Query parameters for fields are available optionally.
- Search results are presented in a scrollable manner, and "No results found" is displayed if no data matches the query.

## Docker Compose

- A sample Docker Compose file (`docker-compose.yml`) is provided. It includes configurations for Kafka, Elasticsearch, and Redis.

## Why Separate LogConsumer and WorkflowManager Services?

1. **Scalability:** The separation allows for independent scaling of log ingestion (LogConsumer) and indexing (WorkflowManager) services.
2. **Flexibility:** Individual services can be updated or replaced without affecting the entire system.
3. **Maintainability:** Isolation of concerns for better code organization and easier maintenance.
4. **Enhanced Performance:** Specific optimizations can be applied to each service for optimal performance.
