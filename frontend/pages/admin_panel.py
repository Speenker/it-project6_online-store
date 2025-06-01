import streamlit as st
import requests
import time

API_URL = "http://fastapi:8000"

def show_admin_panel():
    st.title("Панель администратора 🧑‍💻")

    # Раздел для управления статусами заказов
    st.header("Управление статусами заказов")
    try:
        resp = requests.get(f"{API_URL}/admin/orders")
        resp.raise_for_status()
        orders = resp.json()
    except Exception as e:
        st.error(f"Ошибка при получении заказов: {e}")
        return

    # Фильтрация заказов, исключая Completed
    pending_or_shipped_orders = [order for order in orders if order["status"] != "Completed"]

    if not pending_or_shipped_orders:
        st.warning("Нет заказов для обработки.")
    else:
        order_options = {f"Заказ #{order['order_id']} (Текущий статус: {order['status']})": order for order in pending_or_shipped_orders}
        selected_order_name = st.selectbox("Выберите заказ для изменения статуса:", options=order_options.keys())
        selected_order = order_options[selected_order_name]

        new_status = st.selectbox(
            f"Изменить статус заказа #{selected_order['order_id']}:",
            options=["Pending", "Shipped", "Completed"],
            index=["Pending", "Shipped", "Completed"].index(selected_order["status"]),
            key=f"update_status_{selected_order['order_id']}"
        )

        if st.button("Обновить статус заказа"):
            try:
                resp = requests.put(
                    f"{API_URL}/admin/orders/{selected_order['order_id']}/status",
                    json={"status": new_status}
                )
                resp.raise_for_status()
                st.success(f"Статус заказа #{selected_order['order_id']} обновлен на '{new_status}'.")
                time.sleep(1.5)
                st.rerun()
            except Exception as e:
                st.error(f"Ошибка при обновлении статуса заказа: {e}")

        # Инициализация состояния для отображения деталей заказа
        if f"items_admin_{selected_order['order_id']}" not in st.session_state:
            st.session_state[f"items_admin_{selected_order['order_id']}"] = False

        if st.button(
            "Показать содержимое заказа",
            key=f"btn_items_admin_{selected_order['order_id']}"
        ):
            st.session_state[f"items_admin_{selected_order['order_id']}"] = not st.session_state[f"items_admin_{selected_order['order_id']}"]

        if st.session_state[f"items_admin_{selected_order['order_id']}"]:
            try:
                resp = requests.get(f"{API_URL}/admin/orders/{selected_order['order_id']}/items")
                resp.raise_for_status()
                order_items = resp.json()

                if not order_items:
                    st.info("Заказ не содержит товаров.")
                else:
                    st.write("### Содержимое заказа:")
                    for item in order_items:
                        st.write(f"- **{item['name']}**: {item['quantity']} шт. — {item['price']} $")
            except Exception as e:
                st.error(f"Ошибка при получении деталей заказа: {e}")

    st.divider()

    # Раздел для просмотра пользователей
    st.header("Список пользователей")
    
    # Инициализация состояния для отображения списка пользователей
    if "show_users" not in st.session_state:
        st.session_state.show_users = False

    if st.button("Показать/скрыть список пользователей"):
        st.session_state.show_users = not st.session_state.show_users

    if st.session_state.show_users:
        try:
            resp = requests.get(f"{API_URL}/admin/users")
            resp.raise_for_status()
            users = resp.json()

            if not users:
                st.warning("Пользователи отсутствуют в базе данных.")
            else:
                for user in users:
                    st.write(f"- **{user['email']}** (Роль: {user['role']}, Баланс: {user['balance']} $)")
        except Exception as e:
            st.error(f"Ошибка при получении списка пользователей: {e}")