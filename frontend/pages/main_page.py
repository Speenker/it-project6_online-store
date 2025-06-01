import streamlit as st
import requests

API_URL = "http://fastapi:8000"

def show_main_page():
    st.title("Каталог товаров")

    search_query = st.text_input("Поиск по товарам (по названию и описанию):", "")
    use_search = st.button("Искать")

    products = []
    if search_query and use_search:
        # Поиск через Elasticsearch
        try:
            resp = requests.get(f"{API_URL}/search", params={"q": search_query})
            resp.raise_for_status()
            products = resp.json()
        except Exception as e:
            st.error(f"Ошибка при поиске: {e}")
            return
    else:
        # Получение всех товаров
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

    product_names = [product["name"] for product in products]
    selected_product_name = st.selectbox("Выберите товар", product_names)
    selected_product = next((p for p in products if p["name"] == selected_product_name), None)
    if not selected_product:
        st.error("Ошибка при получении информации о товаре.")
        return

    product_id = selected_product["product_id"]

    # Получение деталей товара (всегда)
    try:
        details_resp = requests.get(f"{API_URL}/products/{product_id}")
        details_resp.raise_for_status()
        product_details = details_resp.json()
    except Exception as e:
        st.error(f"Ошибка при получении деталей товара: {e}")
        return

    # Получение отзывов
    try:
        reviews_resp = requests.get(f"{API_URL}/products/{product_id}/reviews")
        reviews_resp.raise_for_status()
        product_reviews = reviews_resp.json()
    except Exception as e:
        st.error(f"Ошибка при получении отзывов: {e}")
        product_reviews = []

    st.write(f"### {selected_product['name']}")
    st.write(f"**Цена:** {selected_product['price']} $")
    st.write(f"**Осталось на складе:** {product_details['stock']} шт.")

    if "description" not in st.session_state:
        st.session_state["description"] = False
    if "reviews" not in st.session_state:
        st.session_state["reviews"] = False

    if st.button("Описание", key="btn_description"):
        st.session_state["description"] = not st.session_state["description"]
    if st.session_state["description"]:
        st.write(f"**Описание:** {product_details['description']}")
        st.write(f"**Производитель:** {product_details.get('manufacturer_name', '-')} ({product_details.get('manufacturer_id', '-')})")

    if st.button("Отзывы", key="btn_reviews"):
        st.session_state["reviews"] = not st.session_state["reviews"]
    if st.session_state["reviews"]:
        if product_reviews:
            st.write("### Отзывы:")
            for review in product_reviews:
                st.write(f"- {review['review_text']} | {review['rating']}/5 🌟")
        else:
            st.write("Нет отзывов на этот товар.") 