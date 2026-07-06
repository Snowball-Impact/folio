# FOLIO 프로젝트 컨텍스트

새 대화에서 작업을 이어갈 때 이 문서를 먼저 읽어라.
코드와 문서가 다르면 코드베이스를 확인한 뒤 이 문서를 고쳐라.
민감 정보(API 키, 비밀번호 등)는 이 문서에 기록하지 않는다.

---

## 프로젝트 개요

**FOLIO** — 데이터 분석 프로젝트를 포트폴리오 자산으로 등록·탐색·공유하는 MVP.
핵심 메시지: "발표로 끝나지 않는 프로젝트 / AI 시대에는 휴먼 인사이트가 자산이다."

- **스택**: Streamlit + Supabase (PostgreSQL + Auth)
- **실행**: `streamlit run app.py` → `http://localhost:8501`
- **엔트리**: 루트 `app.py` → `folio_app/app.py:main()`

---

## 파일 구조 (핵심만)

```
folio_app/
  app.py                  # 진입점. 쿠키 복구, 라우팅, 온보딩 체크
  styles.py               # 전역 CSS 주입 (apply_global_styles)
  config.py               # 환경변수 로드 (get_settings)
  navigation.py           # 내부 이동 공통 헬퍼와 허용 라우트
  components/
    layout.py             # render_header(), render_hero(), render_placeholder_card()
    ui.py                 # clean_html(), 공통 UI 헬퍼
    project_form.py       # 프로젝트 등록/수정 폼
  pages/
    home.py               # 홈 + 탐색 허브 + 상세 뷰
    project_detail.py     # 상세 렌더링 (home에서 project_id 쿼리로 호출)
    auth.py               # render_login(), render_signup()
    gallery.py            # 레거시 → Home으로 리다이렉트
    protected.py          # render_submit(), render_my_portfolio(), render_profile()
    onboarding.py         # 약관 동의 온보딩
  services/
    auth.py               # get_current_user(), sign_in/out, restore_session()
    profiles.py           # get_profile(), update_profile(), get_onboarding_status()
    projects.py           # CRUD + 좋아요 + 통계
    project_content.py    # 프로젝트 본문 HTML 허용 목록 정제
    supabase_client.py    # Streamlit 세션별 Supabase client
  static/
    hero-preview.png      # 홈 히어로 우측 미리보기 이미지
```

---

## 구현 완료 기능

| 기능 | 파일 | 비고 |
|------|------|------|
| 회원가입 / 이메일 인증 | `auth.py` | Supabase Auth |
| 로그인 / 로그아웃 | `auth.py`, `app.py` | EncryptedCookieManager로 세션 유지 |
| 온보딩 (약관 동의) | `onboarding.py`, `profiles.py` | 첫 로그인 후 강제 진입 |
| 프로필 조회 / 수정 | `protected.py` | 이름, 소속, 자기소개 |
| 프로젝트 등록 / 수정 / 삭제 | `protected.py`, `project_form.py` | |
| 홈 탐색 (검색, 태그, 정렬) | `home.py` | Gallery 페이지 없음, Home이 탐색 허브 |
| 프로젝트 상세 | `project_detail.py` | `?project_id=` 쿼리로 Home 안에서 렌더링 |
| 좋아요 | `projects.py`, `project_detail.py` | 비로그인 → Login으로 이동 |
| 푸터 | `app.py` | Copyright © 2026 Snowball Impact |

---

## 라우팅 구조

`st.query_params["page"]` 값으로 화면 전환. 모든 페이지 이동은 `st.rerun()`.

| page 값 | 화면 | 비고 |
|---------|------|------|
| Home (기본) | 홈 + 탐색 허브 | `?project_id=` 있으면 상세 |
| Login | 로그인 | |
| Sign Up | 회원가입 | nav에 노출 안 됨, 링크로만 접근 |
| Submit | 프로젝트 등록 | 로그인 필요 |
| My Portfolio | 내 포트폴리오 | 로그인 필요 |
| Profile | 프로필 | 로그인 필요 |
| Gallery | 레거시 | Home으로 리다이렉트 |

---

## 네비게이션 구조 (중요)

**인증 상태나 데이터를 변경하는 동작에는 HTML `<a href>` 링크를 사용하지 않는다.**

