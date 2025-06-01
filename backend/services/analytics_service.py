from datetime import datetime
import uuid
from typing import Dict, Any
from repositories.kafka_producer import KafkaEventProducer
from repositories.clickhouse_repository import ClickHouseRepository
import logging

logger = logging.getLogger(__name__)

class AnalyticsService:
    def __init__(self):
        self.kafka_producer = KafkaEventProducer()
        self.clickhouse_repo = ClickHouseRepository()
        
    def track_user_event(self, user_id: str, event_type: str, event_data: Dict[str, Any]) -> None:
        """
        Track a user event and store it in both Kafka and ClickHouse
        
        Args:
            user_id: UUID of the user
            event_type: Type of the event (e.g., 'view_product', 'add_to_cart', 'purchase')
            event_data: Additional event data
        """
        event = {
            'event_id': str(uuid.uuid4()),
            'user_id': user_id,
            'event_type': event_type,
            'event_data': event_data,
            'created_at': datetime.utcnow()
        }
        
        # Send to Kafka for real-time processing
        self.kafka_producer.send_event('user_events', event)
        
        # Store in ClickHouse for analytics
        self.clickhouse_repo.insert_event(event)
        
        # If it's a product-related event, update product analytics
        if 'product_id' in event_data:
            self._update_product_analytics(event_data['product_id'], event_type)
    
    def _update_product_analytics(self, product_id: str, event_type: str) -> None:
        """
        Update product analytics based on the event type
        
        Args:
            product_id: UUID of the product
            event_type: Type of the event
        """
        current_analytics = self.clickhouse_repo.get_product_analytics(product_id) or {
            'product_id': product_id,
            'views': 0,
            'purchases': 0,
            'revenue': 0.0,
            'last_updated': datetime.utcnow()
        }
        
        # Update analytics based on event type
        if event_type == 'view_product':
            current_analytics['views'] += 1
        elif event_type == 'purchase':
            current_analytics['purchases'] += 1
            # Assuming price is in event_data
            current_analytics['revenue'] += float(event_data.get('price', 0))
        
        current_analytics['last_updated'] = datetime.utcnow()
        
        # Update in ClickHouse
        self.clickhouse_repo.update_product_analytics(current_analytics)
    
    def get_product_analytics(self, product_id: str) -> Dict[str, Any]:
        """
        Get analytics data for a specific product
        
        Args:
            product_id: UUID of the product
            
        Returns:
            Dictionary containing product analytics
        """
        return self.clickhouse_repo.get_product_analytics(product_id) 