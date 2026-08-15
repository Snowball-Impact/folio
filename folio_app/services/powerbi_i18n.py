"""Korean labels and summaries for curated Power BI content."""

from __future__ import annotations


MONTH_LABELS = {
    "January": "1월",
    "February": "2월",
    "March": "3월",
    "April": "4월",
    "May": "5월",
    "June": "6월",
    "July": "7월",
    "August": "8월",
    "September": "9월",
    "October": "10월",
    "November": "11월",
    "December": "12월",
}


def localize_release_label(value: str | None) -> str:
    text = str(value or "").strip()
    for english, korean in MONTH_LABELS.items():
        text = text.replace(english, korean)
    return text.replace("update", "업데이트")


def localize_date(value: str | None) -> str:
    text = str(value or "").strip()
    for english, korean in MONTH_LABELS.items():
        text = text.replace(english, korean)
    return text


def release_summary_bullet(row: dict[str, str]) -> str:
    raw_title = (
        row.get("feature_title_en")
        or row.get("feature_title_ko")
        or row.get("title_en")
        or row.get("title_ko")
        or ""
    )
    title = raw_title.lower()
    section = localize_section(row.get("section"))

    if "dataviz world championship" in title:
        return "Power BI 커뮤니티 시각화 대회 일정이 공개되었습니다."
    if "fabcon" in title:
        return "Fabric 및 Power BI 컨퍼런스 등록과 세션 정보가 업데이트되었습니다."
    if "fabric apps" in title and "semantic" in title:
        return "의미 체계 모델을 기반으로 업무용 데이터 앱을 만드는 Fabric 앱 기능이 미리 보기로 추가되었습니다."
    if "copilot" in title and "web modeling" in title:
        return "웹 모델링 화면에서 Copilot이 모델 작성과 수정 작업을 보조합니다."
    if "report authoring agent" in title:
        return "AI가 보고서 작성 과정의 일부를 대신 수행하도록 에이전트 기능이 미리 보기로 추가되었습니다."
    if "data answering" in title and "m365" in title:
        return "Microsoft 365 Copilot Chat에서 데이터 질문에 답하는 기능이 실험적으로 제공됩니다."
    if "data answering" in title:
        return "Fabric Skills와 협업 도구에서 데이터 질문에 답하는 기능이 실험적으로 제공됩니다."
    if "explore improvements" in title:
        return "Copilot 기반 데이터 탐색 흐름이 개선되어 필요한 인사이트를 더 빠르게 찾을 수 있습니다."
    if "summary shortcut" in title:
        return "Copilot 요약을 바로 실행할 수 있는 단축 기능이 추가되었습니다."
    if "shape map" in title:
        return "Shape Map 시각적 개체가 정식 기능으로 전환되어 지도 기반 표현을 더 안정적으로 사용할 수 있습니다."
    if "date picker" in title or "slicer" in title:
        return "슬라이서에 날짜 선택 기능이 추가되어 기간 필터를 더 쉽게 설정할 수 있습니다."
    if "user-defined function" in title or "udf" in title:
        return "DAX 사용자 정의 함수가 확장되어 반복 계산 로직을 더 깔끔하게 관리할 수 있습니다."
    if "matrix" in title:
        return "행렬 시각적 개체의 표시와 상호작용 기능이 개선되었습니다."
    if "visual calculation" in title and "custom total" in title:
        return "시각적 계산과 사용자 지정 합계가 정식 제공되어 보고서 안에서 계산 결과를 더 유연하게 보여줄 수 있습니다."
    if "custom total" in title:
        return "사용자 지정 합계 옵션이 늘어나 합계 행을 보고서 의도에 맞게 조정할 수 있습니다."
    if "scatter" in title:
        return "분산형 차트에서 데이터 포인트를 더 잘 비교할 수 있도록 시각화 옵션이 개선되었습니다."
    if "bar" in title or "column" in title:
        return "막대 및 열 차트의 표현 옵션이 보강되었습니다."
    if "card" in title:
        return "카드 시각적 개체에서 핵심 지표를 보여주는 방식이 개선되었습니다."
    if "azure map" in title or "maps" in title:
        return "Azure 지도와 지도 시각화 관련 표시 옵션이 개선되었습니다."
    if "tooltip" in title:
        return "도구 설명에서 보조 정보를 보여주는 방식이 개선되었습니다."
    if "model" in title:
        return "데이터 모델링 작업을 더 쉽게 관리할 수 있는 기능이 추가되었습니다."
    if "connector" in title or "data connectivity" in title:
        return "외부 데이터 연결과 커넥터 관련 기능이 업데이트되었습니다."
    if "preview" in title:
        return f"{section} 영역에 새 미리 보기 기능이 추가되었습니다."
    if "general availability" in title or "generally available" in title:
        return f"{section} 영역의 미리 보기 기능이 정식 기능으로 전환되었습니다."

    localized_title = localize_title(raw_title)
    return f"{section}: {localized_title}" if section and localized_title else localized_title


