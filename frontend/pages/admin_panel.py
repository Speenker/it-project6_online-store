import streamlit as st
import requests

API_URL = "http://fastapi:8000"

def show_admin_panel():
    st.title("Панель администратора")
    st.write("### Список пользователей")
    try:
        resp = requests.get(f"{API_URL}/admin/users")
        resp.raise_for_status()
        users = resp.json()
    except Exception as e:
        st.error(f"Ошибка при получении пользователей: {e}")
        users = []
    for user in users:
        st.write(f"- {user['email']} (ID: {user['user_id']}, Роль: {user.get('role', '-')})")

    st.write("### Список товаров")
    try:
        resp = requests.get(f"{API_URL}/products")
        resp.raise_for_status()
        products = resp.json()
    except Exception as e:
        st.error(f"Ошибка при получении товаров: {e}")
        products = []
    for product in products:
        st.write(f"- {product['name']} (ID: {product['product_id']}, Цена: {product['price']}$)")

    st.write("### Список заказов")
    try:
        resp = requests.get(f"{API_URL}/admin/orders")
        resp.raise_for_status()
        orders = resp.json()
    except Exception as e:
        st.error(f"Ошибка при получении заказов: {e}")
        orders = []
    for order in orders:
        st.write(f"- Заказ #{order['order_id']} | Пользователь: {order['user_id']} | Сумма: {order['total_price']}$ | Статус: {order['status']}") 