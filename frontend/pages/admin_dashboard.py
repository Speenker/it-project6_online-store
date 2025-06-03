import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from services.analytics import (
    get_user_activity_analytics,
    get_error_analytics,
    get_user_behavior_analytics,
    get_financial_analytics,
    get_extended_financial_analytics
)

def show_dashboard():
    st.title("📊 Аналитическая панель")
    
    # Получаем данные о активности пользователей
    try:
        activity_data = get_user_activity_analytics()
        
        # Активность по часам
        st.subheader("Активность пользователей по часам")
        df_hourly = pd.DataFrame(activity_data['hourly_activity'])
        if not df_hourly.empty:
            fig_hourly = px.line(df_hourly, x='hour', y='count',
                               title='Активность по часам',
                               labels={'count': 'Количество действий', 'hour': 'Час'})
            st.plotly_chart(fig_hourly)
        else:
            st.info("Нет данных об активности по часам")
        
        # Топ действий
        st.subheader("Топ действий пользователей")
        df_actions = pd.DataFrame(activity_data['top_actions'])
        if not df_actions.empty:
            fig_actions = px.bar(df_actions, x='action', y='count',
                               title='Популярные действия',
                               labels={'count': 'Количество', 'action': 'Действие'})
            st.plotly_chart(fig_actions)
        else:
            st.info("Нет данных о действиях пользователей")
        
        # Топ активных пользователей
        st.subheader("Топ активных пользователей")
        df_users = pd.DataFrame(activity_data['top_users'])
        if not df_users.empty:
            fig_users = px.bar(df_users, x='email', y='count',
                             title='Активные пользователи',
                             labels={'count': 'Количество действий', 'email': 'Пользователь'})
            st.plotly_chart(fig_users)
        else:
            st.info("Нет данных о пользователях")
        
    except Exception as e:
        st.error(f"Ошибка при загрузке данных о активности: {str(e)}")
    
    # Получаем расширенную финансовую статистику
    try:
        financial_data = get_extended_financial_analytics()
        
        st.subheader("📈 Финансовая аналитика")
        
        # Общая статистика по заказам
        if financial_data['order_stats']:
            stats = financial_data['order_stats']
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.metric("Всего заказов", stats['total_orders'])
            with col2:
                st.metric("Общая выручка", f"{stats['total_revenue']:.2f} $")
            with col3:
                st.metric("Средний чек", f"{stats['avg_order_value']:.2f} $")
            with col4:
                st.metric("Выполненные заказы", stats['completed_orders'])
            with col5:
                st.metric("Отмененные заказы", stats['cancelled_orders'])
        
        # Статистика по категориям
        if financial_data['category_stats']:
            st.subheader("Статистика по категориям")
            df_categories = pd.DataFrame(financial_data['category_stats'])
            fig_categories = px.bar(df_categories, x='category', y='total_revenue',
                                  title='Выручка по категориям',
                                  labels={'total_revenue': 'Выручка ($)', 'category': 'Категория'})
            st.plotly_chart(fig_categories)
            
            # Таблица с детальной статистикой по категориям
            st.dataframe(df_categories, use_container_width=True)
        
        # Статистика по продуктам
        if financial_data['product_stats']:
            st.subheader("Топ продаваемых продуктов")
            df_products = pd.DataFrame(financial_data['product_stats'])
            
            # График выручки по продуктам
            fig_products = px.bar(df_products, x='product', y='total_revenue',
                                title='Выручка по продуктам',
                                labels={'total_revenue': 'Выручка ($)', 'product': 'Продукт'})
            st.plotly_chart(fig_products)
            
            # Таблица с детальной статистикой по продуктам
            st.dataframe(df_products, use_container_width=True)
        
        # Статистика по времени заказов
        # if financial_data['hourly_stats']:
        #     st.subheader("Распределение заказов по времени")
        #     df_hourly = pd.DataFrame(financial_data['hourly_stats'])
        #     df_hourly['hour'] = pd.to_datetime(df_hourly['hour']).dt.hour
            
        #     fig_hourly = px.line(df_hourly, x='hour', y='order_count',
        #                        title='Количество заказов по часам',
        #                        labels={'order_count': 'Количество заказов', 'hour': 'Час'})
        #     st.plotly_chart(fig_hourly)
        
        # Статистика по клиентам
        if financial_data['customer_stats']:
            st.subheader("Топ клиентов")
            df_customers = pd.DataFrame(financial_data['customer_stats'])
            
            # График выручки по клиентам
            fig_customers = px.bar(df_customers, x='email', y='total_spent',
                                 title='Выручка по клиентам',
                                 labels={'total_spent': 'Сумма покупок ($)', 'email': 'Клиент'})
            st.plotly_chart(fig_customers)
            
            # Таблица с детальной статистикой по клиентам
            st.dataframe(df_customers, use_container_width=True)
        
    except Exception as e:
        st.error(f"Ошибка при загрузке финансовой статистики: {str(e)}")

if __name__ == "__main__":
    show_dashboard() 