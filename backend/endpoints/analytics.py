from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from services.analytics_service import AnalyticsService
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
analytics_service = AnalyticsService()

@router.post("/events/track")
async def track_event(user_id: str, event_type: str, event_data: Dict[str, Any]):
    """
    Track a user event
    
    Args:
        user_id: UUID of the user
        event_type: Type of the event
        event_data: Additional event data
    """
    try:
        analytics_service.track_user_event(user_id, event_type, event_data)
        return {"status": "success", "message": "Event tracked successfully"}
    except Exception as e:
        logger.error(f"Failed to track event: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/products/{product_id}")
async def get_product_analytics(product_id: str):
    """
    Get analytics data for a specific product
    
    Args:
        product_id: UUID of the product
        
    Returns:
        Product analytics data
    """
    try:
        analytics = analytics_service.get_product_analytics(product_id)
        if not analytics:
            raise HTTPException(status_code=404, detail="Product analytics not found")
        return analytics
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get product analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 