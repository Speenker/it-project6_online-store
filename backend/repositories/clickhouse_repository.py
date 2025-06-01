from clickhouse_driver import Client
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class ClickHouseRepository:
    def __init__(self, host: str = 'clickhouse', port: int = 9000, database: str = 'default'):
        self.client = Client(host=host, port=port, database=database)
        self._init_tables()
    
    def _init_tables(self):
        """Initialize necessary tables for analytics"""
        self.client.execute('''
            CREATE TABLE IF NOT EXISTS user_events (
                event_id UUID,
                user_id UUID,
                event_type String,
                event_data String,
                created_at DateTime
            ) ENGINE = MergeTree()
            ORDER BY (created_at, event_id)
        ''')
        
        self.client.execute('''
            CREATE TABLE IF NOT EXISTS product_analytics (
                product_id UUID,
                views UInt32,
                purchases UInt32,
                revenue Decimal(18, 2),
                last_updated DateTime
            ) ENGINE = ReplacingMergeTree()
            ORDER BY (product_id, last_updated)
        ''')
    
    def insert_event(self, event_data: Dict[str, Any]) -> None:
        """
        Insert a new event into user_events table
        
        Args:
            event_data: Dictionary containing event data
        """
        try:
            self.client.execute(
                '''
                INSERT INTO user_events 
                (event_id, user_id, event_type, event_data, created_at)
                VALUES
                ''',
                [(
                    event_data['event_id'],
                    event_data['user_id'],
                    event_data['event_type'],
                    event_data['event_data'],
                    event_data['created_at']
                )]
            )
            logger.info(f"Successfully inserted event {event_data['event_id']}")
        except Exception as e:
            logger.error(f"Failed to insert event: {str(e)}")
            raise
    
    def update_product_analytics(self, analytics_data: Dict[str, Any]) -> None:
        """
        Update product analytics data
        
        Args:
            analytics_data: Dictionary containing product analytics data
        """
        try:
            self.client.execute(
                '''
                INSERT INTO product_analytics 
                (product_id, views, purchases, revenue, last_updated)
                VALUES
                ''',
                [(
                    analytics_data['product_id'],
                    analytics_data['views'],
                    analytics_data['purchases'],
                    analytics_data['revenue'],
                    analytics_data['last_updated']
                )]
            )
            logger.info(f"Successfully updated analytics for product {analytics_data['product_id']}")
        except Exception as e:
            logger.error(f"Failed to update product analytics: {str(e)}")
            raise
    
    def get_product_analytics(self, product_id: str) -> Dict[str, Any]:
        """
        Get analytics data for a specific product
        
        Args:
            product_id: UUID of the product
            
        Returns:
            Dictionary containing product analytics
        """
        try:
            result = self.client.execute(
                '''
                SELECT 
                    product_id,
                    views,
                    purchases,
                    revenue,
                    last_updated
                FROM product_analytics
                WHERE product_id = %(product_id)s
                ORDER BY last_updated DESC
                LIMIT 1
                ''',
                {'product_id': product_id}
            )
            
            if not result:
                return None
                
            return {
                'product_id': result[0][0],
                'views': result[0][1],
                'purchases': result[0][2],
                'revenue': float(result[0][3]),
                'last_updated': result[0][4]
            }
        except Exception as e:
            logger.error(f"Failed to get product analytics: {str(e)}")
            raise 