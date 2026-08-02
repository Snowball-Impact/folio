# FOLIO Design System

이 문서는 FOLIO의 현재 UI 취향과 구현 규칙을 제품 디자인 시스템으로 고정한다. 목적은 새 화면을 만들 때 매번 취향을 다시 찾지 않고, 홈 갤러리에서 정리된 기준을 재사용하는 것이다.

## 1. 디자인 원칙

### 정돈된 라이트 UI

FOLIO는 흰 surface와 연한 blue-gray 배경을 기본으로 한다. 어두운 영역은 헤더와 카드 커버처럼 대비가 필요한 곳에만 제한적으로 사용한다.

### 필요한 컴포넌트만 쓴다

화면 설명을 위한 장식 카드, 중첩 카드, 불필요한 라벨은 피한다. 사용자가 실제로 조작하거나 판단하는 정보만 남긴다.

### 정보 위계가 먼저다

색상 베리에이션보다 제목, 요약, 태그, 메타 정보의 위치와 읽는 순서가 중요하다. 같은 의미의 정보는 같은 컨테이너 안에 묶는다.

### 홈 갤러리를 기준 화면으로 삼는다

홈 갤러리의 히어로, 탐색 패널, 16:9 카드 레일이 FOLIO의 기준 톤이다. 등록, 상세, 마이페이지는 이 기준에서 벗어나지 않게 맞춘다.

## 2. 디자인 토큰

현재 실제 CSS 토큰은 `folio_app/styles/tokens.py`의 `:root`에 있다.

| 토큰 | 값 | 용도 |
|---|---:|---|
| `--folio-navy` | `#0b1f3f` | 본문 제목, 헤더, 카드 하단 대비 |
| `--folio-blue` | `#1459c8` | primary action, 강조 텍스트, 활성 상태 |
| `--folio-mint` | `#0a9485` | 보조 성공/상태 강조 |
| `--folio-bg` | `#f4f7fd` | 앱 전체 배경 |
| `--folio-surface` | `#ffffff` | 히어로, 패널, 폼, 카드 컨테이너 |
| `--folio-border` | `#dce5f7` | 컨테이너 경계, 칩 경계 |
| `--folio-muted` | `#5c6f8a` | 설명, 보조 메타 텍스트 |
| `--folio-subtle` | `#eef3fd` | 연한 배경, 보조 칩 |

## 3. 타이포그래피

기본 폰트는 `Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif`다.

| 역할 | 기준 |
|---|---|
| 앱 본문 | 14px, line-height 1.6 전후 |
| 보조 설명 | 12-13px, `--folio-muted` |
| 섹션 제목 | 20px |
| 홈 카드 레일 제목 | 24px |
| 칩/버튼 텍스트 | 12-13px, 버튼은 700 전후, 태그칩은 과한 bold를 피함 |
| 프로필 주요 값 | 20px |

한글은 `word-break: keep-all`을 우선 사용한다. 제목은 과도한 letter spacing을 쓰지 않는다.

## 4. 레이아웃

### 페이지 폭

앱 본문은 `max-width: 1440px` 기준으로 중앙 정렬한다. 화면별 주요 컨테이너는 넓게 쓰되, 실제 읽기 본문은 900px 안팎으로 제한한다.

### 히어로

홈, 등록, 마이페이지 히어로는 같은 기준을 따른다.

- surface 배경, 1px border, 16px radius
- desktop padding: `28px 42px 34px`
- min-height: 220px
- 좌측 카피, 우측 16:9 visual
- CTA가 없는 서브페이지는 홈 히어로와 시각 기준선이 어긋나지 않게 보이지 않는 spacer를 둔다

모바일에서는 오른쪽 visual이 화면을 길게 만들면 숨긴다. 카피는 중앙 정렬한다.

### 섹션

섹션 제목과 설명은 가능한 한 한 행으로 정리한다. 제목은 왼쪽, 설명은 오른쪽에 둔다. 모바일에서는 세로로 쌓는다.

## 5. 핵심 컴포넌트

### Header

파일: `folio_app/components/layout.py`, `folio_app/styles/header.py`

- dark navy surface
- 왼쪽 Folio 로고, 오른쪽 nav
- 로그인 후 nav 라벨: `홈 갤러리`, `프로젝트 등록`, `마이 페이지`, `로그아웃`
- 현재 페이지는 underline으로 표시

### Page Hero

파일: `folio_app/components/layout.py`, `folio_app/styles/hero.py`

- `render_hero()`를 우선 사용한다.
- 등록/마이페이지는 홈 히어로 기준 여백을 따른다.
- 프로젝트 상세는 같은 구조를 쓰되 상세 정보량 때문에 `.folio-project-detail-hero` 예외 스타일을 둔다.
- 썸네일/visual은 16:9를 유지한다.
- 홈 히어로처럼 조각 HTML을 합쳐 렌더링하는 영역은 최종 HTML 문자열을 확인한다. 이미지 태그는 Markdown 렌더러가 오해하지 않도록 한 줄 HTML로 조합한다.

### Project Card

파일: `folio_app/components/ui.py`, `folio_app/components/home_gallery.py`, `folio_app/styles/cards.py`, `folio_app/styles/project_card_cover.py`, `folio_app/styles/gallery_rail.py`, `folio_app/styles/card_preview.py`

