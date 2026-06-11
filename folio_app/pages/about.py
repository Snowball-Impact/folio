import streamlit as st

from folio_app.components.layout import render_hero


def render() -> None:
    render_hero(
        "About",
        "FOLIO 소개",
        "FOLIO는 데이터 분석 프로젝트를 포트폴리오 자산으로 축적하고 공유하는 플랫폼입니다.",
    )

    st.markdown("### 왜 만들었나요?")
    st.write("교육 현장에서 생산된 프로젝트가 발표 이후 사라지는 문제를 해결하기 위해 만들었습니다.")

    st.markdown("### 핵심 철학")
    st.write("AI 시대에도 휴먼 인사이트는 자산입니다.")

    st.markdown("### 우리가 검증하는 것")
    st.write("1. 사람들은 자신의 프로젝트를 공개할 의향이 있는가")
    st.write("2. 사람들은 다른 사람의 프로젝트를 탐색할 의향이 있는가")
