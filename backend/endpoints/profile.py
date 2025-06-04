from fastapi import APIRouter, Body, Query
from services.profile_service import ProfileService
from typing import Dict

router = APIRouter()
profile_service = ProfileService()

@router.get("/user")
def get_user(email: str = Query(...)):
    return profile_service.get_user(email)

@router.post("/user/balance")
def update_balance(data: Dict = Body(...)):
    return profile_service.update_balance(data)

@router.get("/orders")
def get_user_orders(email: str = Query(...)):
    return profile_service.get_user_orders(email)

@router.get("/orders/{order_id}/items")
def get_order_items(order_id: int):
    return profile_service.get_order_items(order_id) 