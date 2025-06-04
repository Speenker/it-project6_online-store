from fastapi import APIRouter, Query, Body
from typing import Dict
from services.cart_service import CartService

router = APIRouter()
cart_service = CartService()

@router.get("/cart")
def get_cart(email: str = Query(...)):
    return cart_service.get_cart(email)

@router.post("/cart/add")
def add_to_cart(data: Dict = Body(...)):
    return cart_service.add_to_cart(
        email=data["email"],
        product_id=data["product_id"],
        quantity=int(data.get("quantity", 1))
    )

@router.post("/cart/checkout")
def checkout_cart(data: Dict = Body(...)):
    return cart_service.checkout_cart(data["email"])

@router.get("/cart/clear")
def clear_cart(data: Dict = Body(...)):
    return cart_service.clear_cart(data["email"]) 