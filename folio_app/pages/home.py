import streamlit as st

from folio_app.components.layout import render_hero, render_placeholder_card


def render() -> None:
    render_hero(
        "Portfolio Platform",
        "발표로 끝나지 않는 프로젝트",
        "데이터 분석 프로젝트를 포트폴리오 자산으로 축적하고 공유하세요.",
    )

    search = st.text_input("프로젝트 검색", placeholder="프로젝트명, 태그, 인사이트로 검색")
    if search:
        st.info("검색 기능은 Week 3에서 실제 프로젝트 데이터와 연결됩니다.")

    st.markdown("### 카테고리")
    st.pills(
        "카테고리",
        ["Data Analytics", "Power BI", "Public Data", "ML", "Visualization"],
        selection_mode="multi",
        label_visibility="collapsed",
    )

    st.markdown("### 인기 프로젝트")
    cols = st.columns(3)
    samples = [
        ("서울시 청년 취업 데이터 분석", "지역별 교육 인프라와 취업률의 관계를 탐색합니다.", "조회 124"),
        ("직업훈련 과정 수요 분석", "AI 과정 증가와 지역별 공급 편차를 확인합니다.", "조회 98"),
        ("공공자전거 이용 패턴 분석", "날씨와 출퇴근 시간대 수요 변화를 비교합니다.", "조회 74"),
    ]
    for col, sample in zip(cols, samples):
        with col:
            render_placeholder_card(*sample)
