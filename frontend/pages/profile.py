import streamlit as st
import requests
import time

API_URL = "http://fastapi:8000"

def show_profile_page(email):
    st.title("Ваш профиль")

    # Получение информации о пользователе
    try:
        resp = requests.get(f"{API_URL}/user", params={"email": email})
        resp.raise_for_status()
        user = resp.json()
    except Exception as e:
        st.error(f"Ошибка при получении профиля: {e}")
        return

    st.write(f"**Email:** {user['email']}")
    st.write(f"**Баланс:** {user['balance']:.2f} $")

    st.write("### Пополнение баланса")
    add_balance = st.number_input("Введите сумму", min_value=0.0, step=10.0)
    if st.button("Пополнить баланс"):
        if add_balance > 0:
            try:
                resp = requests.post(f"{API_URL}/user/balance", json={"email": email, "amount": add_balance})
                resp.raise_for_status()
                new_balance = resp.json()["balance"]
                st.success(f"Баланс успешно пополнен. Новый баланс: {new_balance:.2f}")
                time.sleep(2.0)
                st.rerun()
            except Exception as e:
                st.error(f"Ошибка при пополнении: {e}")
        else:
            st.warning("Введите положительную сумму!")

    st.divider()
    st.write("### Ваши заказы")
    try:
        orders_resp = requests.get(f"{API_URL}/orders", params={"email": email})
        orders_resp.raise_for_status()
        user_orders = orders_resp.json()
    except Exception as e:
        st.error(f"Ошибка при получении заказов: {e}")
        return

    if not user_orders:
        st.info("Вы еще не сделали ни одного заказа.")
    else:
        order_options = {f"Заказ #{order['order_id']} - {order['status']} ({order['order_date']})": order for order in user_orders}
        selected_order_name = st.selectbox("Выберите заказ для просмотра:", options=order_options.keys())
        selected_order = order_options[selected_order_name]
        if "items" not in st.session_state:
            st.session_state["items"] = False
        if st.button("Показать содержимое заказа", key="btn_items"):
            st.session_state["items"] = not st.session_state["items"]
        if st.session_state["items"]:
            try:
                items_resp = requests.get(f"{API_URL}/orders/{selected_order['order_id']}/items")
                items_resp.raise_for_status()
                order_items = items_resp.json()
            except Exception as e:
                st.error(f"Ошибка при получении содержимого заказа: {e}")
                order_items = []
            if not order_items:
                st.warning("Содержимое заказа отсутствует.")
            else:
                st.write(f"### Содержимое заказа #{selected_order['order_id']}")
                for item in order_items:
                    st.write(f"- **{item['name']}**: {item['quantity']} шт. — {item['price']} $") 