- 16:9 미디어 타일
- 제목 2줄, 요약 1줄, 태그 최대 4개 + `+N`, 푸터 메타
- 자동 커버는 24종 색/패턴 베리에이션
- 카드 전체 클릭은 stretched link 패턴을 사용한다.
- 홈 갤러리 레일에서만 hover 확대와 iframe preview를 켠다.
- 등록 미리보기, 상세 썸네일에는 hover action을 넣지 않는다.
- 카드 커버의 상단 eyebrow 라벨은 홈 카드에서 숨기고, 제목·요약·태그·메타의 상하 여백으로 정보 위계를 만든다.

### Chip

칩은 짧은 상태와 메타 정보를 묶는 데 사용한다.

- radius: 999px
- height: 32px 기준
- font-size: 12px
- border: `--folio-border`
- 조회수, 공개 상태, 링크 복사, 좋아요처럼 같은 레벨의 요소는 같은 컨테이너에 둔다.

### Button

파일: `folio_app/styles/buttons_inputs.py`

- primary action은 파란 배경과 흰 글자를 사용한다.
- secondary action은 흰 배경, border, navy/blue 텍스트를 사용한다.
- 한 화면의 primary action은 하나만 뚜렷하게 둔다.
- CTA 링크는 현재 창 이동을 기본으로 한다.

### Form Section Header

파일: `folio_app/components/project_form.py`, `folio_app/styles/project_form.py`

- 제목 왼쪽, 설명 오른쪽
- 번호 원형 배지는 사용하지 않는다.
- 입력 제약은 placeholder보다 tooltip/help와 validation으로 알려준다.

### Detail Action Bar

파일: `folio_app/pages/project_detail.py`, `folio_app/components/share.py`, `folio_app/styles/detail_page.py`, `folio_app/styles/hero_footer.py`

- 조회수, 댓글 수, 공개 상태, 링크 복사 버튼은 `project_action_group_html()`이 일반 HTML로 렌더링한다. 보이는 액션 UI는 custom component iframe 안에 넣지 않는다.
- 좋아요는 로그인 상태와 mutation 흐름 때문에 Streamlit button으로 유지하되, 액션 그룹 바로 오른쪽에 둔다.
- 조회수, 댓글 수, 공개 상태, 링크 복사, 좋아요를 별도 `st.columns()`에 흩어놓지 않는다. 상세 footer는 `st.container(horizontal=True, key="detail_footer_row")` 한 줄 안에서 메타, 액션 그룹, 좋아요 버튼을 sibling으로 둔다.
- 링크 복사 기능은 보이지 않는 0 크기 custom component iframe으로 이벤트 핸들러만 주입한다. iframe 안에 보이는 칩을 넣으면 viewport clipping으로 일부 칩이 잘릴 수 있다.
- 링크 복사 버튼 폭은 좋아요 칩과 통일감을 주는 수준으로 제한하고, 액션 그룹 전체는 우측 정렬한다.

### Profile Summary

파일: `folio_app/pages/protected.py`, `folio_app/styles/profile.py`

- 중앙 정렬
- 작성자, 소속, 이메일 값은 20px
- 통계는 작은 칩으로 묶는다.
- 비어 있는 상태는 장식보다 다음 행동을 명확히 보여준다.

## 6. 인터랙션 규칙

- 홈 갤러리 카드 hover: scale + dashboard preview 허용
- 등록 카드 미리보기: hover action 없음
- 상세 썸네일: hover action 없음
- 카드 preview iframe은 hover/focus 시 lazy mount한다.
- 좌우 레일 버튼은 카드 탐색에만 사용한다.
- 외부 결과물 링크는 상세의 대표 결과물 섹션 하단 액션으로 둔다.

## 7. Streamlit 구현 규칙

Streamlit UI는 Python 레이아웃과 브라우저 DOM wrapper가 같이 만든다. 시각 문제가 생기면 CSS만 보지 않는다.

- `st.columns()` 비율이 불필요한 빈 폭을 만들고 있는지 확인한다.
- `st.container(key=...)`가 실제로 어떤 `.st-key-*` wrapper를 만드는지 확인한다.
- `components.html()` iframe은 주변 button과 높이/정렬 기준이 다르다.
- selector가 실제 요소에 매치되는지 DOM에서 확인한다. key class와 target attribute가 같은 노드에 있으면 descendant selector가 아니라 compound selector를 써야 한다.
- 같은 줄로 보여야 하는 요소는 실제 구조에서도 같은 flex/grid 컨테이너 안에 둔다.
- Streamlit markdown, custom component iframe, Streamlit button이 섞이는 행은 wrapper가 세 종류가 되므로 먼저 구조를 단순화한다.
- 강한 상호작용은 화면 전용 wrapper 아래로 scope를 제한한다.
- Streamlit 내부 auto-generated class에는 의존하지 않는다.

## 8. 새 화면 추가 체크리스트

1. 이 화면의 기준이 홈, 상세, 등록, 마이페이지 중 어디인지 정한다.
2. 새 컴포넌트가 정말 필요한지 확인한다.
3. 기존 토큰으로 색상과 폰트 크기를 해결한다.
4. desktop과 mobile의 visual 노출 여부를 정한다.
5. 같은 의미의 메타/액션이 한 컨테이너 안에 묶였는지 확인한다.
6. hover/preview/scale 같은 상호작용이 필요한 화면에만 켜졌는지 확인한다.
7. 관련 스타일 모듈과 이 문서를 함께 갱신한다.