이유: HTML 링크 클릭 → 브라우저 전체 리로드 → WebSocket 끊김 → `session_state` 초기화 → `get_current_user() = None` → 로그인 상태 소실.

**현재 구현**: `navigation.py`의 `navigate()`가 `st.query_params` + `st.rerun()` 패턴을 통합한다. 공개 프로젝트 카드 전체 클릭은 탐색 UX를 위해 HTML 링크를 허용한다.

```python
# 비로그인 nav: 홈, 로그인
# 로그인 nav:   홈, 프로젝트 제출, 내 포트폴리오, 프로필, 로그아웃
```

헤더는 `st.container(key="folio_header")`와 `.st-key-folio_header` 선택자로 스코프 지정.

---

## CSS 아키텍처

### 핵심 패턴: key 기반 스코프

`st.container(key="...")`가 생성하는 `.st-key-*` 클래스로 컨테이너를 직접 타겟팅한다. 상위 래퍼까지 매칭하는 광범위한 `:has()`는 피한다.

```python
# 코드
with st.container(border=False, key="folio_header"):
    ...

# CSS
.st-key-folio_header {
    background: #08142b;
    ...
}
```

### 현재 컨테이너 key

| key | 용도 |
|------------|------|
| `folio_header` | 헤더 컨테이너 |
| `folio_browse_panel` | 홈 탐색 패널 |
| `folio_auth_shell` | 인증 카드 전체 |
| `folio_auth_form` | 인증 폼 카드 |
| `folio_onboarding_card` | 온보딩 카드 |

### 주의사항

- `stVerticalBlockBorderWrapper` 전역 스타일은 모든 `border=True` 컨테이너에 적용되므로 직접 수정하지 않는다.
- `.stButton>button` 전역 규칙은 `styles.py`에 1개만 유지 (중복 시 충돌).
- 헤더 내 nav 버튼은 `.st-key-folio_header .stButton > button`으로 별도 오버라이드.
- 사용하지 않는 컴포넌트 선택자는 기능 변경 직후 제거하고, 중복 선언은 한 섹션에만 유지한다.

---

## Streamlit CSS 한계 (학습)

**헤더-히어로 gap 제거 불가**: `st.container(border=True)`로 만든 헤더와 다음 요소 사이에 Streamlit이 자동으로 여백을 추가함. `gap: 0 !important`, `margin-bottom: 0 !important` 등 시도했으나 완전 제거 불가.

**결론 및 새 방향**: 다크-온-다크 디자인(헤더+히어로 이음새)은 이 여백 때문에 항상 어색해 보임. **라이트 테마(흰 배경 기반)**로 전환하면 여백이 같은 색이라 눈에 띄지 않음.

**다음 세션 작업 방향**: 라이트 테마 재설계. Streamlit 자연 레이아웃(카드 기반, 일정 여백)을 활용하는 방향.

---

## 세션 / 인증 구조

```
앱 로드
  └─ EncryptedCookieManager.ready() 대기
      └─ 쿠키에서 access_token / refresh_token 복구 시도
          └─ restore_session() → Supabase
              └─ 성공: session_state에 user 저장 → st.rerun()
              └─ 실패: 쿠키 삭제
                  ├─ 공개 페이지: 비로그인 상태로 조용히 계속
                  └─ 보호 페이지: Login으로 이동해 안내 표시
```

- `get_current_user()`: `session_state["folio_user"]` 반환. 없으면 None.
- 로그아웃: `?logout=1` 쿼리 → `sign_out()` → 쿠키 삭제 → 홈 이동.
- Supabase client는 `st.cache_resource` 전역 공유가 아니라 Streamlit 세션별로 생성해 Auth 상태가 사용자 간 섞이지 않게 한다.
- 로그아웃 시 토큰과 함께 세션의 Supabase client도 폐기한다.
- 프로필 복구는 기존 프로필을 덮어쓰지 않고, 누락됐을 때만 생성한다.
- 약관·동의 조회가 실패하면 서비스를 우회시키지 않고 재시도 화면을 표시한다.

---

## Supabase 스키마 (핵심 테이블)

```sql
profiles       (id, email, name, organization, bio, created_at)
projects       (id, author_id, title, one_liner, tags[], is_public, view_count, ...)
likes          (user_id, project_id, created_at)
policy_versions (id, policy_type, version, is_active, content, effective_at)
user_policy_consents (user_id, policy_version_id, consented_at)
```

