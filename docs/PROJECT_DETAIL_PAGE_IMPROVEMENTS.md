# 프로젝트 상세 페이지 UI/UX 개선 - 진행 상황 기록

**작업 기간**: 2026-07-06  
**상태**: 1차 개선 완료 (PC·모바일 렌더링 검증)  
**담당**: UI/UX 개선

---

## 최신 구현 상태 — 이 섹션을 우선 참고

아래의 초기 진행 기록에는 이전 배치가 남아 있다. 새 작업에서는 이 섹션과 `PROJECT_CONTEXT.md`를 현재 기준으로 사용한다.

### 히어로

- 본문: 라벨, 프로젝트명, 한 줄 소개, 프로젝트 커버
- 푸터 왼쪽: `작성자`, `소속`, `등록일` 라벨과 값
- 푸터 오른쪽: 조회수, 좋아요, 읽기 전용 공개 상태
- 오른쪽 세 요소는 동일한 컬럼 비율과 38px 높이
- 히어로 본문/푸터 좌측 좌표와 우측 좌표를 브라우저에서 실측해 일치시킴
- HTML 히어로와 Streamlit 액션은 별도 렌더링하되 CSS로 하나의 카드처럼 연결

### 프로젝트 비주얼

- `대시보드`와 `첨부 자료` 사이에만 구분선 표시
- 영문 보조 라벨 `PROJECT VISUAL`, `RESOURCES`는 사용하지 않음
- iframe, 대시보드 열기, 보고서/GitHub 버튼은 카드 폭을 넘지 않음
- `목록으로 돌아가기`는 비주얼 카드 하단에 배치

### 동작

- 공개 여부 변경은 상세 화면이 아니라 `마이 페이지 → 수정` 폼에서 수행
- mutation 전에 Auth 세션을 복구하고 PostgREST에 JWT를 다시 적용
- 인증이 유효하지 않으면 RLS 오류 원문 대신 재로그인 안내

### 완료 검증 기준

- 시각적으로 비슷해 보이는 것만으로 완료 처리하지 않는다.
- 동일 크기 요청: `getBoundingClientRect()`로 너비·높이를 비교한다.
- 동일 여백 요청: 대상의 `left/right` 좌표를 비교한다.
- Streamlit 버튼 폭은 `stTooltipHoverTarget`을 포함한 중간 래퍼를 확인한다.
- PC 1440×900, 모바일 390×844에서 확인한다.

---

## 📋 개선 목표

프로젝트 상세 페이지의 UI/UX를 세련되게 개선하여:
- 뒤로가기 네비게이션 명확화
- 메타데이터 (작성자, 소속, 등록일, 공개상태) 시각화
- 액션 버튼 (조회수, 좋아요, 비공개 전환) 히어로 영역에 통합
- 섹션별 콘텐츠 카드화 및 아이콘 추가
- 반응형 디자인 개선

---

## ✅ 구현된 내용

### 1. 파일 수정 현황

#### [folio_app/pages/project_detail.py]
**변경사항:**
- 뒤로가기 버튼을 페이지 최상단에서 히어로 액션 영역으로 이동
- 메타데이터 렌더링 개선 (작성자, 소속, 등록일, 공개상태)
- `_render_hero_footer_actions()` 함수 개선:
  - 4개 컬럼 레이아웃: 뒤로가기, 조회수, 좋아요, 비공개전환
  - 모든 액션 버튼을 히어로 푸터에 포함
- `_render_detail_like_button()` 함수 유지
- `_render_project_sidebar()` 함수에 이모지 아이콘 추가

**주요 코드 구조:**
```python
def _render_hero_footer_actions() -> None:
    # 4개 컬럼에 뒤로가기, 조회수, 좋아요, 비공개 전환 배치
    action_col1, action_col2, action_col3, action_col4 = st.columns([2, 1, 1, 1])
    # 각 컬럼에 버튼/메트릭 렌더링
```

#### [folio_app/styles.py]
**추가된 CSS (~300줄):**

1. **메타데이터 스타일** (새 버전)
   - `.folio-detail-meta-section`: 메타데이터 컨테이너
   - `.folio-detail-meta-row`: 메타데이터 행
   - `.folio-detail-meta-item`: 개별 메타데이터 항목
   - 점(·) 구분자로 구분 (::after 사용)
   - `.folio-detail-visibility`: 공개상태 뱃지

2. **섹션 카드 스타일**
   - `.folio-detail-section`: 카드 기반 섹션 (border, border-radius, padding)
   - `.folio-detail-section-title`: 섹션 제목 (하단 보더라인)
   - `.folio-detail-section-content`: 콘텐츠 본문 (타이포그래피)

3. **버튼 호버 효과**
   - `.st-key-detail_hero_back_button`: 뒤로가기 버튼
   - `.st-key-detail_like_action`: 좋아요 버튼
   - `.st-key-detail_visibility_toggle`: 비공개 전환 버튼
   - 모든 버튼에 부드러운 트랜지션 추가

4. **히어로 푸터 액션 스타일**
   - `.st-key-folio_hero_footer_actions`: 푸터 액션 컨테이너
   - 히어로 바로 아래 연결되도록 음수 마진 적용
   - 배경색과 보더가 히어로 푸터와 동일

5. **반응형 CSS**
   - 태블릿 (max-width: 1024px)
   - 모바일 (max-width: 768px)
   - 메타데이터 항목 간 간격 조정

