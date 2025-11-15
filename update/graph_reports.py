import streamlit as st
import pandas as pd
import plotly.express as px
from common import DataBaseConnection, get_connection, download_png

st.title("Отчеты")

connection = get_connection()

with DataBaseConnection(connection) as cursor:
    query = """SELECT time, total_cost FROM orders order by order_id"""
    cursor.execute(query)
    columns = [data[0] for data in cursor.description]
    data = cursor.fetchall()
    df = pd.DataFrame(data=data, columns=columns)
    
    # Заказы по часам
    fig = px.histogram(df, x='time', nbins=24, title="Заказы по часам")
    st.plotly_chart(fig)
    download_png(fig, "orders_by_hour")

    # Выручка по часам
    fig = px.histogram(df, x='time', y='total_cost', title="Выручка по часам", text_auto=True)
    st.plotly_chart(fig)
    download_png(fig, "income_by_hour")

    # Распределение стоимости заказа по времени
    fig = px.scatter(df, x='time', y='total_cost', title="Распределение стоимости заказа по времени")
    st.plotly_chart(fig)
    download_png(fig, "order_cost_by_time")

    # Принятые заказы и выручка по кассирам
    query = """SELECT count(order_id) as amount_by_cashier, sum(total_cost) as cost_by_cashier, full_name 
    FROM orders 
    INNER JOIN cashiers
    ON cashiers.cashier_id = orders.cashier
    group by full_name 
    order by full_name"""
    cursor.execute(query)
    columns = [data[0] for data in cursor.description]
    data = cursor.fetchall()
    df = pd.DataFrame(data=data, columns=columns)
    fig = px.bar(df, x='full_name', y='cost_by_cashier', title="Выручка по кассирам", color='full_name')
    st.plotly_chart(fig)
    download_png(fig, "income_by_cashiers")
    
    fig = px.bar(df, x='full_name', y='amount_by_cashier', title="Принятые заказы по кассирам", color='full_name')
    st.plotly_chart(fig)
    download_png(fig, "orders_by_cashiers")

    # Boxplot цен
    query = """SELECT * FROM menu"""
    cursor.execute(query)
    columns = [data[0] for data in cursor.description]
    data = cursor.fetchall()
    df = pd.DataFrame(data=data, columns=columns)
    fig = px.box(df, x='dish_category', y='price', title="Распределение цен по категориям", color='dish_category')
    st.plotly_chart(fig)
    download_png(fig, "prices_boxplot")
    
    # Прибыль по категориям блюд
    query = """SELECT dish_category, sum(price_at_order) as total_income FROM order_items INNER JOIN menu 
    ON menu.dish_id = order_items.menu_item_id
    GROUP BY dish_category
    ORDER BY total_income DESC
    """
    cursor.execute(query)
    columns = [data[0] for data in cursor.description]
    data = cursor.fetchall()
    df = pd.DataFrame(data=data, columns=columns)
    fig = px.bar(df, x='dish_category', y='total_income', title="Прибыль по категориям блюд", color='dish_category')
    st.plotly_chart(fig)
    download_png(fig, "income_by_category")

    # Прибыль по блюдам (точечный график)
    query = """SELECT name_of_dish, dish_id, sum(price_at_order) as total_income FROM order_items INNER JOIN menu 
    ON menu.dish_id = order_items.menu_item_id
    GROUP BY dish_id
    """
    cursor.execute(query)
    columns = [data[0] for data in cursor.description]
    data = cursor.fetchall()
    df = pd.DataFrame(data=data, columns=columns)
    df['total_income'] = pd.to_numeric(df['total_income'])
    fig = px.scatter(df, x='dish_id', y='total_income', size='total_income', color='total_income', title="Прибыль по блюдам")
    st.plotly_chart(fig)
    download_png(fig, "income_by_dish")

    



