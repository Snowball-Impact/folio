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
              └─ 실패: 쿠키 삭제, restore_failed=1 표시
```

- `get_current_user()`: `session_state["supabase_user"]` 반환. 없으면 None.
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
