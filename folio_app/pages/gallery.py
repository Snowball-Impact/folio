import streamlit as st

from folio_app.navigation import navigate


def render() -> None:
    preserved = {key: st.query_params.get(key) for key in st.query_params}
    navigate("Home", **{key: value for key, value in preserved.items() if key != "page"})