def localize_section(value: str | None) -> str:
    section = str(value or "").strip()
    section_map = {
        "Overview": "요약",
        "General": "일반",
        "Copilot and AI": "Copilot 및 AI",
        "Reporting": "보고서",
        "Modeling": "모델링",
        "Data connectivity": "데이터 연결",
        "Visualizations": "시각화",
        "Other": "기타",
    }
    return section_map.get(section, localize_title(section))


def localize_title(value: str | None) -> str:
    text = str(value or "").strip()
    replacements = {
        "update": "업데이트",
        "announcement": "공지",
        "registration": "등록",
        "Preview": "미리 보기",
        "General Availability": "정식 제공",
        "Semantic Models": "의미 체계 모델",
        "semantic models": "의미 체계 모델",
        "modeling": "모델링",
        "visual": "시각적 개체",
        "visuals": "시각적 개체",
        "slicer": "슬라이서",
        "Slicer": "슬라이서",
        "Maps": "지도",
        "Azure Maps": "Azure 지도",
        "Matrix": "행렬",
        "Card": "카드",
        "Tooltip": "도구 설명",
        "tooltips": "도구 설명",
        "DAX": "DAX",
        "Fabric Apps": "Fabric 앱",
        "Copilot": "Copilot",
        "Power BI": "Power BI",
    }
    for source, target in replacements.items():
        text = text.replace(source, target)
    return text