#### [folio_app/components/layout.py]
**변경사항:**
- `render_hero()` 함수에서 `footer_actions()` 렌더링 방식 개선
- 액션을 별도의 컨테이너에서 렌더링하도록 변경:
  ```python
  if footer_actions:
      with st.container(border=False, key="folio_hero_footer_actions"):
          footer_actions()
  ```

### 2. 시각적 개선 사항

**메타데이터 표시 형식:**
```
작성자 · 소속 · 날짜 · 🔓 공개
```

**섹션 아이콘:**
- 📋 문제 정의
- 📊 사용 데이터
- 🔍 분석 과정
- 💡 핵심 인사이트

**사이드바 섹션:**
- 📊 대시보드
- 🔗 첨부 파일

**액션 버튼 배치:**
```
[← 목록] [조회수] [♡ 좋아요] [비공개]
```

---

## ⚠️ 알려진 문제점

### 1. 히어로 내부 통합 미완성
- **상황**: 조회수, 좋아요, 비공개 전환 버튼이 HTML 푸터 내부에 배치되지 않음
- **원인**: Streamlit의 제약사항
  - HTML 요소 내부에 동적 Streamlit 컴포넌트(버튼, 메트릭)를 직접 삽입할 수 없음
  - 모든 Streamlit 컴포넌트는 HTML 외부에서 렌더링됨
- **현재 상태**: 
  - HTML로 렌더링되는 메타데이터는 히어로 푸터 내부
  - 버튼/메트릭은 별도 컨테이너에서 렌더링 후 CSS로 히어로처럼 스타일링
- **시각적 결과**: 버튼들이 히어로 바로 아래 있어 일부 통합된 것처럼 보임
  - 완전한 시각적 통합은 아님

### 2. 버튼 렌더링 문제
- `footer_actions()` 콜백이 실제로 호출되는지 확인 필요
- Streamlit 세션 상태에서 올바르게 표시되는지 검증 필요

---

## 🔧 수정 사항 요약

| 파일 | 수정 내용 | 상태 |
|------|---------|------|
| `folio_app/pages/project_detail.py` | 뒤로가기·메타데이터·액션 버튼 개선 | ✅ 완료 |
| `folio_app/styles.py` | ~300줄 CSS 추가 (메타데이터·섹션·버튼·반응형) | ✅ 완료 |
| `folio_app/components/layout.py` | footer_actions 컨테이너 래핑 | ✅ 완료 |

---

## 📝 다음 단계 (향후 개선 사항)

### 우선순위 1: 버튼 렌더링 검증
- [ ] Streamlit 서버에서 실제 표시 확인
- [ ] 메타데이터 점(·) 구분자 표시 확인
- [ ] 액션 버튼 작동 여부 확인
- [ ] 반응형 CSS 작동 확인

### 우선순위 2: 완전한 히어로 통합 (기술적 제약)
**현재 Streamlit의 제약으로 인한 문제:**
- HTML 푸터 내부에 버튼 직접 삽입 불가
- 가능한 해결 방안:
  1. **Custom Component 사용**: Streamlit Component 개발 (복잡)
  2. **HTML + JavaScript**: footer_html에 자체 버튼 구현 (상호작용 어려움)
  3. **현재 방식 유지**: CSS로 시각적 통합 (현재 구현)

### 우선순위 3: 사이드바 개선
- [ ] 첨부 파일 링크 스타일 개선
- [ ] 대시보드 임베드 로딩 상태 개선

### 우선순위 4: 성능 최적화
- [ ] CSS 파일 크기 확인
- [ ] 불필요한 스타일 정리

---

## 💡 기술적 참고사항

### Streamlit 컴포넌트 렌더링 원리
```
1. HTML 콘텐츠 (st.markdown + unsafe_allow_html=True)
   ↓ (별도로 렌더링)
2. Streamlit 컴포넌트 (st.button, st.metric 등)
```

- HTML과 Streamlit 컴포넌트는 서로 다른 렌더링 레이어에서 작동
- 따라서 HTML 푸터 내부에 버튼을 직접 배치할 수 없음
- 대신 CSS를 사용해 시각적으로 통합하는 방식으로 해결

### 설계 토큰 (CSS Variables)
```css
--folio-navy: #0b1f3f       /* 주 색상 */
--folio-blue: #1459c8       /* 강조 색상 */
--folio-mint: #0a9485       /* 보조 색상 */
--folio-bg: #f4f7fd         /* 배경 */
--folio-surface: #ffffff    /* 표면 */
--folio-muted: #5c6f8a      /* 약한 텍스트 */
--folio-border: rgba(...)   /* 보더 색상 */
```

---

## 📚 참고 문서
- [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md) - 프로젝트 전체 개요
- [WEEK1_BUILD_CHECKLIST.md](WEEK1_BUILD_CHECKLIST.md) - 1주차 체크리스트
- [WEEK2_BUILD_CHECKLIST.md](WEEK2_BUILD_CHECKLIST.md) - 2주차 체크리스트

---

**작성자 노트:** 현재 Streamlit의 기술적 제약으로 인해 완전한 히어로 내부 통합은 불가능하지만, CSS를 활용한 시각적 통합으로 타협점을 찾았습니다. 다음 작업 시에는 실제 브라우저에서 렌더링 결과를 검증하고 필요시 추가 스타일 조정이 필요합니다.