- `projects.category` 컬럼은 DB에서 제거됨 (코드에도 없음).
- 좋아요 수는 `projects` 컬럼이 아니라 `likes` 테이블에서 계산함.
- RLS 활성화 상태. anon 클라이언트로 공개 프로젝트만 읽기 가능.
- 인증 사용자는 공개 여부와 관계없이 본인이 작성한 프로젝트를 읽을 수 있다. 원격 DB에는 최신 `schema.sql` 재적용이 필요하다.

### 공개 탐색 조회

- 공개 프로젝트는 500건 단위로 전체 페이지 조회하며 원본 결과를 30초 캐시한다.
- 인기 태그는 별도 DB 요청 없이 같은 공개 프로젝트 캐시에서 계산한다.
- 공개 프로필은 60초, 프로젝트별 좋아요 수는 15초 캐시한다.
- 프로젝트 CRUD, 조회수 증가, 좋아요 변경 시 관련 캐시를 즉시 무효화한다.

### 프로젝트 작성 UX

- 프로젝트 본문 미리보기와 카드 미리보기를 제공한다.
- Quill이 섹션 제목에 HTML 속성을 추가해도 문제 정의·사용 데이터·분석 과정·핵심 인사이트를 분리한다.
- 선택 URL은 입력 위치에서 즉시 형식을 검증하고 제출 시 다시 최종 검증한다.
- 등록·수정·삭제 완료 메시지는 `session_state`에 임시 보관해 rerun 뒤에도 표시한다.

### 상세·포트폴리오 UX

- 상세 화면은 첨부 자료가 있으면 2열, 없으면 본문 전체 폭 1열로 렌더링한다.
- 상세 좋아요와 목록 복귀는 HTML 링크가 아닌 Streamlit 버튼을 사용한다.
- 내 포트폴리오는 프로젝트 정보와 관리 액션을 하나의 `border=True` 컨테이너로 묶는다.

### 테스트 범위

- `python -m unittest discover -s tests -v`
- 라우팅, 인증 클라이언트 격리, 온보딩 오류 처리, 프로필 보존
- 프로젝트 HTML 정제, 본문 섹션 파싱, URL 정규화, 태그·검색 필터
- 실제 로그인·회원가입·작성자 전용 RLS는 테스트 계정으로 별도 브라우저 검증이 필요하다.

---

## 작업 원칙

- 단순 CSS/문구 변경은 검증 생략.
- Python 구조 변경은 관련 파일만 Read 후 수정.
- Streamlit 전역 CSS 오염 주의 — 컨테이너 key 기반 스코프 우선.
- 인증 및 상태 변경 동작은 `navigate()`와 Streamlit 버튼 사용. 공개 카드 링크만 예외.
- 한글 문구: `word-break: keep-all` + 적절한 `max-width`.
- 카드 HTML을 `st.markdown()`으로 렌더링 시 들여쓰기 주의 (`clean_html()` 활용).
- 사용자 프로젝트 본문은 저장 시와 표시 시 `sanitize_project_html()`로 정제.
- 캡처 확인은 UI/UX 작업 시만. 확인 후 `artifacts/` 이미지 정리.
- 캡처 스크립트: `tools/capture_streamlit_scroll.py` (의존: selenium, Pillow → `requirements-dev.txt`).

### Streamlit UI 작업 재발 방지 원칙

상세 페이지 개선 과정에서 같은 정렬 요청을 여러 번 수정한 원인은 CSS 값보다 Streamlit의 생성 DOM 구조를 충분히 확인하지 않은 데 있었다. 이후 UI 작업은 아래 순서를 따른다.

1. **요청을 픽셀 단위 완료 조건으로 바꾼다.**
   - "크기를 통일"은 대상 요소들의 실제 `width`와 `height`가 같은 상태를 뜻한다.
   - "여백을 통일"은 비교 대상의 `getBoundingClientRect().left/right`가 같은 상태를 뜻한다.
2. **CSS를 추정해 반복 수정하지 않는다.**
   - 1차 수정이 화면과 다르면 즉시 Selenium `execute_script()`로 대상과 조상 래퍼의 좌표·계산 스타일을 측정한다.
   - 캡처 이미지만 보고 2px, 4px을 누적 보정하지 않는다.
