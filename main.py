import streamlit
import pandas as pd
import time
import uuid

from pages.admin_panel import show_admin_panel
from pages.cart import show_cart_page
from pages.main_page import show_main_page
from pages.profile import show_profile_page

from services.auth import Authotize
import services.users
import services.regist
import repositories.admin
import repositories.users
from cache.tokens import store_token, get_token_user_id, delete_token
from cache.redis_client import redis_client
import json

auth = Authotize()
users = services.users.get_users()
registr = services.regist.Registration()


def login():
    streamlit.title("Авторизация")
    streamlit.write("Введите почту и пароль:")

    email = streamlit.text_input("Почта")
    password = streamlit.text_input("Пароль", type="password")

    if streamlit.button("Войти"):
        if auth.auth(email, password):
            user = repositories.users.get_user(email)
            user_id = user["user_id"].item()

            token = str(uuid.uuid4())
            store_token(user_id, token)

            streamlit.session_state["authenticated"] = True
            streamlit.session_state["username"] = email
            streamlit.session_state["user"] = user
            streamlit.session_state["token"] = token
            streamlit.session_state["admin"] = repositories.admin.get_admins(user_id)

            streamlit.success(f"Добро пожаловать, {email}!")
            time.sleep(2)
            streamlit.rerun()
        else:
            streamlit.error("Неверная почта или пароль!")


def register():
    streamlit.title("Регистрация")
    email = streamlit.text_input("Почта")
    password = streamlit.text_input("Пароль", type="password")
    second_password = streamlit.text_input("Подтверждение пароля", type="password")

    if streamlit.button("Зарегистрироваться"):
        if not email or not password or not second_password:
            streamlit.error("Введите все поля!")
            return

        if password != second_password:
            streamlit.error("Пароли не совпадают!")
            return

        if users["email"].isin([email]).any():
            streamlit.error("Данная почта уже зарегистрирована!")
            return

        user_id = registr.registr(pd.DataFrame({"email": [email], "password": [password]}))
        token = str(uuid.uuid4())
        store_token(user_id, token)

        streamlit.success("Успешная регистрация!")
        streamlit.session_state["authenticated"] = True
        streamlit.session_state["token"] = token
        streamlit.session_state["user"] = pd.DataFrame({"user_id": [user_id], "email": [email]})
        streamlit.rerun()


def logout():
    streamlit.title("Выход")
    if streamlit.button("Выйти из аккаунта"):
        token = streamlit.session_state.get("token")
        if token:
            delete_token(token)
        streamlit.session_state.clear()
        streamlit.success("Вы вышли из аккаунта.")
        time.sleep(2)
        streamlit.rerun()

def main():
    if not streamlit.session_state["authenticated"]:
        pg = streamlit.radio("Войдите или зарегистрируйтесь", ["Вход", "Регистрация", "Основная"])
        if pg == "Вход":
            login()
        elif pg == "Регистрация":
            register()
        elif pg == "Основная":
            show_main_page()
    else:
        email = streamlit.session_state.user["email"].item()
        if streamlit.session_state["admin"]:
            page = streamlit.sidebar.radio(
                "Перейти к странице",
                ["Основная", "Профиль", "Корзина", "Панель Администратора", "Выход"]
            )
            if page == "Профиль":
                show_profile_page(email)
            elif page == "Корзина":
                show_cart_page(email)
            elif page == "Основная":
                show_main_page()
            elif page == "Панель Администратора":
                show_admin_panel()
            elif page == "Выход":
                logout()
        else:
            page = streamlit.sidebar.radio(
                "Перейти к странице",
                ["Основная", "Профиль", "Корзина", "Выход"]
            )
            if page == "Профиль":
                show_profile_page(email)
            elif page == "Корзина":
                show_cart_page(email)
            elif page == "Основная":
                show_main_page()
            elif page == "Выход":
                logout()


if "authenticated" not in streamlit.session_state:
    streamlit.session_state["authenticated"] = False

if "admin" not in streamlit.session_state:
    streamlit.session_state["admin"] = False

if "user" not in streamlit.session_state:
    streamlit.session_state.user = pd.DataFrame(columns=["user_id", "email", "balance"])

if __name__ == "__main__":
    main()
