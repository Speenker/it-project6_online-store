from fastapi import HTTPException
from repositories.cart import CartRepository
from repositories import products as product_repo
from repositories import users as user_repo
from repositories import orders as order_repo
from datetime import datetime

class CartService:
    def __init__(self):
        self.repository = CartRepository()
        # Временное хранилище корзин (на пользователя)
        self.carts = {}

    def get_cart(self, email: str):
        return self.carts.get(email, {"items": []})

    def add_to_cart(self, email: str, product_id: int, quantity: int = 1):
        # Получить товар
        product = product_repo.get_product_details(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Товар не найден")

        # Добавить в корзину
        cart = self.carts.setdefault(email, {"items": []})
        
        # Проверить, есть ли уже этот товар
        for item in cart["items"]:
            if item["product_id"] == product_id:
                item["quantity"] += quantity
                break
        else:
            cart["items"].append({
                "product_id": product_id,
                "name": product["name"],
                "price": product["price"],
                "quantity": quantity
            })
        return {"status": "ok"}

    def checkout_cart(self, email: str):
        cart = self.carts.get(email)
        if not cart or not cart["items"]:
            raise HTTPException(status_code=400, detail="Корзина пуста")

        user = user_repo.get_user_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        total_price = sum(item["quantity"] * item["price"] for item in cart["items"])
        if float(user["balance"]) < total_price:
            raise HTTPException(status_code=400, detail="Недостаточно средств на балансе")

        try:
            # Проверка остатков
            for item in cart["items"]:
                available_stock = self.repository.check_product_stock(item["product_id"], item["quantity"])
                if available_stock is None:
                    raise HTTPException(status_code=404, detail=f"Товар с ID {item['product_id']} не найден")
                if item["quantity"] > available_stock:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Недостаточно товара '{item['name']}'. Доступно: {available_stock}"
                    )

            # Обновляем баланс
            new_balance = float(user["balance"]) - total_price
            self.repository.update_user_balance(user["user_id"], new_balance)

            # Создаём заказ
            order_id = order_repo.create_order(
                user_id=user["user_id"],
                total_price=total_price,
                order_date=datetime.now(),
                status="Pending"
            )

            # Добавляем товары и обновляем остатки
            for item in cart["items"]:
                self.repository.create_order_item(order_id, item["product_id"], item["quantity"])
                self.repository.update_product_stock(item["product_id"], item["quantity"])

            self.carts[email] = {"items": []}
            return {"status": "ok", "order_id": order_id}

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Ошибка при оформлении заказа: {str(e)}")

    def clear_cart(self, email: str):
        self.carts[email] = {"items": []}
        return {"status": "ok"} 