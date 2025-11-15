import streamlit as st
import toml

pages = {
    "Принять заказ": [st.Page("main.py", title="Заказ")],
    "Меню":  [st.Page("menu.py", title="Меню")],
    "Отчеты": [st.Page("graph_reports.py", title="Графические отчеты"), st.Page("text_reports.py", title="Текстовые отчеты")],
    "Информация": [st.Page("info.py", title="О приложении")],
    "Настройки": [st.Page("settings.py", title="Настройки")]
}

pg = st.navigation(pages)
pg.run()