3. **Streamlit의 실제 래퍼를 확인한다.**
   - 컬럼 test id는 `stColumn`이다. `column` 선택자는 동작하지 않는다.
   - `st.button()`은 `stElementContainer → stButton → 중간 div → stTooltipIcon → stTooltipHoverTarget → button` 구조가 될 수 있다.
   - 버튼 컬럼과 `stButton`이 100%여도 `stTooltipHoverTarget`이 내용 폭이면 실제 버튼은 축소된다. 버튼 폭 통일 시 이 래퍼까지 확인한다.
4. **HTML과 Streamlit 위젯의 렌더링 경계를 존중한다.**
   - `st.markdown()` HTML 내부에 `st.button()`을 넣을 수 없다. 히어로와 액션 컨테이너를 별도로 렌더링하고 CSS로 하나의 카드처럼 연결한다.
   - 여러 줄 HTML을 f-string에 삽입할 때 들여쓰기가 Markdown 코드 블록으로 해석될 수 있다. 공통 히어로처럼 중첩 HTML이 들어가는 마크업은 들여쓰기 없는 문자열 조합을 사용한다.
5. **스코프와 박스 모델을 먼저 고정한다.**
   - `.st-key-*` 아래로 스타일을 제한하고 `box-sizing: border-box`, `min-width: 0`, `max-width: 100%`를 먼저 확인한다.
   - iframe·링크 버튼이 카드 밖으로 나가면 자식 너비만 줄이지 말고 padding을 가진 상위 래퍼의 박스 모델을 확인한다.
6. **PC와 모바일을 모두 검증한다.**
   - PC 1440×900과 모바일 390×844 캡처를 기본 검증 크기로 사용한다.
   - 검증 후 임시 캡처는 `artifacts/`에서 삭제한다.

### 로그인 전환 시 레이아웃 플래시 방지

- 전역 CSS는 일반 본문 요소인 `st.markdown()`으로 주입하지 않는다. rerun 시 본문 DOM과 함께 스타일 노드가 교체되어 잠깐 기본 레이아웃이 노출될 수 있다.
- 현재 `apply_global_styles()`는 스타일 전용 `st.html()`을 사용한다. Streamlit 1.41에서는 style-only 콘텐츠가 메인 레이아웃이 아닌 이벤트 컨테이너에 배치되어 인증 rerun 중에도 CSS가 안정적으로 유지된다.
- CookieManager 동기화 iframe은 전역 CSS에서 계속 숨긴다. 인증 전환 중 이 iframe이 노출되면 레이아웃이 튀는 것처럼 보일 수 있다.

### 상세 페이지 현재 레이아웃 기준

- 히어로 본문과 푸터 콘텐츠의 실제 좌우 좌표가 일치해야 한다.
- 푸터 왼쪽은 `작성자 / 소속 / 등록일`, 오른쪽은 `조회수 / 좋아요 / 공개 상태` 순서다.
- 우측 세 요소는 동일 컬럼 비율이며 브라우저 실측 기준 같은 너비·38px 높이를 사용한다.
- 상세 푸터의 공개 상태는 읽기 전용이다. 공개 여부 변경은 `내 포트폴리오 → 수정 → 프로젝트 공개`에서 저장한다.
- 수정 화면의 공개 설정 카드는 폼 최하단 좌측에 두고 취소/저장 액션은 우측에 둔다.
- `목록으로 돌아가기`는 프로젝트 비주얼 카드 하단에 둔다. 비주얼 카드가 없으면 본문 하단에 둔다.
- 프로젝트 비주얼은 `대시보드`와 `첨부 자료` 사이에만 구분선을 둔다.
- 대시보드 iframe과 링크 버튼은 프로젝트 비주얼 카드 안에서 `max-width: 100%`를 유지한다.

### 인증/RLS 작업 교훈

