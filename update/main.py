import streamlit as st
import pandas as pd
import psycopg2

from common import DataBaseConnection, get_connection, download_csv

#Небольшая демоверсия
st.title("Coffeshop-online")

connection = get_connection()

with DataBaseConnection(connection) as cursor:
  query = "SELECT * FROM orders order by order_id LIMIT 20"
  cursor.execute(query)
  columns = [data[0] for data in cursor.description]
  data = cursor.fetchall()
  df = pd.DataFrame(data=data, columns=columns)
  st.data_editor(df, hide_index=True, disabled=["order_id"])
  download_csv(df, "orders_db")