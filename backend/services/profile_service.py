from fastapi import HTTPException
from repositories import users as user_repo, orders as order_repo
from typing import Dict

class ProfileService:
    def __init__(self):
        self.user_repo = user_repo
        self.order_repo = order_repo

    def get_user(self, email: str):
        user = self.user_repo.get_user_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        return user

    def update_balance(self, data: Dict):
        email = data["email"]
        amount = data["amount"]
        
        user = self.user_repo.get_user_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
            
        new_balance = float(user["balance"]) + float(amount)
        self.user_repo.update_user_balance(email, new_balance)
        
        return {"balance": new_balance}

    def get_user_orders(self, email: str):
        user = self.user_repo.get_user_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        return self.order_repo.get_user_orders(user["user_id"])

    def get_order_items(self, order_id: int):
        return self.order_repo.get_order_items(order_id) 