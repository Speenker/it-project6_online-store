import streamlit as st
import requests
import time

API_URL = "http://fastapi:8000"

def show_cart_page(email):
    st.title("Покупки")

    if "search_query" not in st.session_state:
        st.session_state.search_query = ""
    if "search_results" not in st.session_state:
        st.session_state.search_results = []

    search_query = st.text_input("Поиск по товарам (по названию и описанию):", st.session_state.search_query)
    use_search = st.button("Искать")

    products = []
    if search_query and use_search:
        try:
            resp = requests.get(f"{API_URL}/search", params={"q": search_query})
            resp.raise_for_status()
            products = resp.json()
            st.session_state.search_query = search_query
            st.session_state.search_results = products
        except Exception as e:
            st.error(f"Ошибка при поиске: {e}")
            return
    elif st.session_state.search_results:
        products = st.session_state.search_results
    else:
        try:
            resp = requests.get(f"{API_URL}/products")
            resp.raise_for_status()
            products = resp.json()
        except Exception as e:
            st.error(f"Ошибка при получении товаров: {e}")
            return

    if not products:
        st.warning("Товары не найдены.")
        return

    st.write("### Список товаров")

    try:
        resp = requests.get(f"{API_URL}/products")
        resp.raise_for_status()
        all_products = resp.json()
        stock_data = {p['product_id']: p['stock'] for p in all_products}
    except Exception as e:
        st.error(f"Ошибка при получении информации о наличии товаров: {e}")
        return

    try:
        cart_resp = requests.get(f"{API_URL}/cart", params={"email": email})
        cart_resp.raise_for_status()
        current_cart = cart_resp.json()
        cart_items = {item['product_id']: item['quantity'] for item in current_cart.get('items', [])}
    except Exception as e:
        st.error(f"Ошибка при получении корзины: {e}")
        cart_items = {}

    product_options = []
    for p in products:
        stock = stock_data.get(p['product_id'], 0)
        available_stock = stock - cart_items.get(p['product_id'], 0)
        product_options.append(f"{p['name']} — {p['price']} $ (Доступно: {available_stock} шт.)")

    selected_product_str = st.selectbox("Выберите товар", product_options, key="product_select")
    selected_product = next((p for p in products if p['name'] in selected_product_str), None)

    if selected_product:
        product_id = selected_product['product_id']
        current_stock = stock_data.get(product_id, 0)
        in_cart = cart_items.get(product_id, 0)
        available_stock = current_stock - in_cart

        if available_stock <= 0:
            st.warning(f"Товар '{selected_product['name']}' закончился на складе.")
        else:
            quantity = st.number_input("Количество", min_value=1, step=1, value=1, key="cart_quantity")

            if st.button("Добавить в корзину"):
                if quantity > available_stock:
                    st.error(f"Нельзя добавить в корзину {quantity} шт. товара '{selected_product['name']}'. Доступно только {available_stock} шт.")
                else:
                    try:
                        resp = requests.post(
                            f"{API_URL}/cart/add",
                            json={
                                "email": email,
                                "product_id": product_id,
                                "quantity": quantity
                            }
                        )
                        resp.raise_for_status()
                        st.success(f"Товар '{selected_product['name']}' добавлен в корзину.")
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Ошибка при добавлении в корзину: {e}")
    else:
        st.info("Выберите товар для добавления в корзину")

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
    insufficient_stock = []
    for item in cart["items"]:
        current_stock = stock_data.get(item['product_id'], 0)
        if item['quantity'] > current_stock:
            insufficient_stock.append(f"{item['name']} (заказано: {item['quantity']}, доступно: {current_stock})")
        st.write(f"- **{item['name']}**: {item['quantity']} шт. — {item['price']} $")
        total += item['quantity'] * item['price']

    st.write(f"**Итого:** {total} $")

    if st.button("Оформить заказ"):
        if insufficient_stock:
            st.error("Недостаточно товара на складе:")
            for item in insufficient_stock:
                st.error(f"- {item}")
        else:
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