- `session_state`에 사용자가 있다고 해서 PostgREST 요청도 인증된 것은 아니다.
- 작성자 전용 mutation 전에 `ensure_authenticated_session()`으로 세션을 갱신하고 갱신된 access token을 `client.postgrest.auth()`에 명시적으로 적용한다.
- 프로젝트 UPDATE는 `return=representation`을 사용하지 않는다. 공개→비공개 변경 직후 변경 행을 다시 SELECT해 반환하면 원격 RLS 정책과 충돌할 수 있으므로 `return=minimal`과 영향 행 count로 성공을 판정한다.
- 인증 재동기화 후에도 42501이 발생하면 로그인 오류로 오진하지 않는다. 원격 DB에 `Users can read own projects`와 `Users can update own projects` 정책이 누락된 것이므로 `supabase/fix_project_owner_rls.sql`을 SQL Editor에서 적용한다.
- 비로그인 또는 유령 세션에서 mutation을 보내 RLS 원문 오류를 노출하지 않는다. 세션을 정리하고 Login으로 이동시킨다.
- RLS 관련 변경은 단위 테스트만으로 완료로 판단하지 않고 실제 테스트 계정으로 공개↔비공개 전환을 확인한다.

---

## 최근 작업 요약

### 핵심 변경 사항
- 프로젝트 상세 히어로 푸터를 작성자·소속·등록일과 조회수·좋아요·공개 설정 구조로 재편했다.
- 조회수·좋아요·공개 설정은 동일 너비와 38px 높이로 맞췄으며, Streamlit의 `stTooltipHoverTarget` 래퍼까지 폭을 확장했다.
- 프로젝트 비주얼 카드의 iframe·링크 오버플로를 수정하고 대시보드/첨부 자료의 정보 위계를 정리했다.
- 작성자 mutation 전에 Supabase Auth 세션과 PostgREST JWT를 재동기화하도록 보강했다.
- `내 포트폴리오` 카드에서 태그 정렬 문제를 수정했고, 태그와 뷰/좋아요/공개 정보를 카드 하단 footer로 이동했다.
- `보기 / 수정 / 삭제` 버튼을 카드 오른쪽에 배치하여 관리 액션을 명확히 했다.
- `render_tag_chips()`와 `render_project_metrics()` 공통 UI 헬퍼를 분리해 재사용성을 높였다.
- 로그아웃 상태에서는 자동 로그인 복원을 중단하고, 로그인/회원가입 화면에서는 복원 실패 메시지를 숨기도록 auth 흐름을 개선했다.

### 주요 교훈
- UI 레이아웃 문제는 개별 스타일이 아니라 카드 구조 전체를 재정렬하는 것이 더 효과적일 때가 많다.
- Streamlit에서는 상태/쿼리/버튼 동작을 함께 고려해야 하며, `navigate()` 스타일의 쿼리 이동을 우선해야 한다.
- 공통 렌더링 로직 분리는 유지보수성과 일관성에 큰 도움이 된다.

## 다음 작업 우선순위

현재 MVP 핵심 기능과 단위 테스트는 구현되어 있다. 새 기능을 늘리기 전에 아래 순서로 배포 안정성을 높인다.

1. **실제 Supabase 통합 검증**
   - 테스트 계정 2개로 회원가입, 이메일 인증, 로그인 유지, 온보딩을 확인한다.
   - 프로젝트 공개/비공개 RLS와 작성자 전용 수정·삭제를 확인한다.
   - 조회수 RPC, 같은 세션의 중복 조회 방지, 좋아요 추가·취소·정렬을 확인한다.
2. **오류 처리와 운영 진단 보강**
   - 데이터가 없는 상태와 Supabase 조회 실패 상태를 화면에서 구분한다.
   - 현재 조용히 무시하는 조회수 RPC 실패를 진단할 수 있게 한다.
   - 주요 조회 화면에 재시도 흐름을 제공한다.
3. **라이트 테마 재설계**
   - 색상 토큰과 전역 배경부터 정리한 뒤 Home, 카드, 상세, 인증/관리 화면 순으로 적용한다.
   - UI 변경 후 PC·모바일 스크롤 캡처로 확인한다.
4. **프로젝트 작성 초안 보호**
   - 신규 등록과 수정 내용을 구분해 `session_state`에 임시 보존한다.
   - 등록·수정 완료 또는 명시적 취소 시 초안을 제거한다.
5. **테스트와 문서 보강**
   - CRUD, 좋아요, 조회수 실패, 쿠키 복구, 비공개 접근 흐름의 테스트를 추가한다.
   - 기능 변경 시 이 문서와 관련 체크리스트를 함께 갱신한다.
