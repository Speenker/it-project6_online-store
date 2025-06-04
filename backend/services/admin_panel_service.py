from fastapi import HTTPException
from repositories.admin import AdminRepository

class AdminPanelService:
    def __init__(self):
        self.repository = AdminRepository()

    def get_all_users(self):
        return self.repository.get_all_users()

    def get_all_orders(self):
        return self.repository.get_all_orders()

    def get_order_items(self, order_id: int):
        return self.repository.get_order_items(order_id)

    def update_order_status(self, order_id: int, status: str):
        return self.repository.update_order_status(order_id, status)

    def get_sales_analytics(self):
        try:
            total_sales = self.repository.get_total_sales()
            
            daily_sales = [
                {
                    "date": row[0].strftime("%Y-%m-%d"),
                    "sales": float(row[1]),
                    "orders": row[2]
                }
                for row in self.repository.get_daily_sales()
            ]

            top_products = [
                {
                    "name": row[0],
                    "quantity": row[1],
                    "revenue": float(row[2])
                }
                for row in self.repository.get_top_products()
            ]

            order_statuses = [
                {
                    "status": row[0],
                    "count": row[1],
                    "amount": float(row[2])
                }
                for row in self.repository.get_order_statuses()
            ]

            return {
                "total_sales": float(total_sales),
                "daily_sales": daily_sales,
                "top_products": top_products,
                "order_statuses": order_statuses
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Ошибка при получении аналитики: {str(e)}")

    def get_inventory_analytics(self):
        try:
            low_stock = [
                {
                    "name": row[0],
                    "stock": row[1],
                    "category": row[2],
                    "manufacturer": row[3]
                }
                for row in self.repository.get_low_stock_products()
            ]

            category_stats = [
                {
                    "category": row[0],
                    "product_count": row[1],
                    "total_stock": row[2],
                    "total_value": float(row[3])
                }
                for row in self.repository.get_category_stats()
            ]

            row = self.repository.get_inventory_summary()
            inventory_summary = {
                "total_products": row[0],
                "total_stock": row[1],
                "total_value": float(row[2])
            }

            return {
                "low_stock": low_stock,
                "category_stats": category_stats,
                "inventory_summary": inventory_summary
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Ошибка при получении аналитики: {str(e)}") 