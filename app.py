import streamlit as st

st.set_page_config(
    page_title="FOLIO",
    page_icon="F",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from folio_app.app import main


if __name__ == "__main__":
    main()