def localize_fix(value: str | None) -> str:
    original = str(value or "").strip().rstrip(".")
    if not original:
        return "변경 로그 항목"
    title = original.lower()

    if "data label positioning" in title and "column chart" in title:
        return "열 차트에서 데이터 레이블 위치가 어긋나던 문제가 수정되었습니다."
    if "native queries" in title and "export queries" in title:
        return "쿼리 내보내기에서 네이티브 쿼리를 출력 대상으로 저장할 때 실패하던 문제가 수정되었습니다."
    if "selected marker fill color" in title and "azure maps" in title:
        return "Azure 지도에서 선택한 마커 채우기 색상이 적용되지 않던 문제가 수정되었습니다."
    if "adbc driver assemblies" in title:
        return "ADBC 드라이버 어셈블리가 누락되던 문제가 수정되었습니다."
    if "view switcher icons" in title:
        return "Power BI Desktop에서 보기 전환 아이콘이 올바르게 표시되지 않던 문제가 수정되었습니다."
    if "empty schema" in title and "multimodel" in title:
        return "여러 모델을 함께 작성할 때 스키마가 비어 있는 것으로 처리되어 Copilot이나 모델 작성 화면에서 오류가 나던 문제가 수정되었습니다."
    if "calculated tables" in title and "refresh" in title:
        return "계산 테이블이 새로 고침 과정에서 누락되던 문제가 수정되었습니다."
    if "treat calculated tables as refreshable" in title:
        return "계산 테이블도 새로 고침 대상에 포함되도록 동작이 업데이트되었습니다."
    if "snowflake connector" in title and "directquery" in title:
        return "Snowflake 커넥터를 DirectQuery 모드로 사용할 때 지원되지 않는 쿼리 오류가 발생하던 문제가 수정되었습니다."
    if "pbip files" in title and "hangs" in title:
        return "연결 또는 파일 오류가 있는 PBIP 파일을 열 때 Power BI Desktop이 멈추던 문제가 수정되었습니다."
    if "oracle managed odp provider" in title:
        return "Oracle Managed ODP Provider 미리 보기 기능의 기본 설정이 일부 TNS alias 환경에서 실패하지 않도록 되돌려졌습니다."
    if "copilot orchestration throttling" in title:
        return "Copilot 오케스트레이션 제한 오류가 사용자 오류로 올바르게 분류되도록 수정되었습니다."
    if "refreshing tables" in title and "directquery" in title:
        return "DirectQuery 테이블을 새로 고침할 때 오류가 표시되던 문제가 수정되었습니다."
    if "unable to save" in title and "composite model" in title:
        return "LiveConnect에서 복합 모델로 변환한 뒤 보고서를 저장하지 못하던 문제가 수정되었습니다."
    if "queries" in title and "powerquery editor" in title:
        return "Power Query 편집기에서 쿼리 섹션이 보이지 않던 문제가 수정되었습니다."
    if "column or measure not found" in title:
        return "저장 시 '열 또는 측정값을 모델에서 찾을 수 없음' 오류가 발생하던 문제가 수정되었습니다."
    if "azure maps conversion dialog" in title:
        return "제한된 사용자에게 Azure Maps 변환 대화상자가 노출되던 문제가 수정되었습니다."
    if "ui buttons" in title and "conditional visibility" in title:
        return "조건부 표시 기능과 관련해 UI 버튼이 잘못 표시되던 문제가 수정되었습니다."
    if "databricks sql endpoint" in title:
        return "Databricks SQL Endpoint 연결 문제가 수정되었습니다."
    if "gen1 dataflows" in title:
        return "Gen1 Dataflows에서 향상된 컴퓨팅을 사용할 때 DirectQuery가 실패하던 문제가 수정되었습니다."
    if "pbir versioning" in title:
        return "Translytical task flows 미리 보기에서 PBIR 버전 관리 문제가 수정되었습니다."
    if "count-distinct" in title and "incorrect result" in title:
        return "Snowflake 쿼리의 count-distinct 계산이 잘못된 결과를 반환하던 문제가 수정되었습니다."
    if "creating relationships" in title and "snowflake" in title:
        return "Snowflake 연결 상태에서 관계를 만들 때 개체 참조 오류가 발생하던 문제가 수정되었습니다."
    if "ungrouping visuals" in title:
        return "시각적 개체 그룹을 해제한 뒤 페이지 이동이나 시각화 표시가 잘못되던 문제가 수정되었습니다."
    if "dataflow refresh" in title:
        return "Power BI Desktop에서 Dataflow 새로 고침이 실패하던 문제가 수정되었습니다."
    if "model.abf is stale" in title:
        return "로컬 model.abf가 오래된 상태일 때 모델을 열며 테이블 새로 고침이 실패하던 문제가 수정되었습니다."
    if "region not supported" in title:
        return "Copilot에서 알 수 없는 오류 코드가 발생할 때 더 이해하기 쉬운 '지역 미지원' 메시지로 표시되도록 수정되었습니다."
    if "index was outside the bounds" in title:
        return "커넥터 Implementation 2.0 사용 시 배열 범위 오류가 발생하던 문제가 수정되었습니다."
    if "incremental refresh validation" in title:
        return "여러 데이터 원본을 참조하는 테이블의 증분 새로 고침 검증 문제가 수정되었습니다."
    if "high-contrast mode" in title and "manage relationships" in title:
        return "고대비 모드에서 관계 관리 창의 체크박스와 아이콘이 왜곡되어 보이던 문제가 수정되었습니다."

    text = original
    replacements = {
        "Fixed an issue where ": "",
        "Fixed issues with ": "",
        "Fixed issue where ": "",
        "Addressed an issue of ": "",
        "Addressed an issue where ": "",
        "wasn't": "적용되지 않던 문제가",
        "failed": "실패하던 문제가",
        "missing": "누락되던 문제가",
        "data label positioning": "데이터 레이블 위치",
        "column charts": "열 차트",
        "native queries": "네이티브 쿼리",
        "Export queries": "쿼리 내보내기",
        "output destination": "출력 대상",
        "selected marker fill color": "선택한 마커 채우기 색상",
        "Azure Maps": "Azure 지도",
        "ADBC driver assemblies": "ADBC 드라이버 어셈블리",
        " in ": " 관련 ",
    }
    for source, target in replacements.items():
        text = text.replace(source, target)
    if not text.endswith(("수정", "개선", "해결")):
        text = f"{text} 수정"
    return text
