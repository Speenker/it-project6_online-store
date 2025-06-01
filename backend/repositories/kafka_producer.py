from kafka import KafkaProducer
import json
from typing import Any, Dict
import logging

logger = logging.getLogger(__name__)

class KafkaEventProducer:
    def __init__(self, bootstrap_servers: str = 'kafka:9092'):
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        
    def send_event(self, topic: str, event: Dict[str, Any]) -> None:
        """
        Send an event to Kafka topic
        
        Args:
            topic: Kafka topic name
            event: Event data as dictionary
        """
        try:
            future = self.producer.send(topic, event)
            self.producer.flush()
            future.get(timeout=60)
            logger.info(f"Successfully sent event to topic {topic}")
        except Exception as e:
            logger.error(f"Failed to send event to topic {topic}: {str(e)}")
            raise 