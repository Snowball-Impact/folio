import streamlit as st

from folio_app.components.layout import render_hero, render_placeholder_card


def render() -> None:
    render_hero(
        "Gallery",
        "프로젝트 갤러리",
        "데이터 분석 포트폴리오와 인사이트를 탐색하세요.",
    )

    st.text_input("검색어 입력", placeholder="예: Power BI, 공공데이터, 취업")
    left, right = st.columns([2, 1])
    with left:
        st.pills(
            "카테고리",
            ["전체", "Data Analytics", "Power BI", "Public Data", "ML"],
            default="전체",
        )
    with right:
        st.selectbox("정렬", ["최신순", "조회수순", "좋아요순"])

    render_placeholder_card(
        "서울시 청년 취업 데이터 분석",
        "청년 취업률은 지역별 교육 인프라와 함께 움직인다. 작성자: 홍길동",
        "조회 124 / 좋아요 12",
    )
    render_placeholder_card(
        "직업훈련 과정 수요 분석",
        "AI 과정은 증가했지만 지역별 공급 편차가 크다. 작성자: 김데이터",
        "조회 98 / 좋아요 7",
    )
