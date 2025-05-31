import streamlit as st
import requests
import time

API_URL = "http://fastapi:8000"

def show_cart_page(email):
    st.title("Покупки")

    # Получение списка товаров
    try:
        resp = requests.get(f"{API_URL}/products")
        resp.raise_for_status()
        products = resp.json()
    except Exception as e:
        st.error(f"Ошибка при получении товаров: {e}")
        products = []

    if products:
        st.write("### Список товаров")
        product_options = [f"{p['name']} — {p['price']} $ (ID: {p['product_id']})" for p in products]
        selected_product_str = st.selectbox("Выберите товар", product_options, key="product_select")
        selected_product = next((p for p in products if p['name'] in selected_product_str), None)
        quantity = st.number_input("Количество", min_value=1, step=1, value=1, key="cart_quantity")
        if st.button("Добавить в корзину"):
            if selected_product:
                # Отправить запрос на добавление в корзину (локально, через API)
                try:
                    resp = requests.post(f"{API_URL}/cart/add", json={"email": email, "product_id": selected_product['product_id'], "quantity": quantity})
                    resp.raise_for_status()
                    st.success(f"Товар '{selected_product['name']}' добавлен в корзину.")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Ошибка при добавлении в корзину: {e}")

    st.divider()
    st.write("### Корзина")
    try:
        resp = requests.get(f"{API_URL}/cart", params={"email": email})
        resp.raise_for_status()
        cart = resp.json()
    except Exception as e:
        st.error(f"Ошибка при получении корзины: {e}")
        return

    if not cart or not cart.get("items"):
        st.info("Ваша корзина пуста.")
        return

    total = 0
    for item in cart["items"]:
        st.write(f"- **{item['name']}**: {item['quantity']} шт. — {item['price']} $")
        total += item['quantity'] * item['price']

    st.write(f"**Итого:** {total} $")

    if st.button("Оформить заказ"):
        try:
            resp = requests.post(f"{API_URL}/cart/checkout", json={"email": email})
            resp.raise_for_status()
            st.success("Заказ успешно оформлен!")
            time.sleep(2)
            st.rerun()
        except Exception as e:
            st.error(f"Ошибка при оформлении заказа: {e}")

    if st.button("Очистить корзину"):
        try:
            resp = requests.post(f"{API_URL}/cart/clear", json={"email": email})
            resp.raise_for_status()
            st.success("Корзина очищена!")
            time.sleep(1)
            st.rerun()
        except Exception as e:
            st.error(f"Ошибка при очистке корзины: {e}") 