from fastapi import APIRouter
from pydantic import BaseModel
from services.admin_panel_service import AdminPanelService

router = APIRouter()
admin_service = AdminPanelService()

class OrderStatusUpdate(BaseModel):
    status: str

@router.get("/admin/users")
def get_all_users():
    return admin_service.get_all_users()

@router.get("/admin/orders")
def get_all_orders():
    return admin_service.get_all_orders()

@router.get("/admin/orders/{order_id}/items")
def get_order_items(order_id: int):
    return admin_service.get_order_items(order_id)

@router.put("/admin/orders/{order_id}/status")
def update_order_status(order_id: int, status_update: OrderStatusUpdate):
    return admin_service.update_order_status(order_id, status_update.status)

@router.get("/admin/dashboard/sales")
def get_sales_analytics():
    return admin_service.get_sales_analytics()

@router.get("/admin/dashboard/inventory")
def get_inventory_analytics():
    return admin_service.get_inventory_analytics() 