import streamlit as st
import pandas as pd
from common import get_connection, DataBaseConnection, update_db_after_editing, download_csv

st.title("Меню")

connection = get_connection()

with DataBaseConnection(connection) as cursor:
    query = "SELECT * FROM menu order by dish_id"
    cursor.execute(query)
    columns = [data[0] for data in cursor.description]
    data = cursor.fetchall()
    original_df = pd.DataFrame(data=data, columns=columns)
    edited_df = st.data_editor(original_df, hide_index=True, disabled=["dish_id"], num_rows="dynamic")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Сохранить", use_container_width=True):
            update_db_after_editing(connection=connection, cursor=cursor, edited_df=edited_df, original_df=original_df)
    with col2:
        download_csv(original_df, "menu_db", use_container_width=True)