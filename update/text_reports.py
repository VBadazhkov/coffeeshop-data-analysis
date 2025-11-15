import streamlit as st
import pandas as pd
import plotly.express as px
from common import DataBaseConnection, get_connection, download_csv

st.title("Текстовые отчеты")

connection = get_connection()

with DataBaseConnection(connection) as cursor:
    query = "SELECT order_id, time, total_cost, cashier FROM orders order by order_id"
    cursor.execute(query)
    columns = [data[0] for data in cursor.description]
    data = cursor.fetchall()
    df = pd.DataFrame(data=data, columns=columns)

    # Эффективность кассиров
    st.subheader("Эффективность кассиров")
    query = """SELECT full_name, count(order_id), round(avg(total_cost), 2), 
    sum(total_cost), round(avg(total_cost) * count(order_id) / 300, 2) FROM orders
    INNER JOIN cashiers
    ON orders.cashier = cashiers.cashier_id
    group by full_name order by full_name"""
    cursor.execute(query)
    columns = ["ФИО", "принятые заказы", "средний чек", "прибыль", "KPI"]
    data = cursor.fetchall()
    df = pd.DataFrame(data=data, columns=columns)
    st.dataframe(df, hide_index=True)
    download_csv(df, "cashier_effeciency")

    # Самые популярные блюда
    st.subheader("Самые популярные блюда")
    query = """SELECT name_of_dish, count(dish_id) as num_ordered, sum(price_at_order) as total_income 
    FROM order_items 
    INNER JOIN menu 
    ON menu.dish_id = order_items.menu_item_id
    GROUP BY name_of_dish
    ORDER BY total_income DESC
    LIMIT 10
    """
    cursor.execute(query)
    columns = ["позиция", "количество заказов", "суммарный доход по позиции"]
    data = cursor.fetchall()
    df = pd.DataFrame(data=data, columns=columns)
    st.dataframe(df, hide_index=True)
    download_csv(df, "popular_dishes")

    # Самые частые пожелания
    st.subheader("Самые частые пожелания")
    query = """SELECT DISTINCT wishes, COUNT(wishes) as quantity
    FROM orders
    WHERE wishes IS NOT NULL
    GROUP BY wishes
    ORDER BY quantity DESC
    LIMIT 10
    """
    cursor.execute(query)
    columns = ["пожелание", "количество"]
    data = cursor.fetchall()
    df = pd.DataFrame(data=data, columns=columns)
    st.dataframe(df, hide_index=True)
    download_csv(df, "wishes")



