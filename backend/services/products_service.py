from fastapi import HTTPException
from repositories import products as product_repo

class ProductsService:
    def __init__(self):
        self.repository = product_repo

    def get_all_products(self):
        return self.repository.get_all_products()

    def get_product_details(self, product_id: int):
        product = self.repository.get_product_details(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Товар не найден")
        
        manufacturer_name = None
        if product.get("manufacturer_id"):
            manufacturer_name = self.repository.get_manufacturer_name(product["manufacturer_id"])
        product["manufacturer_name"] = manufacturer_name
        
        return product

    def get_product_reviews(self, product_id: int):
        return self.repository.get_product_reviews(product_id)

    def search_products(self, query: str):
        return self.repository.search_products(query) 