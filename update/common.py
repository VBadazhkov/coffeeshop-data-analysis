import psycopg2
import pandas as pd
import streamlit as st
import toml
import os
from dotenv import load_dotenv

load_dotenv()
user=str(os.getenv("USER"))
password=str(os.getenv("PASSWORD"))
host=str(os.getenv("HOST"))
port=str(os.getenv("PORT"))
database=str(os.getenv("DATABASE"))

class DataBaseConnection:
  def __init__(self, connection):
    self.connection = connection

  def __enter__(self):
    self.cursor = self.connection.cursor()
    return self.cursor

  def __exit__(self, exc_type, exc_val, exc_tb):
    if exc_type is None:
      self.connection.commit()
    else:
      self.connection.rollback()

    self.cursor.close()
    self.connection.close()

def get_connection():
    connection = psycopg2.connect(
        user=user,
        password=password,
        host=host,
        port=port,
        database=database
    )
    return connection

def update_db_after_editing(connection, cursor, edited_df, original_df):
    try:
        for i in range(len(edited_df)):
            row_edited = edited_df.iloc[i]
            row_original = original_df.iloc[i]
                
            if not row_edited.equals(row_original):
                query = """update menu 
                set name_of_dish=%s, price=%s, dish_discount=%s, dish_category=%s, is_available=%s
                where menu.dish_id = %s"""
                cursor.execute(query, (str(row_edited["name_of_dish"]), float(row_edited["price"]), 
                                       float(row_edited["dish_discount"]), str(row_edited["dish_category"]), 
                                       bool(row_edited["is_available"]), int(row_edited["dish_id"])))
        connection.commit()
        st.success("Изменения сохранены!")

    except Exception as e:
        connection.rollback()
        st.write(f"Ошибка сохранения: {e}")

def download_csv(df, title, use_container_width=False):
  st.download_button(
        label="Скачать csv",
        data=df.to_csv(index=False, sep=";").encode("utf-8-sig"),
        file_name=f"{title}.csv",
        mime="text/csv",
        icon=":material/download:",
        use_container_width=use_container_width
    )
  
def download_png(fig, title):
  st.download_button(
        label="Скачать png",
        data=fig.to_image(format="png"),
        file_name=f"{title}.png",
        mime="image/png",
        icon=":material/download:"
    )

def redact_toml(theme):
    with open(".streamlit/config.toml", 'r') as f:
      content = toml.load(f)
      
      if 'theme' not in content:
        content['theme'] = {}

      theme_section = {'base': theme}
      content['theme'] = theme_section

    with open('.streamlit/config.toml', 'w') as f:
      toml.dump(content, f)
