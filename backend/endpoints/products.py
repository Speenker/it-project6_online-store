from fastapi import APIRouter, HTTPException
from repositories import products as repo

router = APIRouter()

@router.get("/products")
def get_products():
    return repo.get_all_products()

@router.get("/products/{product_id}")
def get_product_details(product_id: int):
    product = repo.get_product_details(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    manufacturer_name = None
    if product.get("manufacturer_id"):
        manufacturer_name = repo.get_manufacturer_name(product["manufacturer_id"])
    product["manufacturer_name"] = manufacturer_name
    return product

@router.get("/products/{product_id}/reviews")
def get_product_reviews(product_id: int):
    return repo.get_product_reviews(product_id) 