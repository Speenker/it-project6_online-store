import json
from kafka import KafkaProducer
from datetime import datetime
import logging
from .logging_config import logger
from .clickhouse_logger import log_to_clickhouse

# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS = 'kafka:9092'
TOPIC_USER_ACTIONS = 'user_actions'

# Initialize Kafka producer
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def log_user_action(action_type, email, **kwargs):
    """
    Log user actions to Kafka, console and ClickHouse
    """
    try:
        # Prepare log data
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'action_type': action_type,
            'email': email,
            **kwargs
        }
        
        # Send to Kafka
        producer.send(TOPIC_USER_ACTIONS, value=log_data)
        
        # Log to console
        logger = logging.getLogger('kafka_logger')
        logger.info(f"User Action: {action_type} | User: {email} | Details: {kwargs}")
        
        # Log to ClickHouse
        log_to_clickhouse(action_type, email, **kwargs)
        
    except Exception as e:
        logger = logging.getLogger('kafka_logger')
        logger.error(f"Failed to log user action: {str(e)}")