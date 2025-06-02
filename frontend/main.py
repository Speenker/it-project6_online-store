import streamlit as st
import requests
import time
import asyncio

from pages.main_page import show_main_page
from pages.cart import show_cart_page
from pages.profile import show_profile_page
from pages.admin_panel import show_admin_panel
from pages.admin_dashboard import show_dashboard
from services.kafka_logger import log_user_action
from services.logging_config import logger
from services.tracing_service import TracingService
import pandas as pd

API_URL = "http://fastapi:8000"
tracing_service = TracingService()

async def make_traced_request(url: str, method: str = "GET", **kwargs):
    return await tracing_service.trace_request(url, method, **kwargs)

def login():
    st.title("Авторизация")
    email = st.text_input("Почта")
    password = st.text_input("Пароль", type="password")
    if st.button("Войти"):
        response = asyncio.run(make_traced_request(
            f"{API_URL}/login",
            method="POST",
            json={"email": email, "password": password}
        ))
        if response.status_code == 200:
            data = response.json()
            st.session_state["authenticated"] = True
            st.session_state["token"] = data["token"]
            st.session_state["user"] = data["user"]
            st.session_state["admin"] = data.get("is_admin", False)
            
            # Log successful login
            log_user_action('login', email)
            
            st.success(f"Добро пожаловать, {email}!")
            time.sleep(1)
            st.rerun()
        else:
            st.error("Неверная почта или пароль!")

def register():
    st.title("Регистрация")
    email = st.text_input("Почта")
    password = st.text_input("Пароль", type="password")
    second_password = st.text_input("Подтверждение пароля", type="password")
    if st.button("Зарегистрироваться"):
        if not email or not password or not second_password:
            st.error("Введите все поля!")
            return
        if password != second_password:
            st.error("Пароли не совпадают!")
            return
        response = asyncio.run(make_traced_request(
            f"{API_URL}/register",
            method="POST",
            json={"email": email, "password": password}
        ))
        if response.status_code == 200:
            # Log successful registration
            log_user_action('register', email)
            
            st.success("Успешная регистрация! Теперь войдите.")
            time.sleep(1)
            st.rerun()
        else:
            st.error(response.json().get("detail", "Ошибка регистрации"))

def logout():
    st.title("Выход")
    if st.button("Выйти из аккаунта"):
        # Log logout
        if "user" in st.session_state:
            log_user_action('logout', st.session_state['user']['email'])
        
        st.session_state.clear()
        st.success("Вы вышли из аккаунта.")
        time.sleep(1)
        st.rerun()

def main():
    # Initialize logging
    # Инициализация состояний сессии
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if "admin" not in st.session_state:
        st.session_state["admin"] = False

    if "user" not in st.session_state:
        st.session_state.user = pd.DataFrame(columns=["user_id", "email", "balance"])
    
    if not st.session_state.get("authenticated"):
        pg = st.radio("Войдите или зарегистрируйтесь", ["Вход", "Регистрация", "Основная"])
        if pg == "Вход":
            login()
        elif pg == "Регистрация":
            register()
        elif pg == "Основная":
            show_main_page()
    else:
        user = st.session_state["user"]
        is_admin = st.session_state.get("admin", False)
        page_options = ["Основная", "Профиль", "Корзина", "Выход"]
        if is_admin:
            page_options.insert(-1, "Панель Администратора")
            page_options.insert(-1, "Аналитика")
        page = st.sidebar.radio("Перейти к странице", page_options)
        if page == "Профиль":
            show_profile_page(user["email"])
        elif page == "Корзина":
            show_cart_page(user["email"])
        elif page == "Основная":
            show_main_page(user["email"])
        elif page == "Панель Администратора":
            show_admin_panel()
        elif page == "Аналитика":
            show_dashboard()
        elif page == "Выход":
            logout()

if __name__ == "__main__":
    main() 