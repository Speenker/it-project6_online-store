from fastapi import APIRouter, Query
from services.products_service import ProductsService

router = APIRouter()
products_service = ProductsService()

@router.get("/products")
def get_products():
    return products_service.get_all_products()

@router.get("/products/{product_id}")
def get_product_details(product_id: int):
    return products_service.get_product_details(product_id)

@router.get("/products/{product_id}/reviews")
def get_product_reviews(product_id: int):
    return products_service.get_product_reviews(product_id)

@router.get("/search")
def search_products(q: str = Query(..., description="Поисковый запрос")):
    return products_service.search_products(q) 