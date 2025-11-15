import streamlit as st
from common import redact_toml

st.title("Настройки")

THEMES = {
    "светлая": "light",
    "тёмная": "dark"
}

if 'theme' not in st.session_state:
    st.session_state.theme = None

theme = st.radio("Тема", list(THEMES.keys()))

if st.button(label="применить"):
    if theme != st.session_state.theme:
        st.session_state.theme = THEMES[theme]
        redact_toml(THEMES[theme])
