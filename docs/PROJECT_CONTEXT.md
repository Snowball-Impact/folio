# FOLIO 프로젝트 컨텍스트

새 대화에서 작업을 이어갈 때 이 문서를 먼저 읽어라.
코드와 문서가 다르면 코드베이스를 확인한 뒤 이 문서를 고쳐라.
민감 정보(API 키, 비밀번호 등)는 이 문서에 기록하지 않는다.

---

## 프로젝트 개요

**FOLIO** — 공개된 우수 데이터 시각화 프로젝트를 선별해 소개하고, 사용자가 직접 경험한 뒤 의견을 나눌 수 있도록 하는 콘텐츠 기반 커뮤니티.
핵심 메시지: "좋은 데이터 시각화 프로젝트를 발견하고, 직접 경험하고, 함께 이야기하는 커뮤니티 / AI 시대에도 사람의 질문과 해석은 중요한 자산이다."

2026-08 기준 제품 방향은 `docs/MVP_PRD.md`를 기본으로 하며, 커뮤니티 게시판은 `docs/FOLIO_Community_PRD.md`, 운영자 화면은 `docs/FOLIO_Admin_PRD.md`를 따른다. 기존 코드는 아직 "사용자 직접 등록 포트폴리오 MVP" 구조가 많이 남아 있으므로, 다음 큰 작업은 기존 기능을 보존하면서 Power BI-first 콘텐츠, 데이터 시각화 갤러리 경험, 커뮤니티/운영 기능을 단계적으로 결합하는 것이다.

- **스택**: Streamlit + Supabase (PostgreSQL + Auth)
- **실행**: `streamlit run app.py` → `http://localhost:8501`
- **엔트리**: 루트 `app.py` → `folio_app/app.py:main()`
- **배포 채널**: Streamlit Community Cloud. 목적은 기존 Streamlit 앱을 유지하면서 Playwright 기반 썸네일 자동 캡처를 실험하는 것이다.

### 현재 핸드오프 상태 (2026-08-23)

다음 대화에서는 아래 상태에서 이어가면 된다.

- 마지막 원격 반영 기준 커밋은 `c336dc6 Enable Power BI first launch mode`이다.
- 현재 작업 트리에는 레퍼런스 정렬 UX 개선, 홈 히어로 설명 문구 변경, 푸터 버전 `v2026.08.23.10`, 새 PRD 문서 2개와 이 문서 갱신이 남아 있다. 커밋/푸시는 아직 하지 않았다.
- 새 PRD 문서:
  - `docs/FOLIO_Community_PRD.md`: 하나의 `커뮤니티` 게시판으로 공지/질문/팁·노하우/기타를 다룬다. 별도 Q&A/자유게시판/공지사항 화면을 만들지 않는다. MVP 댓글은 기존 프로젝트 댓글 UI/기능을 확장해 재사용하는 방향이다.
  - `docs/FOLIO_Admin_PRD.md`: `/admin` 통합 운영 화면이다. 승인·심사 시스템이 아니라 프로젝트/커뮤니티/댓글/사용자를 조회하고 필요 시 숨김/공개/삭제하는 사후 관리 도구다.
- 런칭 모드는 Power BI-first다. Tableau/Looker Studio/Streamlit 레퍼런스 분류와 수집 데이터는 유지하되, UI 노출 플랫폼은 `VISIBLE_REFERENCE_PLATFORM_KEYS = ("powerbi",)`로 제한한다.
- 홈 콘텐츠 유형 필터는 숨기고 Power BI로 고정한다. 상단 독립 `레퍼런스` 메뉴는 숨기며, Power BI 메뉴 안의 `레퍼런스` 링크와 직접 `Reference` URL은 Power BI 레퍼런스만 보여준다.
- 레퍼런스 페이지는 히어로에서 "공식" 문구를 제거했다. 정렬 옵션은 `최신`, `좋아요`, `조회수`이며 홈 갤러리 정렬 값(`최신순`, `좋아요순`, `조회수순`)을 재사용한다.
- 레퍼런스 정렬 버튼은 페이지 리로드 없이 클라이언트 JS가 이미 렌더된 카드 DOM을 `data-created-at`, `data-like-count`, `data-view-count` 기준으로 재정렬한다. URL의 `sort`는 `history.pushState`로 조용히 갱신하고, 상세 카드 링크에도 현재 정렬값을 반영한다.
- 레퍼런스의 `더 보기`는 아직 기존 Streamlit 방식이다. 하단 도달 시 `visible` query parameter를 늘리고 rerun으로 다음 묶음을 렌더링한다.
- 홈 히어로 1번 설명은 서비스 방향성에 맞춰 "FOLIO는 좋은 시각화를 발견하고, 직접 경험하며 토론하고 함께 성장하는 커뮤니티입니다."로 변경했다. 히어로 설명 문장은 쉼표 뒤에서 줄바꿈하며, 첫 줄은 짧고 아래 줄이 더 길고 무겁게 받치는 구도를 선호한다.
- 나머지 홈 히어로 설명도 같은 줄바꿈 균형을 적용했다.
- 푸터는 좌측 저작권, 중앙 앱 버전, 우측 정책 링크 묶음으로 배치한다. 버전 문자열은 `folio_app/app.py`의 `APP_VERSION`에 둔다.
- 버전 숫자는 실제 배포할 때 갱신한다. 현재 작업트리 버전은 `v2026.08.23.10`이다.
- 홈 기본 로딩 최적화를 위해 첫 화면 카드 레일은 레일당 6개만 가져와 렌더링한다. 검색/태그/플랫폼 필터를 쓰는 경우에는 기존 전체 필터 경로를 사용한다.
- 홈 인기 태그에는 플랫폼 메뉴성 태그와 레퍼런스 분류 태그를 노출하지 않는다. 제외 대상은 `Tableau`, `Power BI`, `Data Studio`, `Streamlit`, `Looker Studio`, `Other`, `reference`, `references`, `레퍼런스`, `참고` 등이다.
- 등록/수정에서 PBIX 업로드와 썸네일 자동 캡처를 함께 쓰면 PBIX 게시/배포 완료와 명시 대기 후 캡처가 실행되어야 한다. 게시 대기와 캡처 대기는 각각 진행률 메시지를 표시한다.
- 다음 작업 후보는 Power BI 콘텐츠 번역 품질 개선이다. 새 컨텍스트에서는 `docs/curation/powerbi_CONTENT_OPS.md`, `docs/curation/powerbi_*`, `folio_app/services/powerbi_content.py`, `folio_app/services/powerbi_i18n.py`, `tests/test_powerbi_content.py`와 관련 테스트를 먼저 분석하고, 바로 수정하지 말고 번역 대상/방식/우선순위 계획부터 세운다.
- 검증 완료 명령:
  - `python -m pyflakes folio_app app.py tests`
  - `python -m unittest tests.test_project_references tests.test_core_flows tests.test_ui_cards -v`
  - `python -m pyflakes folio_app\pages\home.py`

### PRD v1.5 전환 기준

- 초기 콘텐츠 범위는 Power BI Embedded 기술 검증과 Tableau/Public Streamlit/Looker Studio 중심의 공개 데이터 시각화 프로젝트다.
- 사용자의 직접 프로젝트 등록은 유지하되, Power BI 프로젝트는 Embedded Viewer와 PBIX 게시 흐름으로 단계적으로 제품화한다.
- 프로젝트 상세는 `Hero -> Project Preview -> Project Summary -> Data & Analysis -> Source & Links -> Comments` 순서를 기준으로 한다.
- 임베드 실패는 예외가 아니라 정상 상태다. `embed_supported`, `external_link_only`, `embed_failed` 상태를 모델과 UI에서 구분해야 한다.
- 도구보다 주제를 우선한다. 갤러리 필터는 주제 카테고리와 플랫폼 필터를 함께 제공한다.
- 원본 프로젝트, 원작자, 원본 플랫폼, 원본 URL, FOLIO 편집·요약 표시를 명확히 노출한다.
- 관리자 사전 승인 흐름은 만들지 않고, 부적절한 프로젝트는 사후 관리한다.
- Power BI Embed Token과 Client Secret은 서버 전용이며 DB와 클라이언트에 영구 노출하지 않는다.
- PBIX는 임시 처리 후 Power BI Import가 끝나면 삭제하고, Supabase Storage에 영구 보관하지 않는다.
- PBIX 업로드는 등록/수정 완료 버튼을 눌렀을 때 실행하며, 실패하면 프로젝트 생성/수정은 보류하고 입력 초안을 유지한다.
- PBIX 최대 파일 크기는 100MB로 제한한다.
- 수정 시 새 PBIX Import가 성공하면 기존 프로젝트 ID, 댓글, 조회수, 좋아요, 상세 URL은 유지하고 `powerbi_reports` 메타데이터만 교체한다. 실패하면 기존 Power BI 게시본은 유지한다.
- Power BI Import polling은 MVP에서 최대 100초로 제한한다.
- 프로젝트 유형 후보는 Power BI, Tableau, Looker Studio, Streamlit, Notebook, HTML Report, Markdown Report, Web/App, 기타다.
- HTML Report는 sandbox iframe으로만 표시하고, Markdown Report는 sanitize 후 렌더링한다. Notebook은 MVP에서 서버 실행/변환하지 않고 GitHub 또는 nbviewer URL 등록을 우선한다.
- GitHub 연동은 Todo로만 둔다. 초기 아이디어는 public GitHub repo/file URL 기반 README 또는 파일 감지와 폼 자동 채움이며, OAuth/GitHub App/private repo import는 MVP 제외다.
- 소셜미디어 링크와 Kaggle은 Todo로 둔다. Instagram, YouTube, Threads, Facebook, Blog, LinkedIn, X, Kaggle 등은 프로젝트 링크와 제작자 프로필 링크를 구분해 안전한 외부 URL로 표시하는 방향이다.

---

## 파일 구조 (핵심만)

```
folio_app/
  app.py                  # 진입점. 쿠키 복구, 라우팅, 온보딩 체크
  styles/                 # 전역 CSS 주입 (apply_global_styles), UI 영역별 CSS 모듈
  config.py               # 환경변수 로드 (get_settings)
  navigation.py           # 내부 이동 공통 헬퍼와 허용 라우트
  components/
    assets.py             # static 이미지 data URI 헬퍼
    dashboard.py          # 상세 대표 결과물 iframe 컴포넌트
    home_gallery.py       # 홈 카드 레일, 카드 preview script, count-up script
    layout.py             # render_header(), render_hero()
    auth_forms.py         # auth 컴포넌트 public facade
    auth_login.py         # 로그인 폼
    auth_signup.py        # 회원가입 폼
    auth_password_reset.py # 비밀번호 재설정 폼
    auth_validation.py    # 회원가입 입력/정책 검증
    analytics.py          # GA page view/event script bridge
    policy_consent.py     # 약관 동의 checkbox/링크 렌더링
    portfolio_items.py    # 마이페이지 프로젝트 관리 카드
    profile_summary.py    # 마이페이지 프로필·통계 요약 HTML
    project_body.py       # Quill 본문 편집기, 섹션 파싱, plain text 변환
    project_comments.py   # 상세 댓글·답글 UI
    project_detail_content.py # 상세 대표 결과물, 본문 섹션, 외부 링크 액션
    project_editor.py     # 등록/수정 제출 흐름
    share.py              # 공유 버튼, 상세 액션 그룹 HTML 컴포넌트
    ui.py                 # clean_html(), 공통 UI 헬퍼
    project_form.py       # 프로젝트 등록/수정 공용 입력 폼과 payload 검증
  pages/
    about.py              # 서비스 소개 페이지
    home.py               # 홈 + 탐색 허브 + 상세 뷰
    project_detail.py     # 상세 렌더링 (home에서 project_id 쿼리로 호출)
    auth.py               # render_login(), render_signup()
    gallery.py            # 레거시 → Home으로 리다이렉트
    notifications.py      # 댓글 알림 목록과 읽음 처리
    protected.py          # render_submit(), render_my_page() (프로필+포트폴리오 통합). render_my_portfolio()/render_profile()은 My Page로 리다이렉트만 하는 레거시 라우트 핸들러
    onboarding.py         # 약관 동의 온보딩
    policy.py             # 약관/개인정보 정책 본문
  services/
    auth.py               # 인증 public facade. 세션/계정/복구/비밀번호 모듈 re-export
    auth_session.py       # session_state 토큰, Supabase client binding, 로그아웃
    auth_account.py       # 회원가입, 로그인, 인증 메일 재발송
    auth_restore.py       # 쿠키 기반 세션 복구
    auth_password_reset.py # 비밀번호 재설정 요청/완료
    auth_types.py, auth_errors.py
    comments.py           # 댓글 public facade. 조회/작성/읽음/통계 모듈 re-export
    comment_queries.py    # 댓글 조회, 작성자 attach, 답글 가능 여부
    comment_mutations.py  # 댓글 작성/삭제, 알림 생성 bridge
    comment_reads.py      # 프로젝트별 댓글 읽음 상태
    comment_stats.py      # 댓글 수, 최신 댓글 시각 캐시
    comment_types.py, comment_utils.py
    profiles.py           # get_profile(), update_profile(), get_onboarding_status()
    projects.py           # 프로젝트 public facade. query/mutation/normalizer/type re-export
    project_queries.py    # 공개/작성자 목록, 검색·태그·정렬, 좋아요/작성자 attach, 캐시
    project_mutations.py  # 생성/수정/삭제, 조회수, 좋아요 mutation
    project_normalizers.py # payload, 태그, URL, Power BI iframe src 정규화
    project_types.py      # ProjectResult, ProjectServiceError, ViewCountResult
    project_drafts.py     # 사용자·작업별 세션 초안 저장·복구·삭제
    project_content.py    # 프로젝트 본문 HTML 허용 목록 정제
    notifications.py      # 댓글 알림 생성·조회·읽음 처리
    email_notifications.py # SMTP 댓글 이메일 알림
    supabase_client.py    # Streamlit 세션별 Supabase client
  static/
    hero-preview-home.jpg # 홈 히어로 전용 경량 미리보기 이미지
    gapyear-hero-banner.jpg, snowball-impact.webp, vision-snowball.webp # 서비스 소개 페이지 이미지
```

---

## 구현 완료 기능

| 기능 | 파일 | 비고 |
|------|------|------|
| 회원가입 / 이메일 인증 | `pages/auth.py`, `components/auth_signup.py`, `services/auth.py` | Supabase Auth |
| 로그인 / 로그아웃 | `pages/auth.py`, `components/auth_login.py`, `services/auth.py`, `app.py` | EncryptedCookieManager로 세션 유지 |
| 약관 동의 | `components/auth_signup.py`, `components/policy_consent.py`, `pages/onboarding.py`, `services/profiles.py` | 회원가입 폼에서 동의 수집(체크 이력을 Auth user_metadata에 저장) → 첫 로그인 시 조용히 `user_policy_consents`에 기록. 메타데이터가 없거나 기록 실패 시 온보딩 화면이 폴백으로 강제 진입 |
| 프로필 조회 / 수정 | `protected.py` | 이름, 소속, 자기소개 |
| 프로젝트 등록 / 수정 / 삭제 | `protected.py`, `project_editor.py`, `project_form.py`, `services/projects.py` | |
| 홈 탐색 (검색, 태그, 정렬) | `home.py`, `home_gallery.py` | Gallery 페이지 없음, Home이 탐색 허브 |
| 프로젝트 상세 | `project_detail.py`, `project_detail_content.py`, `project_comments.py` | `?project_id=` 쿼리로 Home 안에서 렌더링 |
| 서비스 소개 | `about.py` | 경기청년 갭이어 2026, Snowball Impact, FOLIO, VISION 소개 |
| 좋아요 | `services/projects.py`, `project_detail.py` | 비로그인 → Login으로 이동 |
| 푸터 | `app.py`, `styles/tokens.py` | 좌측 저작권, 중앙 버전, 우측 정책 링크. 버전은 배포 시점에만 갱신 |

---

## PRD v1.5 전환 갭

현재 구현은 사용자 작성 프로젝트 포트폴리오 플랫폼에 가깝고, PRD v1.5는 Power BI Embedded/PBIX 게시 제품화와 데이터 시각화 갤러리 경험을 함께 우선한다. 큰 방향은 맞지만 아래 항목은 아직 전환이 필요하다.

### 데이터 모델

현재 `projects`는 `author_id`, `one_liner`, `problem`, `dataset`, `process`, `insights`, `power_bi_url`, `report_url`, `github_url`, `thumbnail_url`, `thumbnail_mode`, `tags`, `is_public` 중심이다.

PRD v1.5 전환에 필요한 필드:

- `summary` 또는 기존 `one_liner`의 의미 재정의
- `topic_category`
- `project_format`
- `platform`
- `project_type`: `powerbi`, `tableau`, `looker`, `streamlit`, `web`, `other`
- `status`: `processing`, `published`, `failed`, `deleted`
- `creator_name`
- `creator_url`
- `source_url`
- `embed_url` 또는 기존 `power_bi_url`의 범용화
- `data_source`
- `embed_status`: `supported`, `external_only`, `failed`
- `source_type`: `curated`, `submitted`, `creator_owned`
- `published_at`
- `deleted_at`
- `powerbi_reports` 테이블: `workspace_id`, `report_id`, `dataset_id`, `embed_url`, `import_id`, `import_status`

기존 프로젝트 설명 필드(`problem`, `dataset`, `process`, `insights`)는 PRD v1.5의 상세 설명 구조와 대부분 대응된다. 다만 `process`는 "분석 및 시각화", `insights`는 "주요 관찰 포인트"로 화면 문구를 바꿔야 한다.

### 갤러리

현재 홈은 태그 중심 검색·정렬과 최근/조회/좋아요 레일을 제공한다. PRD v1.5에서는 기존 레퍼런스 갤러리를 유지하되, Power BI 프로젝트를 실제 Embedded로 체험할 수 있는 흐름이 중요하다.

우선순위:

1. 기존 태그 필터와 플랫폼 필터를 유지한다.
2. 카드에 주제 카테고리, 플랫폼, 제작자, 댓글 수, Power BI 처리 상태를 단계적으로 표시한다.
3. 레퍼런스와 사용자 직접 등록 프로젝트가 한 화면에서 혼동되지 않도록 출처와 프로젝트 유형을 명확히 표시한다.

### 상세 페이지

현재 상세는 Power BI iframe 또는 외부 링크 중심이며, 작성자 포트폴리오 맥락이 강하다. PRD v1.5 기준 상세는 Power BI Embedded Viewer, 원작자·원본 플랫폼·원본 URL, 임베드 실패 fallback이 핵심이다.

우선순위:

1. `power_bi_url` 중심 명명을 범용 `embed_url`/`source_url` 개념으로 확장한다.
2. Power BI Embedded는 서버에서 Embed Token을 동적 발급하고 클라이언트에는 secret을 노출하지 않는다.
3. `embed_status`와 `status`에 따라 iframe, Embedded Viewer, 대표 이미지 fallback, 외부 실행 버튼을 분기한다.
4. 상세 본문 섹션 제목을 문제 정의, 사용 데이터, 분석 및 시각화, 주요 관찰 포인트로 표준화한다.
5. Source & Links 섹션에 원본 프로젝트, 제작자 프로필, GitHub, 데이터 출처, 관련 보고서를 노출한다.

### 등록 흐름

현재 `Submit`은 로그인 사용자가 프로젝트를 직접 게시한다. PRD v1.5에서는 관리자 사전 승인 없이 직접 게시를 유지하되, Power BI 프로젝트는 `processing -> published/failed` 상태를 거친다.

우선순위:

1. 프로젝트 유형 선택을 추가한다.
2. 대표 썸네일 업로드를 우선 구현한다.
3. Power BI 선택 시 PBIX 업로드와 Import 상태 표시를 추가한다.
4. PBIX는 임시 처리 후 Power BI Import 성공 시 삭제하며 Supabase Storage에 영구 보관하지 않는다.

### 댓글

현재 댓글, 1단계 답글, 삭제, 알림, 이메일 알림은 구현되어 있다. PRD v1.5의 최소 커뮤니티 Gap은 "본인 댓글 수정"과 관리자 사후 삭제 정책이다.

우선순위:

1. 본인 댓글 수정 기능을 추가한다.
2. 댓글 신고와 구조화 댓글은 P1/P2로 보류한다.

### 분석 이벤트

현재 GA page view, 공유 링크 진입, 좋아요, 등록 등 일부 이벤트가 있다. PRD v1.5에서는 카드 클릭, 상세 조회, 임베드 또는 원본 실행 클릭, 댓글 작성, Power BI embed load/success/error, PBIX import success/failed가 중요하다.

우선순위:

1. 원본 실행 버튼 클릭 이벤트를 추가한다.
2. 프로젝트 카드 클릭과 상세 조회 이벤트 이름을 v1.5 지표에 맞춰 정리한다.
3. Power BI Embedded와 PBIX Import 이벤트를 추가한다.

---

## 라우팅 구조

`st.query_params["page"]` 값으로 화면 전환. 모든 페이지 이동은 `st.rerun()`.

| page 값 | 화면 | 비고 |
|---------|------|------|
| Home (기본) | 홈 + 탐색 허브 | `?project_id=` 있으면 상세 |
| About | 서비스 소개 | 공개 페이지 |
| Login | 로그인 | |
| Sign Up | 회원가입 | nav에 노출 안 됨, 링크로만 접근 |
| Submit | 프로젝트 등록 | 로그인 필요 |
| My Page | 프로필 + 내 포트폴리오 통합 | 로그인 필요 |
| My Portfolio | 레거시 | My Page로 리다이렉트 |
| Profile | 레거시 | My Page로 리다이렉트 |
| Gallery | 레거시 | Home으로 리다이렉트 |

---

## 네비게이션 구조 (중요)

**인증 상태나 데이터를 변경하는 동작에는 HTML `<a href>` 링크를 사용하지 않는다.**

이유: HTML 링크 클릭 → 브라우저 전체 리로드 → WebSocket 끊김 → `session_state` 초기화 → `get_current_user() = None` → 로그인 상태 소실.

**현재 구현**: `navigation.py`의 `navigate()`가 `st.query_params` + `st.rerun()` 패턴을 통합한다. 공개 프로젝트 카드 전체 클릭은 탐색 UX를 위해 HTML 링크를 허용한다.

```python
# 비로그인 nav: 홈 갤러리, 서비스 소개, 로그인
# 로그인 nav:   홈 갤러리, 서비스 소개, 프로젝트 등록, 마이 페이지, 로그아웃
```

헤더는 `st.container(key="folio_header")`와 `.st-key-folio_header` 선택자로 스코프 지정.

---

## CSS 아키텍처

### 파일 구조: UI 영역별 모듈 분리

`folio_app/styles.py` 단일 파일(2400줄+)이 계속 커지면서 죽은 선택자·중복 선언이 쌓였다. 이후 `folio_app/styles/` 패키지로 분리했고, 2026-08 리팩토링에서 홈 갤러리·카드 preview·상세 visual·댓글·헤더 알림처럼 화면 책임이 큰 CSS를 더 작은 영역별 모듈로 나눴다:

```
folio_app/styles/
  __init__.py          # apply_global_styles() -- 아래 모듈들의 CSS를 정해진 순서로 이어붙여 st.html() 1회 호출
  tokens.py            # :root 토큰과 앱 배경
  streamlit_overrides.py # Streamlit 공통 wrapper/사이드바/CookieManager/푸터 보정
  header.py            # 상단 헤더(브랜드, nav 버튼, 로그인 버튼, 메뉴 팝오버)
  header_notifications.py # 헤더 알림 버튼/배지
  hero.py              # 홈 히어로 + 서브페이지 공용 히어로(render_hero)
  hero_footer.py       # 상세 히어로 footer 액션 정렬
  about.py             # 서비스 소개 페이지 기본 섹션
  about_vision.py      # VISION snowball visual
  buttons_inputs.py     # 전역 버튼/입력 필드 스타일
  browse_panel.py       # 홈 탐색(검색/태그/정렬) 패널
  cards.py              # 홈 프로젝트 카드 본체
  project_card_cover.py # 자동 커버 아트
  gallery_rail.py       # 홈 카드 레일/가로 스크롤/레일 버튼
  shared.py             # folio-tags/folio-tag/folio-detail-meta/folio-muted (카드·히어로·상세 공용)
  auth.py               # 로그인/회원가입 카드
  notifications.py      # 알림 페이지
  onboarding.py         # 온보딩(약관 동의) 카드
  project_form.py        # 프로젝트 등록/수정 폼 + 공개 설정 토글
  portfolio.py           # 내 포트폴리오 카드
  detail_page.py         # 프로젝트 상세 페이지 레이아웃/본문
  detail_visual.py       # 상세 대표 결과물/iframe/외부 링크
  detail_comments.py     # 상세 댓글 UI
  profile.py             # 프로필 페이지
```

각 모듈은 `<style>` 태그 없이 순수 CSS 텍스트를 담은 `CSS` 상수만 노출한다. `__init__.py`가 고정된 순서로 이어붙여 기존과 동일하게 `st.html()`을 1회만 호출한다 (스타일 전용 콘텐츠가 이벤트 컨테이너에 배치되어 인증 rerun 중에도 CSS가 유지되는 특성은 그대로 유지됨).

**분리 시 검증 방법**: 선택자+선언을 정규화해 분리 전/후 CSS를 구조적으로 비교하는 스크립트로 전체 선택자 집합과 선언 내용이 1:1로 동일함을 확인했다(의도적으로 제거한 죽은 선택자 제외). 이 방법은 이후 CSS 파일을 다시 재구성할 때도 재사용 가능하다.

**새 섹션을 추가할 때**: 어느 화면에 속하는지 위 표에서 가장 가까운 모듈을 찾아 그 모듈의 `CSS` 상수에 추가한다. 새 화면 영역이면 새 모듈을 만들고 `__init__.py`의 `_SECTIONS` 튜플에 등록한다 (등록 순서 = 최종 CSS 내 등장 순서 = 동일 선택자·동일 명시도 충돌 시 타이브레이크 순서이므로, 특정 선택자를 다른 모듈의 규칙보다 나중에 덮어써야 한다면 순서에 유의).

**현재 구조상 facade 규칙**: `styles/__init__.py`만 CSS 모듈을 조합한다. 페이지·컴포넌트에서 개별 style module을 직접 import하지 않는다. CSS 추가는 `CSS` 상수와 `_SECTIONS` 순서를 함께 확인한다.

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
| `folio_header_brand`, `folio_header_nav` | 헤더 내부 브랜드/네비게이션 스코프 |
| `folio_hero_footer_actions` | 공용 히어로 footer 액션 영역 |
| `folio_browse_panel` | 홈 탐색 패널 |
| `folio_auth_shell` | 인증 카드 전체 |
| `folio_auth_form` | 인증 폼 카드 |
| `folio_onboarding_card` | 온보딩 카드 |
| `profile_overview`, `profile_edit_card`, `portfolio_item_<id>` | My Page 프로필/프로젝트 관리 |
| `detail_footer_row`, `detail_back_action_row` | 상세 footer 액션/복귀 버튼 행 |
| `project_detail_visual` | 상세 대표 결과물 영역 |
| `project_comments_section`, `comment_row_<kind>_<id>` | 상세 댓글 섹션/댓글 row |
| `notifications_panel`, `notification_item_<id>` | 알림 목록 |
| `<prefix>_form_section_overview/content/links` | 등록·수정 폼 섹션 |
| `<prefix>_visibility_setting` | 등록·수정 공개 설정 |

### 주의사항

- `stVerticalBlockBorderWrapper` 전역 스타일은 모든 `border=True` 컨테이너에 적용되므로 직접 수정하지 않는다.
- `.stButton>button` 전역 규칙은 `buttons_inputs.py`에 1개만 유지 (중복 시 충돌).
- 헤더 내 nav 버튼은 `.st-key-folio_header .stButton > button`으로 별도 오버라이드.
- 사용하지 않는 컴포넌트 선택자는 기능 변경 직후 제거하고, 중복 선언은 한 섹션에만 유지한다. (2026-07-06 리팩토링에서 이 원칙을 어긴 죽은 CSS ~450줄과 그 CSS만을 위해 남아있던 미사용 Python 함수 3개를 정리했다 — 아래 "최근 작업 요약" 참고.)
- 새 CSS 선택자를 추가하기 전에 그 클래스/키가 실제로 어떤 `.py` 파일에서 렌더링되는지 먼저 확인한다. 렌더링 코드가 바뀌거나 삭제됐는데 CSS만 남으면 이번처럼 다음 정리 때까지 죽은 채로 쌓인다.

---

## Streamlit CSS 한계 (학습)

헤더/네비처럼 항상 보이는 요소는 `position:absolute` + `top:50%`/`margin:auto` 수동 중앙정렬 대신 **flex/grid 네이티브 정렬(`align-items`, `justify-content`)을 먼저 시도**한다 (`min-height`만 있는 컨테이너는 `top:50%`가 조용히 static position으로 대체되어 로그인 전/후 마크업 차이에 따라 위치가 흔들렸던 사례). 현재 헤더는 이 원칙에 따라 `display:flex; flex-direction:row; align-items:center; justify-content:space-between;`로 구성되어 있다(`folio_app/styles/header.py`).

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
- 검색은 제목·한줄소개·본문(문제정의/데이터/과정/인사이트)·태그에 더해 **작성자 이름·소속·등록일**도 대상으로 한다(`_project_matches_search`). 이를 위해 `list_public_projects()`는 작성자·좋아요 정보를 먼저 붙인 뒤(`_attach_related_data`) 검색/태그로 필터링하는 순서로 동작한다(이전에는 필터링 후 붙여서 작성자 정보로 검색이 불가능했다).

### 프로젝트 작성 UX

- 기본 정보와 Home 카드 미리보기를 하나의 카드에 2열로 배치하며, 미리보기는 항상 표시하고 입력에 맞춰 갱신한다.
- 모바일에서는 기본 정보·카드 미리보기와 관련 링크 3열을 각각 1열로 전환한다.
- 프로젝트 본문 편집기 아래에 접을 수 있는 본문 미리보기를 제공한다.
- Quill이 섹션 제목에 HTML 속성을 추가해도 문제 정의·사용 데이터·분석 과정·핵심 인사이트를 분리한다.
- 선택 URL은 입력 위치에서 즉시 형식을 검증하고 제출 시 다시 최종 검증한다.
- 등록·수정·삭제 완료 메시지는 `session_state`에 임시 보관해 rerun 뒤에도 표시한다.

### 상세·포트폴리오 UX

- 상세 화면은 첨부 자료가 있으면 2열, 없으면 본문 전체 폭 1열로 렌더링한다.
- 상세 좋아요와 목록 복귀는 HTML 링크가 아닌 Streamlit 버튼을 사용한다.
- My Page는 프로필·통계와 내 프로젝트 관리 목록을 한 화면에 표시한다.
- 프로젝트 정보와 보기·수정·삭제 액션을 하나의 `border=True` 컨테이너로 묶고, 모바일에서는 액션을 카드 하단 가로 3열로 배치한다.

### 테스트 범위

- `python -m unittest discover -s tests -v`
- 라우팅, 인증 클라이언트 격리, 온보딩 오류 처리, 프로필 보존
- 프로젝트 HTML 정제, 본문 섹션 파싱, URL 정규화, 태그·검색 필터
- 실제 로그인, 신규 회원가입, 이메일 인증, 최초 온보딩, 프로젝트 CRUD, 공개→비공개 전환, 작성자 비공개 열람, 서로 다른 두 계정 간 권한 격리, 좋아요, 조회수, 댓글 알림과 이메일 알림은 배포 환경에서 검증을 완료했다. 상세 결과는 `docs/INTEGRATION_VALIDATION.md`를 참고한다.

### Streamlit Community Cloud 배포

- 현재 기본 배포 문서는 `docs/STREAMLIT_CLOUD_DEPLOYMENT.md`다.
- 배포 Main file path는 루트 `app.py`다.
- Linux 패키지는 `packages.txt`로 설치한다. 현재 자동 캡처 fallback을 위해 `chromium`이 들어 있다.
- Streamlit Cloud Secrets에는 시스템 Chromium fallback을 위해 `CHROME_BINARY_PATH=/usr/bin/chromium`을 둘 수 있다.
- `APP_URL`은 최종 `https://*.streamlit.app` 주소와 반드시 맞춰야 하며, Supabase Auth Site URL/Redirect URLs도 같은 값으로 갱신한다.
- 완전한 커스텀 도메인은 직접 연결 대신 별도 정적 호스팅의 전체 iframe shell로 우회할 수 있다. 이 경우 인증 redirect, 쿠키, iframe 정책을 실제 배포에서 확인한다.
- Community Cloud의 무료 런타임에서는 cold start, resource limit, hibernation 영향이 있을 수 있다. Chromium 자동 캡처가 불안정하면 관리자 배치 캡처 또는 별도 캡처 worker로 분리한다.

---

## 작업 원칙

- **모든 작업은 GitHub 이슈로 관리한다** (버그·기능·완료된 작업 기록 포함). 처리 흐름(분석 → 범위 확인 → 구현 → 검증 → 코멘트 → 명시적 승인 후 닫기)은 `docs/ENGINEERING_PLAYBOOK.md` 14번 섹션 참고.
- 기본 협업 스타일은 **Ponytail + Caveman**이다. 코드는 Ponytail처럼 최소 동작 변경, 기존 패턴·stdlib·native 우선, 불필요한 dependency/abstraction 제거를 기준으로 짠다. 사용자 보고는 Caveman처럼 짧게, 결론 먼저, 개조식으로, 군더더기 없이 하되 보안·검증·배포 리스크는 생략하지 않는다.
- 단순 CSS/문구 변경은 검증 생략.
- Python 구조 변경은 관련 파일만 Read 후 수정.
- Streamlit 전역 CSS 오염 주의 — 컨테이너 key 기반 스코프 우선.
- 인증 및 상태 변경 동작은 `navigate()`와 Streamlit 버튼 사용. 공개 카드 링크만 예외.
- 한글 문구: `word-break: keep-all` + 적절한 `max-width`.
- 카드 HTML을 `st.markdown()`으로 렌더링 시 들여쓰기 주의 (`clean_html()` 활용).
- 사용자 프로젝트 본문은 저장 시와 표시 시 `sanitize_project_html()`로 정제.
- 셀레니움 동적 테스트나 스크린샷 검증은 **수정사항이 크리티컬하거나 원인 파악이 어려울 때만** 한다. 원인이 명확한 단순 CSS/문구 변경은 `py_compile` + 유닛 테스트로 끝내고 브라우저 검증은 생략한다. 확인이 필요할 때도 캡처 후 `artifacts/` 임시 이미지는 정리한다.
- 같은 증상(예: 정렬/위치가 자꾸 미세하게 어긋남)이 서로 다른 수정으로 세 번 이상 재발하면, 패치를 더 쌓지 말고 **접근 방식 자체를 재검토(리팩토링)**하는 걸 먼저 고려한다. 헤더를 `position:absolute` 트릭으로 여러 번 고치다 계속 재발한 뒤 flex-row로 다시 짜서 근본 해결한 사례 참고 ("Streamlit CSS 한계" 섹션).
- 버그를 추론할 때는 앱 코드뿐 아니라 **Streamlit 프레임워크 자체의 알려진 동작/한계**도 항상 초기 가설에 넣는다 (`st.columns()`의 내부 ResizeObserver, 위젯 버전별 API 변경, 서드파티 컴포넌트 iframe 타이밍 등).
- 로그인 등 실제 인증 세션이 있어야 확인되는 UI는, 계정이 없어도 `get_current_user()`를 몽키패치해서 두 상태를 나란히 렌더링·비교할 수 있다 → `tools/probe_header_auth_states.py` 참고.
- 캡처 스크립트: `tools/capture_streamlit_scroll.py` (의존: selenium, Pillow → `requirements-dev.txt`).
- 페이지 전환 CLS 측정 스크립트: `tools/measure_transition_cls.py` (Selenium, `scrollTop`/`scrollHeight`/헤더·히어로 좌표를 시간대별로 기록).
- 인증 상태별 UI 비교 스크립트: `tools/probe_header_auth_states.py` (`get_current_user()` 몽키패치로 로그인 세션 없이 logged_in/logged_out 헤더를 나란히 렌더링).

### 작업 실행 프로토콜 (진단 → 수정 → 검증)

과거 세션에서 같은 요청을 여러 번 반복 수정한 원인은 구현 난이도보다 진단 순서가 늦었던 데 있었다. 아래를 기본 흐름으로 쓴다.

1. **완료 조건을 수정 전에 구체화한다.** "정렬을 맞춰라" → `left/right` 좌표 일치, "크기를 통일" → `width/height` 일치, "상태 변경" → 입력 상태·DB 결과·rerun 후 화면 상태를 각각 정의. 모호한 "비슷하게"를 CSS 값 추정으로 반복 보정하지 않는다.
2. **1차 수정이 화면과 다르면 즉시 실측한다.** UI는 Selenium `execute_script()`로 대상·조상 래퍼의 좌표/computed style을 확인한다 (`stColumn`이 실제 컬럼 testid, `st.button()`은 `stElementContainer → stButton → stTooltipHoverTarget → button` 구조일 수 있음에 유의). 인증은 `session_state` / Supabase Auth 세션 / PostgREST JWT를 분리해서 확인한다. 캡처 이미지만 보고 2~4px씩 누적 보정하지 않는다.
3. **관련 변경을 한 번의 응집된 패치로 처리한다.** 함수 시그니처를 바꾸면 모든 호출부·반환 데이터·테스트를 같은 차례에 검색한다. UI 요소를 이동하면 기존 로직과 죽은 CSS도 함께 제거한다.
4. **검증은 위험도에 맞게 계층화한다.** CSS 한 줄은 문법 확인, Python 흐름은 관련 테스트 + `py_compile`, 공통 서비스/인증/DB payload는 회귀 테스트 후 전체 테스트 1회. 동일한 전체 테스트·전체 캡처를 작은 수정마다 반복하지 않는다. PC 1440×900 / 모바일 390×844를 기본 검증 크기로 쓰고, 임시 캡처는 `artifacts/`에서 삭제한다.
5. **외부 적용이 필요한 순간을 일찍 알린다.** RLS/스키마/배포 설정처럼 로컬 코드만으로 끝나지 않는 작업은 즉시 구분하고, 실행 가능한 SQL/절차를 제공하되 원격 적용 전에는 "완료"라고 하지 않는다.
6. **작업 종료 시 다음 세션 진입 비용을 없앤다.** 현재 상태·남은 문제·완료 기준을 이 문서에 짧게 갱신한다.

**피해야 할 패턴**: DOM 확인 없이 padding 반복 조정 · Streamlit 내부 래퍼를 추측한 선택자 사용 · 오류 문구만 보고 인증 실패로 단정 · 함수 인자 하나만 고치고 다른 호출부 미확인 · 외부 DB 정책 미적용을 앱 코드로 우회 · 매 단계 대형 파일/전체 diff 반복 출력.

### 로그인 전환 시 레이아웃 플래시 방지

- 전역 CSS는 `st.markdown()`이 아니라 `apply_global_styles()`의 스타일 전용 `st.html()`로 주입한다 (`st.markdown()`은 rerun 시 본문 DOM과 함께 교체되어 스타일이 잠깐 빠질 수 있음). style-only 콘텐츠는 메인 레이아웃이 아닌 이벤트 컨테이너에 배치되어 인증 rerun 중에도 CSS가 안정적으로 유지된다.
- CookieManager 동기화 iframe은 전역 CSS에서 계속 숨긴다. 인증 전환 중 이 iframe이 노출되면 레이아웃이 튀는 것처럼 보일 수 있다.

### 상세 페이지 현재 레이아웃 기준

- 히어로 본문과 푸터 콘텐츠의 실제 좌우 좌표가 일치해야 한다.
- 푸터는 `작성자 / 소속 / 등록일`과 `조회수 / 공개 상태`를 하나의 정보 스트립으로 묶는다.
- 좋아요만 작은 pill 형태의 Streamlit 액션 버튼으로 유지한다.
- 상세 푸터의 공개 상태는 읽기 전용이다. 공개 여부 변경은 `마이 페이지 → 수정 → 프로젝트 공개`에서 저장한다.
- 본문은 `프로젝트 리포트` 카드 하나에 문제 정의·사용 데이터·분석 과정·핵심 인사이트를 구분선으로 연결한다.
- 수정 화면의 공개 설정 카드는 폼 최하단 좌측에 두고 취소/저장 액션은 우측에 둔다.
- `홈 갤러리로 돌아가기`는 프로젝트 비주얼 카드 하단에 둔다. 비주얼 카드가 없으면 본문 하단에 둔다.
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

### CSS 리팩토링 (2026-07-06)

`folio_app/styles.py`(2405줄) 전체를 감사해 스타일 중심으로 정리했다. 요청 계기: 파일이 계속 커지며 중복·죽은 CSS가 쌓였다.

- **버그 수정**: `/* ── Profile ──` 주석이 닫는 `*/` 없이 이어지다 우연히 `/* ── Generic card ── */`(같은 줄에 열고 닫음)에서 닫히는 바람에, 프로필 페이지가 실제로 쓰는 `.folio-profile-header`/`.folio-avatar`/`.folio-profile-info-name`/`.folio-profile-info-org`/`.folio-profile-bio`/`.st-key-profile_overview`/`st.metric` 스타일 전체가 통째로 죽어 있었다(프로필 페이지가 무스타일로 렌더링됨). 주석을 닫아 복구.
- **죽은 CSS ~450줄 제거**: 렌더링 코드가 없거나(레거시 히어로/갤러리 카드, 미사용 백링크·첨부링크 클래스), 렌더링 함수 자체가 어디서도 호출되지 않거나(`render_portfolio_card_html`, `render_gallery_card_html`, `render_placeholder_card`), 클래스명이 실제 마크업과 어긋난(`folio-visibility-pill` vs 실제 `folio-detail-visibility-stat`, `folio-detail-visibility` vs 실제 클래스 없음) 선택자들을 확인 후 제거. 검증은 각 클래스/키를 `grep`으로 모든 `.py` 파일과 대조해 실제 호출부가 있는지 하나씩 확인하는 방식으로 진행했다.
- **중복 선언 통합**: 좋아요 버튼(`st-key-detail_like_action`) 스타일이 서로 다른 3곳(구 상세 히어로, 히어로 푸터 액션, "Like button styling" 섹션)에 흩어져 있었다 — `detail_like_action`은 항상 `folio_hero_footer_actions` 안에서만 렌더링되므로, 실제 캐스케이드 결과(어느 선언이 specificity로 이겼는지)를 계산해 하나의 규칙으로 합쳤다.
- **파일 분리**: `folio_app/styles.py` → `folio_app/styles/` 패키지(화면 영역별 14개 모듈). 자세한 구조는 위 "CSS 아키텍처 → 파일 구조" 참고.
- **연쇄 Python 정리**: 위 죽은 CSS의 원인이었던 미사용 함수 3개(`render_portfolio_card_html`, `render_gallery_card_html` in `ui.py`, `render_placeholder_card` in `layout.py`)와 `render_hero()`의 미사용 `footer_html` 매개변수를 제거했다(호출부가 전혀 없음을 grep으로 확인, 테스트도 참조하지 않음).
- **검증**: 분리 전/후 CSS를 선택자+선언 단위로 정규화해 구조적으로 비교하는 스크립트로 완전히 동일함을 확인(의도적으로 제거한 항목 제외). `python -m unittest discover -s tests`(32개) 통과, 모든 페이지/컴포넌트 모듈 import 스모크 테스트 통과. 화면 동작 자체는 바꾸지 않는 리팩토링이라 브라우저 검증은 생략함 — 다음에 실제로 화면을 열 때 프로필 페이지가 정상적으로 스타일링되는지(버그 수정 확인 차원) 한 번 확인하면 좋음.
- **후속 정리 (같은 날, 서비스 레이어)**: CSS 정리와 같은 패턴(정의는 됐는데 아무도 안 부르는 함수)을 서비스 레이어에서도 스캔해 3개를 정리했다. `is_authenticated()`(`services/auth.py`), `set_project_visibility()`(`services/projects.py`)는 호출부가 없어 삭제. `count_author_stats()`(`services/projects.py`)는 정작 자기 자신은 안 쓰이면서 `protected.py`의 프로필 화면이 똑같은 통계 집계 로직을 인라인으로 중복 구현하고 있었다 — 원래 시그니처(`author_id`를 받아 내부에서 `list_projects_by_author()`를 다시 호출)대로 그냥 재사용하면 프로필 화면이 이미 가져온 목록을 두고 DB를 한 번 더 호출하게 되므로, 시그니처를 `projects: list[dict]`를 받도록 바꿔 `protected.py`가 이미 조회한 목록을 그대로 넘기게 했다(중복 호출 없이 중복 로직만 제거).
- `app.py`의 `_sync_browser_auth_storage()`에 죽은 분기가 하나 더 있었다: `cookies.get("restore_failed") == "1"` 체크와 `st.session_state.pop("folio_restore_failed", ...)` 모두, 그 값을 세팅하는 코드가 어디에도 없어 항상 거짓/no-op이었다. 삭제.

### 미해결: 로그인·서브페이지 전환 시 헤더 순간 깨짐 (관찰됨, 2026-07-06)

**증상**: 로그인하는 순간 헤더가 잠깐 깨졌다가 원상복구된다. 로그인 후 처음 서브페이지(Submit/My Portfolio/Profile 등)로 이동할 때도 한 번 더 발생한다. 그 이후로는 재발하지 않는다(같은 세션에서 다시 로그인하거나 다른 서브페이지로 이동해도 안 나타남).

**작업 가설 (미확정)**: "한 번만 발생하고 다시 안 나타난다"는 패턴은 세션(브라우저 탭)당 한 번만 초기화되는 리소스를 의심하게 한다.
- 로그인 시: `EncryptedCookieManager`가 토큰을 브라우저에 쓸 때(`cookies.save()`) 처음으로 `"CookieManager.sync_cookies.save"` 키의 커스텀 컴포넌트(별도 iframe)가 새로 마운트된다. 이 라이브러리는 `st.cache`/`key=` 기반 위젯이 아니라 `components.declare_component()`로 만든 순수 커스텀 컴포넌트라서, 우리 CSS가 의존하는 `.st-key-*` 클래스가 애초에 붙지 않는다(Streamlit 소스 확인: `.st-key-*`는 button/checkbox 등 내장 위젯 엘리먼트 코드에서만 명시적으로 부여됨). 그래서 이 iframe은 `iframe[title*="CookieManager"]` 같은 속성 기반 선택자로만 숨길 수 있는데, 이 선택자는 iframe에 해당 속성이 실제로 채워진 뒤에야 매치된다 — 최초 마운트 시 그 잠깐의 간극에서 래퍼가 잠깐 정상 크기로 보였다가(레이아웃 밀림) CSS가 따라잡으며 복구되는 것일 수 있다.
- 서브페이지 이동 시: 해당 페이지에서만 쓰는 위젯(`st.toggle`, `st.dialog`, Quill 커스텀 컴포넌트 등)이 이 세션에서 처음 마운트되며 비슷한 종류의 콜드 스타트 비용이 들 수 있다.
- 두 경우 모두, 한 번 마운트된 컴포넌트는 이후 세션 동안 그대로 남아있어 재마운트 비용이 없다 — "그 이후로는 재발하지 않음"과 부합.

**확인 안 된 것**: 위 가설은 정적 코드 분석(Streamlit 설치 패키지 소스 확인 포함)으로 도출했고, 실제 DevTools Network 탭이나 `PerformanceObserver({type:'layout-shift'})` 계측으로 실측 확인은 하지 않았다. `is_authenticated`/`set_project_visibility`/`count_author_stats`/`restore_failed` 죽은 코드 정리는 이 조사 과정에서 발견해 함께 반영했지만, 헤더 깨짐 증상 자체를 없애지는 못했을 가능성이 있다(재현 확인 필요). 확정하려면 `tools/measure_transition_cls.py` 계열 도구로 로그인 순간과 첫 서브페이지 진입 순간을 실측해야 한다.

### 완료: 페이지 전환 CLS 개선 (2026-07-06)

Streamlit 1.41.1 → 1.58.0 업그레이드로 근본 해결(`st.columns()` 내부 ResizeObserver 오버슈트가 프레임워크 차원에서 고쳐짐). 헤더도 `st.columns()`를 걷어내고 flex-row로 재구성(위 "Streamlit CSS 한계" 참고).

**남은 것**: 홈 화면 검색/태그 필터 패널 등 다른 `st.columns()` 사용처는 리사이즈 시 여전히 작은 흔들림이 있음(범위상 보류). 로그인 세션에서 메뉴 팝오버(`st.popover`) 동작 재확인 필요.

## 다음 작업 우선순위

현재 MVP 핵심 기능과 단위 테스트는 구현되어 있다. 새 기능을 늘리기 전에 아래 순서로 배포 안정성을 높인다.

1. **완료: 오류 처리와 운영 진단 보강**
   - 프로젝트 mutation·좋아요·인증·프로필·온보딩에서 공급자 예외 원문을 제거하고 서버 로그에만 남긴다.
   - 프로필 없음, 좋아요 0건, 빈 작성자 정보와 실제 조회 실패를 서비스 오류로 구분한다.
   - 마이 페이지 프로필과 상세 좋아요 상태에 재시도 흐름을 추가하고, 조회수 RPC 실패는 완료 처리하지 않는다.
   - JWT 복구 후 재실패, 로그인 프로필 복구 실패, 공급자 로그아웃 실패도 진단 로그를 남긴다.
   - 오류 처리 테스트 8개를 추가해 전체 단위 테스트 50개가 통과한다.
2. **완료: 일간 순조회수 적용**
   - ADR-012에 따른 `project_views`, RPC, 익명 방문자 쿠키와 앱 호출 로직을 로컬과 원격 Supabase에 적용했다.
   - 쿠키 유지, RPC 결과 구분, 실패 후 재시도, SQL 중복·작성자 제외 계약 테스트를 추가했다.
   - 실제 anon 호출, 하드 리로드, 작성자 본인 열람 제외와 직접 테이블 접근 차단을 검증했다.
   - 기존 조회수와 검증 기록을 초기화하고 새 정책 기준으로 집계를 시작했다. 상세 결과는 `docs/INTEGRATION_VALIDATION.md`를 참고한다.
3. **미검증 인증 흐름 확인**
   - 별도 테스트 계정 사용 승인 후 회원가입, 이메일 인증, 최초 온보딩을 확인한다.
   - 서로 다른 두 계정 사이의 작성자 전용 수정·삭제 RLS를 확인한다.
4. **완료: 프로젝트 작성 초안 보호**
   - 신규 등록과 프로젝트별 수정 초안을 사용자 ID와 작업 ID로 분리해 `session_state`에 임시 보존한다.
   - 일반 입력과 Quill 본문 반환값을 매 rerun마다 함께 저장하고 폼 재진입 시 복구한다.
   - 등록·수정 성공, 수정 취소, `초안 지우기`에서 초안과 관련 위젯 상태를 제거한다.
   - 위젯 상태 삭제는 다음 rerun의 렌더 전에 수행해 Streamlit 상태 변경 제약을 피한다.
   - 초안 격리·복구·삭제 테스트 6개를 추가해 전체 단위 테스트 56개가 통과한다.
5. **테스트와 문서 보강**
   - CRUD, 좋아요, 조회수 실패, 쿠키 복구, 비공개 접근 흐름의 테스트를 추가한다.
   - 기능 변경 시 이 문서와 관련 체크리스트를 함께 갱신한다.

### 개발 서버 파일 감시 설정 (2026-07-26)

`.streamlit/config.toml`은 개발 편의를 위해 `fileWatcherType = "auto"`와 `runOnSave = true`를 사용한다. Streamlit 1.58.0/Windows 환경에서 자동 reload가 동작하므로 CSS·문구 수정은 서버를 매번 재시작하지 않고 확인할 수 있다.

다만 과거에는 자동 reload 중 오래된 Uvicorn 프로세스가 8501 포트를 계속 잡아 최신 코드가 가려지는 혼선이 있었다. 반영이 이상하면 먼저 `netstat -ano -p tcp`로 `0.0.0.0:8501` 리스너가 하나인지 확인하고, 필요하면 서버를 재시작한다.

### 완료: GitHub QA 이슈 172/174 대응 (2026-07-07)

회원가입 화면의 필수 입력 라벨에 `*`를 표시했다. `소속`은 필수 입력으로 유지하되 placeholder에 `개인, 학원, 교육과정, 학교, 기관, 회사명` 예시를 추가했다. `회원가입` 버튼은 Streamlit 텍스트 입력 rerun 타이밍 때문에 비활성 상태가 늦게 풀리는 UX가 있어 항상 누를 수 있게 두고, 제출 시 이메일/비밀번호/비밀번호 확인/이름/소속을 검증한다. `profiles` 기준 가입 여부 조회가 실패하면 미가입으로 간주하지 않고 가입 진행을 막는다. Supabase Auth가 기존 이메일을 `user.identities == []` 형태의 성공 응답처럼 돌려주는 경우도 "이미 가입된 이메일"로 차단한다. `인증 메일 다시 받기` 영역과 `이미 계정이 있다면 로그인하기` 버튼은 상시 노출하지 않고 가입 성공 후 또는 이미 가입된 이메일을 입력/제출했을 때의 맥락에 맞춰 표시한다. Supabase Auth는 보안상 기존 이메일에도 성공처럼 응답할 수 있으므로 재발송 성공 문구는 "발송 완료"가 아니라 "요청 처리"로 표현한다. 관련 단위 테스트와 `docs/SUPABASE_SETUP.md`를 갱신했다.

### 완료: 코덱스 UI/UX 리뷰 대응 (2026-07-07)

이전 세션에서 코덱스에게 요청한 전반적 UI/UX 검토(PC·모바일, 로그인 상태) 결과를 코드로 하나씩 대조 검증한 뒤 세 가지를 수정했다.

- **Primary 버튼이 흰색으로 보이던 문제**: `project_form.py`의 등록 버튼은 이미 `type="primary"`였지만, `styles/buttons_inputs.py`의 전역 `.stButton > button` 규칙이 `kind` 속성 구분 없이 모든 버튼에 흰 배경을 강제해 무시되고 있었다. `[kind="primary"]` 전용 규칙(파란 배경, 흰 글자, hover 진한 파랑)을 추가해 해결.
- **모바일 Submit 폼이 2/3열을 유지해 입력창이 잘리던 문제**: `render_project_form()`은 PC 기준으로만 설계돼 `st.columns(2)`(기본정보/미리보기), `st.columns(3)`(BI/GitHub/ETC URL)을 그대로 쓰고, 기존 `@media (max-width: 860px)` 블록은 여백만 조정할 뿐 컬럼을 쌓지 않았다. `styles/project_form.py`의 반응형 블록에 `[data-testid="stHorizontalBlock"] { flex-direction: column }` + `[data-testid="stColumn"] { width: 100% }`를 추가해 모바일에서 1열로 전환.
- **모바일 마이페이지 보기/수정/삭제 버튼이 세로로 좁아 글자가 꺾이던 문제**: `protected.py`가 `st.columns([5, 1])`로 프로젝트 정보:액션을 나눠, 좁은 1/6 칸에 버튼 3개가 세로로 쌓이는 구조였다. `styles/portfolio.py`에 모바일 전용 규칙을 추가해 액션 컬럼을 프로젝트 정보 아래로 내리고(`flex-direction: column`), 그 안의 버튼 3개는 `display:flex; flex-direction:row`로 가로 배치.

검증은 `tools/probe_header_auth_states.py`와 같은 패턴으로 `get_current_user()`/`list_projects_by_author()`/`get_profile()`을 몽고패치하는 임시 스크립트를 만들어 실제 로그인 없이 Submit/My Page를 렌더링하고, Selenium으로 모바일 390×844 뷰포트를 캡처해 확인했다(임시 스크립트와 캡처 이미지는 확인 후 삭제). `python -m unittest discover -s tests`(32개) 통과.

**후속 (같은 날)**: 코덱스가 중간 우선순위로 지적한 "회원가입 화면에 로그인 전환 링크 없음"을 확인하는 과정에서, `WIREFRAME.MD`에 "회원가입 페이지 하단에는 로그인 전환 링크를 두지 않는다"가 의도된 규칙으로 명시돼 있는 걸 발견했다. 사용자에게 확인한 결과 해당 규칙은 폐기하되, 로그인 전환 버튼은 상시 노출하지 않고 이미 가입된 이메일로 판단되는 맥락에서만 보여주기로 했다.

같은 확인 과정에서 문서 드리프트도 발견해 정리했다: `My Portfolio`/`Profile`은 코드상 이미 `My Page`로 통합됐고(`protected.py`의 `render_my_portfolio()`/`render_profile()`은 `navigate("My Page")`만 호출) 헤더 nav도 "마이 페이지" 하나뿐인데, `WIREFRAME.MD`·`PROJECT_CONTEXT.md`(이 문서)·`README.md`가 전부 예전 2-페이지 구조로 남아 있었다. 라우팅 표, nav 설명, 파일 역할 설명을 현재 코드 기준으로 갱신했다. `README.md`의 `folio_app/styles.py`(2026-07-06에 이미 패키지로 분리됨) 참조도 함께 바로잡았다.

남은 것: 모바일 상세 Power BI 임베드가 다소 무겁다는 지적은 아직 미착수.

### 종료: 라이트 테마 재설계 (2026-07-06, 재검토 후 대부분 이미 완료 상태로 확인)

이 항목은 원래 "다크 헤더 + 다크 히어로 이음새 gap이 어색하다"는 이유로 우선순위에 있었다. 재검토 결과 이미 실질적으로 해결되어 있었다: `render_hero()`의 `dark=True` 옵션(→ `.folio-page-hero-dark`)을 실제로 넘기는 호출부가 코드 어디에도 없어서, Home·Submit·My Portfolio·Profile·상세 페이지의 히어로는 전부 흰 배경(`--folio-surface`)이었다. 남는 다크 요소는 헤더(sticky, 둥근 카드)와 로그인/회원가입 카드 상단 배너뿐이고, 둘 다 페이지 배경에 바로 이어붙는 형태가 아니라 독립된 카드라서 애초에 우려했던 "이음새" 문제가 발생하지 않는 구조다. 죽은 `dark` 매개변수와 `.folio-page-hero-dark` CSS(+반응형 규칙)를 제거했다. 헤더/로그인 배너까지 라이트로 바꾸는 건 순수 취향 문제로 남겨두고, 이 우선순위 항목 자체는 닫는다.

### 완료: GitHub 이슈 #176 약관 동의 시점 개선 (2026-07-07)

"이메일 인증 후에야 약관 동의를 받는 게 어색하다"는 QA 피드백에 대응했다. 기존에는 회원가입 → 이메일 인증 → 첫 로그인 후 온보딩 화면에서 강제로 약관 동의를 받았는데, 그 사이에 "회원가입이 완료되었습니다" 메시지가 먼저 노출돼 순서가 어색했다.

- **회원가입 폼에 필수 동의 체크박스 추가**: `auth.py`의 `render_signup()`이 `get_required_policy_versions()`로 활성 정책을 가져와 `components/policy_consent.py`의 공용 `render_policy_agreement_fields()`로 렌더링한다. 제출 시 모든 필수 정책에 동의했는지 검증한다.
- **동의 이력은 가입 시점에 Auth user_metadata로만 저장**: 이메일 인증 전에는 세션이 없어 RLS(`auth.uid() = user_id`) 때문에 `user_policy_consents`에 바로 insert할 수 없다. 대신 `sign_up()`이 동의한 `policy_version_id` 목록을 Supabase Auth의 `options.data`(`consented_policy_version_ids`)에 저장해두고, 이후 `sign_in()`/`restore_session()`에서 인증된 세션이 생기는 즉시 `complete_onboarding()`으로 조용히 커밋한다(이미 기록된 정책은 건너뜀). 이 조용한 커밋이 실패해도 로그인 자체는 막지 않고 로그만 남긴다.
- **온보딩 화면은 폴백으로 유지**: 위 과정이 어떤 이유로든 완료되지 못한 계정(가입 폼 정책 조회 실패, 메타데이터 유실 등)은 `app.py`의 기존 `get_onboarding_status()` 체크에 걸려 여전히 온보딩 화면으로 안내된다. 온보딩 화면 자체 로직은 바뀌지 않았고, 체크박스 렌더링만 `policy_consent.py`로 공용화했다.
- 스크린샷의 온보딩 카드 상단 헤딩("서비스 이용을 시작하기 전")이 2열 그리드 히어로 레이아웃의 왼쪽 컬럼에 치우쳐 보이던 것도 함께 고쳤다. `.folio-onboarding-hero`에 `grid-template-columns: 1fr`과 `text-align: center`를 추가해 단일 컬럼 중앙 정렬로 전환했다.
- 검증: `py_compile` + 단위 테스트 67개 전체 통과. 실제 이메일 인증 흐름을 포함한 브라우저 검증은 아직 하지 않았다 — 다음에 실제 신규 계정으로 가입~로그인까지 확인 필요.

### 완료: GitHub 이슈 #178 GA(Google Analytics) 연동 (2026-07-07)

Streamlit은 `st.markdown()`/`st.html()`로 넣은 `<script>`를 보안상 실행하지 않아 GA 태그를 일반적인 방식으로 넣을 수 없다. `folio_app/components/analytics.py`가 `streamlit.components.v1.html()`로 만든 iframe 안 스크립트로 `window.parent.document`(같은 출처라 접근 가능)에 직접 태그를 심는 우회 방식을 쓴다.

- `render_google_analytics(measurement_id)`: `app.py`의 `main()`에서 1회 호출. `GA_MEASUREMENT_ID`가 비어 있으면 아무 것도 하지 않는다(로컬 `.env`에는 값을 넣지 않아 로컬 트래픽이 운영 통계에 안 섞이게 함). 중복 삽입 방지를 위해 `document.getElementById` 가드가 있다.
- `track_page_view(title, path)` / `track_event(name, params)`: 이미 심어진 `gtag`를 호출하는 헬퍼. `window.parent.gtag`가 없으면(즉 GA 미설정 로컬 환경) 조용히 no-op.
- Streamlit은 `navigate()`가 `st.query_params` + `st.rerun()`으로 화면을 바꿀 뿐 실제 브라우저 탐색이 없어 GA가 화면 전환을 자동으로 못 잡는다. 그래서 `app.py`의 페이지 디스패치 지점(`page_handlers.get(selected_page, home.render)()` 직전)과 온보딩 분기에서 `track_page_view()`를 호출해 가상 페이지뷰를 수동으로 보낸다. `Home`에 `project_id` 쿼리가 있으면 "Project Detail"로 레이블링한다.
- 핵심 전환 이벤트도 추가: 회원가입 성공(`sign_up`, `auth.py`), 로그인 성공(`login`, `auth.py`), 프로젝트 등록 성공(`project_submit`, `protected.py`), 프로젝트 상세 조회(`view_item`, `project_detail.py`), 좋아요/좋아요 취소(`like`/`unlike`, `project_detail.py`), 검색 실행(`search`, `home.py`).
- 외부 링크 클릭(Power BI/GitHub/리포트, `st.link_button`으로 렌더링되는 실제 `<a>` 태그)은 별도 코드를 추가하지 않았다 — GA4의 기본 활성화된 "향상된 측정 → 아웃바운드 클릭"이 도메인이 다른 링크 클릭을 자동으로 잡아주므로 중복 계측을 피하기 위해 커스텀 이벤트를 넣지 않았다. GA4 속성에서 이 설정이 꺼져 있지 않은지만 확인하면 된다.
- **알려진 한계**: `login`/`project_submit`/`like`처럼 이벤트 발생 직후 `navigate()`나 `st.rerun()`이 바로 실행되는 지점은, 이벤트 스크립트가 브라우저에 전달되어 실행되는 시점과 rerun으로 DOM이 교체되는 시점의 경합(race)이 이론상 있을 수 있다. 스크립트는 마운트되는 즉시 동기적으로 실행되므로 실전에서는 대체로 문제없지만, 100% 보장되는 구조는 아니다.
- 검증: `py_compile` + 단위 테스트(신규 5개 포함) 77개 전체 통과. GA 실시간 리포트로 실제 이벤트 수신 여부는 아직 확인하지 않았다.

### 완료: 백로그 1차 대응과 홈/상세 UX 정리 (2026-07-26)

브랜치 `feature/backlog-1-password-reset`에서 기능정의서 기반 백로그 이슈를 만들고, 배포 전 개발 브랜치로 계속 진행하기로 했다. 사용자가 "커밋"만 요청하면 로컬 커밋까지만 수행하고, 푸시는 별도 요청이 있을 때만 한다.

- **#183 비밀번호 찾기/재설정**: Supabase recovery 링크의 `token_hash`/`code`/access token 흐름을 처리하고 새 비밀번호 입력 화면으로 리다이렉트되게 했다. 동일 비밀번호 등 실패 후 재시도할 수 있도록 reset session을 보존했다.
- **#184 헤더 네비게이션**: Streamlit popover형 메뉴 대신 헤더 우측 정렬 nav를 노출했다. 홈 메뉴 라벨은 `홈 갤러리`로 통일했다.
- **#185 홈 히어로 CTA**: 1차 히어로에 `내 분석 프로젝트 등록하기` CTA를 추가하고, 로그인 여부에 따라 Submit/Login으로 이동하게 했다.
- **#191 서비스 설명 슬라이드**: 홈 히어로를 2장 자동 롤링 구조로 바꿨다. 2번째 슬라이드는 `Collective Insight`, `인사이트는 공유할수록 깊어집니다.` 메시지와 `공유 -> 피드백 -> 발전` 도식으로 구성했다. 두 슬라이드 모두 같은 `eyebrow -> h1 -> body -> CTA` 구조를 사용한다.
- **#188 글쓰기 템플릿 구조화**: 프로젝트 본문 에디터 기본값에 `문제 정의`, `사용 데이터`, `분석 과정`, `핵심 인사이트`별 문장 뼈대와 예시를 넣었다. 예시는 Quill 색상 포맷에 맞춰 `span style="color: rgb(138, 152, 173);"`로 연한 회색 처리했다.
- **#187 공유 링크 복사**: 프로젝트 상세 히어로 액션 영역에 `링크 복사` 버튼을 추가했다. 복사 URL은 `/?page=Home&project_id={id}&utm_source=folio&utm_medium=share&utm_campaign=project_share` canonical 형태이며, 공유 링크 진입 시 `project_share_open` GA 이벤트를 세션당 프로젝트별 1회 전송한다. 추가 트래킹 결정은 GitHub 이슈 #187 코멘트에 기록했다.
- **홈/서브페이지 여백 정리**: 홈 갤러리와 서브페이지 히어로의 헤더 간격을 맞췄고, 프로젝트 탐색 패널과 카드 그리드 사이 여백은 절반 수준으로 줄였다. 히어로 카피 영역은 flex column + `gap`으로 간격을 직접 제어한다.

검증은 변경 위험도에 맞춰 수행했다. 공유 링크와 GA 진입 이벤트는 `tests.test_core_flows` 18개 통과, 글쓰기 템플릿은 관련 테스트 통과, 단순 카피/CSS 조정은 `ast.parse` 문법 확인으로 마무리했다. 전체 브라우저 캡처는 사용자가 단순 수정에서는 생략해도 된다고 한 기준에 따라 수행하지 않았다.

남은 백로그 중 비교적 큰 작업은 #189 댓글 기능 1차 구현, #186 썸네일/갤러리 UIUX, #190 이벤트 알림 목록이다. 콘텐츠가 100개 이상 등록된 상태라 갤러리 UIUX는 마지막에 크게 잡기로 했다.

### 계획 변경: 프로젝트 범위 확대와 댓글 MVP 단순화 (2026-08-01)

기획 범위는 데이터 분석 프로젝트 전용에서 데이터·AI·웹 앱 등 디지털 프로젝트 전반으로 확대한다. 데이터 분석은 초기 강점과 진입 시장으로 유지하되, 프로젝트 유형은 대시보드, AI 실험, 웹 앱, 자동화, 서비스 기획 산출물까지 포괄한다. 이 내용은 현재 `docs/MVP_PRD.md`에 통합되어 있고, 당시 기준 PRD는 `docs/legacy/PRD.md`에 보존했다.

#189 댓글 기능은 구조화 피드백 질문·유형·알림까지 한 번에 구현하지 않고, 먼저 단순 댓글과 1단계 대댓글로 실증한다. 1차 포함 범위는 댓글 작성·조회·삭제, 대댓글 작성, 작성자 배지, 댓글 수 표시다. 댓글 수정, 피드백 유형, 작성자 질문, 알림, 관리자 댓글 관리는 실제 사용 반응 확인 후 후속 이슈로 분리한다.

### 완료: 홈 갤러리·상세·등록·마이페이지 UI 정리 (2026-08-01)

FOLIO의 주요 사용자 화면을 홈 갤러리 기준의 차분한 라이트 UI로 맞췄다. 사용자는 장식적인 컴포넌트보다 필요한 정보만 정돈된 화면을 선호한다. 앞으로 새 화면을 만들 때도 과한 카드 중첩, 설명성 UI, 불필요한 장식보다 정보 위계와 정렬을 우선한다.

- **홈 갤러리**
  - 프로젝트 목록은 최근 등록순, 조회순, 좋아요순 3개 카드 레일 구조를 유지한다.
  - 카드 hover iframe preview는 사용하지 않는다.
  - hover는 홈/레퍼런스 카드에서 약한 상승감과 5px 파란 테두리만 사용한다.
  - 카드 썸네일은 16:9를 유지하고, 자동 커버는 24종 색/패턴 베리에이션을 사용한다. 너무 알록달록하거나 어두운 팔레트는 피하고, 원래의 선명한 미디어 타일 느낌을 기준으로 둔다.
- **프로젝트 상세**
  - 히어로 썸네일은 16:9로 고정한다.
  - 조회수, 댓글 수, 공개 상태, 링크 복사는 `components/share.py`의 `project_action_group_html()`이 일반 HTML로 렌더링한다. 보이는 액션 UI를 custom component iframe 안에 넣지 않는다. 링크 복사 동작만 0 크기 iframe script bridge(`render_project_share_handler()`)로 붙인다.
  - 상세 히어로 footer는 `st.container(horizontal=True, key="detail_footer_row")` 한 줄 구조다. 메타 영역이 `flex: 1`로 남은 폭을 먹고, 조회/댓글/공개/링크복사/좋아요가 오른쪽 끝에 붙는다. 실제 DOM에서는 `.st-key-detail_footer_row`와 `[data-testid="stHorizontalBlock"]`가 같은 노드에 붙으므로 selector는 `.st-key-detail_footer_row[data-testid="stHorizontalBlock"]` 형태여야 한다.
  - 대표 결과물 섹션의 설명 문구를 제거하고, 대시보드/보고서/GitHub 링크는 결과물 하단 액션으로 단순화한다.
  - 리포트 본문 앞에 하드코딩된 `01 문제 정의` 같은 제목은 붙이지 않는다. 에디터에서 넘어온 본문만 출력한다.
- **프로젝트 등록**
  - 네비게이션 라벨은 `프로젝트 등록`을 사용한다.
  - 섹션 제목은 왼쪽, 설명은 오른쪽에 한 행으로 배치하고 모바일에서는 세로로 쌓는다.
  - 카드 미리보기 설명은 제거하고, 실제 홈 카드에서 보일 내용만 확인하게 한다.
  - 프로젝트명은 48자, 한 줄 소개는 56자, 태그는 최대 5개 기준으로 제한한다. 제목/소개 입력에는 카드 노출 기준 툴팁을 둔다.
- **마이페이지**
  - 프로필 영역은 중앙 정렬한다.
  - 작성자, 소속, 이메일 값은 20px로 키워 가독성을 확보한다.
  - 프로젝트 목록은 `내 프로젝트` 중심으로 간결하게 정리한다.
- **히어로 통일**
  - 홈 갤러리, 프로젝트 등록, 마이페이지 히어로는 홈 화면의 여백과 카피 구조를 기준으로 맞춘다.
  - CTA가 없는 서브페이지는 보이지 않는 CTA 높이 스페이서를 사용해 홈 히어로와 시각 기준선을 맞춘다. 이 방식은 향후 더 좋은 공통 hero API로 정리할 수 있다.
  - 홈 히어로 CTA는 로그인 새 창이 아니라 현재 창에서 `?page=Submit`으로 이동한다.
  - 홈 히어로 첫 번째 이미지는 `hero-preview-home.jpg` 경량 이미지를 사용한다. 리팩토링 후 조각 HTML을 합치는 구조에서는 여러 줄 `<img>` 태그가 Markdown에서 raw text처럼 보일 수 있으므로, 최종 이미지 태그는 한 줄 HTML로 조합한다.

### 완료: 서비스 소개 페이지와 UI 리팩토링 후속 안정화 (2026-08-01)

- **서비스 소개 페이지**
  - `About` 라우트와 헤더 nav를 추가했다.
  - 페이지 순서는 히어로(경기청년 갭이어 이미지/캡션) → Snowball Impact 팀 소개 → FOLIO 서비스 소개 → VISION으로 구성한다.
  - 경기천년체는 가독성 문제로 사용하지 않는다. 경기청년 갭이어 2026 지원 사실은 문구와 이미지로 설명하되, 과한 배지/태그형 장식은 쓰지 않는다.
- **컴포넌트 분리**
  - static 이미지 인코딩은 `components/assets.py`로 모았다.
  - 공유 버튼/상세 액션 그룹은 `components/share.py`로 분리했다.
  - Power BI 임베드는 `components/dashboard.py`로 분리했다.
  - 상세 리포트 섹션, visual context, 홈 레일 spec처럼 테스트 가능한 순수 helper를 늘렸다.
- **후속 안정화**
  - 중복 Streamlit 서버가 8501 포트에 여러 개 떠 있으면 최신 코드/세션/네트워크 상태가 꼬일 수 있다. 공개 프로젝트가 안 보이거나 수정 반영이 이상하면 먼저 `netstat -ano | Select-String ":8501"`로 리스너 수를 확인한다.
  - 홈 히어로 이미지는 리팩토링 후 태그가 노출된 적이 있으므로, 조각 HTML을 바꾸면 최종 문자열에 `raw_img_multiline` 형태가 남지 않는지 확인한다.
  - 상세 히어로 footer의 보이는 액션 UI는 iframe에 넣지 않는다. 조회/댓글/공개/링크복사 HTML과 좋아요 Streamlit button을 같은 horizontal container의 sibling으로 두고, 복사 script만 0 크기 iframe으로 둔다. DOM selector는 반드시 Selenium/브라우저 계측으로 실제 매치 여부를 확인한다.

관련 이슈와 커밋:

- #185 메인 히어로 CTA 추가: 완료 처리.
- #186 프로젝트 썸네일에 결과물 미리보기 적용: 완료 처리.
- 로컬 커밋: `65199cd Polish gallery detail form and profile UI`.

검증:

- `python -m compileall -q app.py folio_app tests`
- `python -m unittest tests.test_core_flows tests.test_project_form tests.test_ui_cards tests.test_view_count -v`

### 완료: GitHub 이슈 #189 댓글 기능 1차 구현 (2026-08-02)

#189는 단순 댓글과 1단계 대댓글 MVP로 마무리했다. 포함 범위는 다음과 같다.

- `supabase/schema.sql`에 `comments` 테이블, 인덱스, grant, RLS, 1단계 대댓글 검증 trigger를 추가했다. 공개 프로젝트 댓글은 공개 조회 가능하고, 비공개 프로젝트 댓글은 프로젝트 작성자만 조회할 수 있다. 댓글 작성은 로그인 사용자 본인 `author_id`로만 가능하며, 답글은 같은 프로젝트의 최상위 댓글에만 달 수 있다.
- `folio_app/services/comments.py`를 추가해 댓글 조회, 작성, 삭제, 트리 구성, 프로젝트별 댓글 수 집계를 분리했다. 작성/삭제 전에는 `ensure_authenticated_session()`으로 인증 세션을 재확인한다.
- `services.projects._attach_related_data()`가 좋아요 수와 함께 `comment_count`를 붙인다. 댓글 작성/삭제 시 댓글 수 캐시를 비운다.
- 홈 프로젝트 카드와 상세 히어로 액션 그룹에 댓글 수를 표시한다.
- 프로젝트 상세 하단에 댓글 섹션을 렌더링한다. 비로그인 사용자는 조회만 가능하고 로그인 CTA를 본다. 로그인 사용자는 댓글과 최상위 댓글에 대한 1단계 답글을 작성할 수 있으며, 본인 댓글만 삭제 버튼이 보인다. 프로젝트 작성자의 댓글에는 `작성자` 배지를 표시한다. 댓글 목록은 루트 댓글 기준 20개 단위 페이지네이션을 사용하고, 한 페이지뿐이어도 중앙에 페이지 번호를 표시한다.
- 댓글/답글 입력 버튼은 항상 활성 상태로 두고, 빈 입력과 인증 오류는 댓글 영역 안에서 안내한다.
- 마이페이지 프로젝트 카드에는 공통 메트릭 컴포넌트를 통해 댓글 수가 함께 표시된다.
- 댓글 기획서는 `docs/COMMENT_FEATURE_PLAN.md`에 별도로 기록했다.
- 상세 히어로 footer 정렬 문제를 여러 번 반복 수정한 뒤 실제 Selenium DOM 계측으로 원인을 확인했다. 핵심 원인은 selector 오해였다: `st.container(horizontal=True, key="detail_footer_row")`는 `.st-key-detail_footer_row`와 `[data-testid="stHorizontalBlock"]`가 같은 DOM 노드에 붙는다. descendant selector(`.st-key-detail_footer_row [data-testid="stHorizontalBlock"]`)는 매치되지 않아 메타 영역 `flex: 1`이 적용되지 않았고, 숨은 복사 handler wrapper가 남은 폭을 먹었다. 현재는 compound selector(`.st-key-detail_footer_row[data-testid="stHorizontalBlock"]`)와 0 크기 iframe wrapper 처리로 해결했다. 같은 UI 문제가 두 번 이상 재발하면 다음 패치 전에 반드시 DOM 좌표와 computed style을 측정한다.

로컬 검증:

- `python -m unittest tests.test_comments tests.test_ui_cards tests.test_detail_components -v`
- `python -m compileall -q app.py folio_app tests`
- `python -m pyflakes folio_app app.py`
- `python -m unittest discover -s tests -v`

로컬 밖에서 남은 것:

- 원격 Supabase에 `supabase/schema.sql` 재적용 필요.
- 실제 계정으로 공개 프로젝트 댓글 조회/작성/삭제, 비공개 프로젝트 작성자 조회, 다른 사용자 권한 차단을 브라우저에서 검증해야 한다.

### 완료: 미확인 댓글 NEW 배지 (2026-08-02)

알림 목록을 만들지 않고, 마이페이지에서 안 본 댓글이 있는 프로젝트만 가볍게 표시하는 1.5차 범위로 구현했다.

- `supabase/schema.sql`에 `project_comment_reads` 테이블과 RLS를 추가했다. 프로젝트 작성자만 자신의 프로젝트에 대한 읽음 상태를 조회·생성·갱신할 수 있다.
- `folio_app/services/comments.py`에 `get_unread_comment_project_ids()`, `annotate_unread_comment_status()`, `mark_project_comments_read()`를 추가했다.
- 미확인 기준은 “프로젝트 작성자가 아닌 사용자가 남긴 최신 댓글이 `last_read_at`보다 최신인 경우”다. 작성자 본인이 남긴 댓글은 `NEW` 기준에서 제외한다.
- 마이페이지 내 프로젝트 카드는 `has_unread_comments`가 있으면 제목 옆에 작은 `NEW` 배지를 표시한다.
- 프로젝트 작성자가 상세 댓글 섹션을 보면 `project_comment_reads.last_read_at`을 upsert해 확인 처리한다.

검증:

- `python -m pyflakes folio_app app.py`
- `python -m compileall -q app.py folio_app tests`
- `python -m unittest tests.test_comments tests.test_ui_cards -v`

### 완료: 댓글 알림 1차 구현 (2026-08-02)

댓글 알림은 마이페이지 `NEW` 배지와 별도의 알림 도메인으로 구현한다. 1차 범위는 프로젝트 댓글 알림만 포함한다.

- `supabase/schema.sql`에 `notifications` 테이블과 RLS를 추가했다. 사용자는 자신의 알림만 조회·갱신할 수 있고, 댓글 작성자는 자신이 작성한 댓글에 대해 프로젝트 작성자에게만 `project_comment` 알림을 생성할 수 있다.
- `folio_app/services/notifications.py`를 추가해 댓글 알림 생성, 목록 조회, 미확인 알림 수 집계, 개별/전체 읽음 처리를 분리했다. 댓글 알림 생성은 서버 내부 작업이므로 `SUPABASE_SERVICE_ROLE_KEY`가 있으면 service role 클라이언트를 우선 사용한다.
- `comments.create_comment()`은 댓글 insert 성공 후 프로젝트 작성자에게 알림 생성을 시도한다. 알림 생성 실패가 댓글 작성 성공을 되돌리지는 않는다.
- 로그인 사용자 헤더에 종 아이콘 알림 버튼을 추가했다. 읽지 않은 알림이 있으면 버튼 우상단에 빨간 `N` 배지를 표시한다. 알림 버튼은 로그아웃 오른쪽 맨 끝에 두고 텍스트는 숨긴다.
- 헤더 종 아이콘은 최근 알림 popover를 연다. popover를 여는 것만으로는 읽음 처리하지 않고, 알림별 `보기`나 `모두 읽음`에서 읽음 처리한다.
- `folio_app/pages/notifications.py`는 전체 알림 목록을 보여주고, 페이지를 본 뒤 미확인 알림을 읽음 처리한다. 알림의 `프로젝트 보기`를 누르면 해당 상세로 이동한다.
- 프로젝트 작성자가 알림이 아닌 다른 경로로 자기 프로젝트 상세 댓글 영역을 봐도 해당 프로젝트의 댓글 알림을 읽음 처리한다.
- 이메일 알림은 `folio_app/services/email_notifications.py`에서 처리한다. `SUPABASE_SERVICE_ROLE_KEY`와 SMTP 설정이 모두 있을 때만 프로젝트 작성자 이메일을 service role로 조회해 발송한다. 설정이 없거나 발송이 실패해도 댓글 작성과 앱 내부 알림 생성은 성공 상태를 유지한다. 댓글 등록 UX가 SMTP 왕복에 막히지 않도록 이메일 발송은 백그라운드 스레드에서 처리한다.
- 같은 댓글 알림이 중복 생성되지 않도록 `notifications_project_comment_unique_idx` unique index를 추가했다. 중복 insert가 발생하면 이미 생성된 알림으로 보고 성공 처리하며, 메일은 다시 보내지 않는다.

검증:

- `python -m pyflakes folio_app app.py`
- `python -m compileall -q app.py folio_app tests`
- `python -m unittest tests.test_notifications tests.test_comments tests.test_core_flows -v`
- `python -m unittest tests.test_notifications tests.test_core_flows -v`
- `python -m unittest tests.test_email_notifications tests.test_notifications tests.test_config -v`

배포 검증:

- 원격 Supabase에 최신 `supabase/schema.sql`을 적용했다.
- Streamlit Cloud Secrets에 `SUPABASE_SERVICE_ROLE_KEY`, `SMTP_HOST`, `SMTP_FROM_EMAIL` 등 SMTP 값을 설정하고 앱을 재시작했다.
- 실제 계정으로 B가 A 프로젝트에 댓글 작성 → A 헤더 알림 `N` 배지 표시 → 알림 페이지 진입 후 읽음 처리 → 프로젝트 이동을 확인했다.
- 댓글 이메일 알림 발송을 확인했다.
- 댓글과 알림 기능은 현 범위에서 충분한 것으로 판단해 추가 확장은 보류한다.

### 완료: 홈갤러리 활동 NEW 배지 (2026-08-02)

홈갤러리 카드에는 개인화된 읽음 상태가 아니라 공개 활동성을 보여주는 배지를 붙인다.

- `services.comments.latest_comment_at_by_project()`가 프로젝트별 최신 댓글 시각을 계산한다.
- `services.projects._attach_related_data()`가 `latest_comment_at`을 프로젝트 dict에 붙인다.
- `components.ui.render_project_card_html()`은 최근 7일 내 등록 프로젝트에 `NEW`, 등록은 오래됐지만 최근 7일 내 댓글이 달린 프로젝트에 `댓글 NEW`를 표시한다.
- 배지는 카드 우상단에 absolute 배치하며, stretched link 클릭을 막지 않도록 `pointer-events: none`을 둔다.

검증:

- `python -m pyflakes folio_app app.py`
- `python -m compileall -q app.py folio_app tests`
- `python -m unittest tests.test_comments tests.test_ui_cards -v`

### 완료: Tableau Viz Gallery 1차 수집과 등록 (2026-08-11)

이전 Visual Gallery 전환 작업에서 Tableau Viz Gallery의 공개 시각화 프로젝트를 실제 Share 패널 기준으로 수집했다. 최종 등록 결과는 27개 후보 중 23개다. 수집 CSV는 `docs/curation/tableau_gallery/all.csv`, 재사용 수집기는 `tools/collect_tableau_gallery.py`에 둔다.

- 첫 시도에서 URL 규칙으로 embed URL을 추정해 CSV를 만들었으나, 실제 Share 버튼에서 얻은 값이 아니므로 폐기했다. 앞으로 Tableau embed code는 실제 UI의 Share 패널에서 읽은 값만 사용한다.
- Tableau Public 상세 페이지는 바깥 페이지와 내부 viz iframe으로 나뉜다. Share 버튼은 바깥 페이지에 있지만, Embed Code input과 Link input은 `public.tableau.com/views/...` iframe 내부에 열린다. 최상위 DOM만 보면 공유 패널이 열린 사실을 놓친다.
- Embed Code 전체는 CSV에 보존하고, FOLIO 현재 DB 모델에는 iframe으로 열 수 있는 Link input 값을 `power_bi_url`에 저장한다. 썸네일은 Embed Code의 `static_image` param에서 추출한다.
- 수집 기본 텍스트는 Tableau Details의 제목, 작성자, First Published Date, Last Published Date, Language를 사용한다. 본문 첫 줄은 로케일에 따라 `등록`, `만들기` 같은 메뉴 텍스트로 잘못 잡힐 수 있으므로 제목은 브라우저 title에서 `| Tableau Public`을 제거해 얻는다.
- Tableau UI는 영어 또는 한국어로 노출될 수 있으므로 Share 버튼 탐색은 `Share`와 `공유`를 모두 허용한다.
- 긴 수집은 전체 종료 후 판단하지 않고 항목별로 `collected`, `skipped_*`, `error_*`를 기록하고 CSV를 즉시 저장한다.

최종 스킵 항목:

- `#1` Finding Oases In Food Deserts: 10초 대기 후에도 embed code와 link를 읽지 못함
- `#7` Total Annual Loss of Bee Colonies in the US: link는 읽혔지만 embed code가 비어 있음
- `#8` Boeing Market Outlook: Tableau Public 상세 페이지가 404
- `#22` VFSG Feb: link는 읽혔지만 embed code가 비어 있음

Tableau 상세 embed는 기존 16:9/520px 가정으로 세로가 잘렸으므로 `components/dashboard.py`에서 Tableau Public URL일 때 높이를 1240px로 잡고, `styles/detail_visual.py`에서 custom component wrapper의 900px 제한과 모바일 16:9 강제를 제거했다.

검증:

- `python -m compileall -q folio_app\components\dashboard.py folio_app\styles\detail_visual.py`
- `python -m unittest tests.test_detail_components -v`

### 완료: Looker Studio Gallery 1차 수집과 등록 (2026-08-11)

Looker Studio/Data Studio Gallery의 Featured, Marketing Templates, Community, Community Visualizations 항목을 수집한 뒤 iframe 접근성을 재검증했다. 정상 렌더링되는 80개만 공개 유지하고, 접근 불가 또는 시스템 오류 항목은 skip했다. Featured 1차 등록에서 접근 불가로 확인된 6개는 Supabase에서 `is_public=false`로 전환했다. 수집 CSV는 `docs/curation/looker_studio_gallery/all.csv`, skip 로그는 `docs/curation/looker_studio_gallery/skipped.csv`, 재사용 수집기는 `tools/collect_looker_studio_gallery.py`에 둔다.

- Gallery URL은 `https://datastudio.google.com/gallery`다.
- 카테고리 URL은 `?category=marketing`, `?category=community`, `?category=visualization`으로 접근한다. Featured는 기본 Gallery URL이다.
- 카드 DOM의 `a.reportImageUrl`에서 제목, 작성자, 설명, `open/...` URL, 썸네일 URL을 읽을 수 있다.
- `open/...` URL을 브라우저로 열면 실제 보고서 URL인 `reporting/{report_id}/page/{page_id}`로 이동한다. 이 URL을 source URL로 저장한다.
- iframe embed URL은 `reporting/`을 `embed/reporting/`으로 바꾼 뒤 실제로 열어 렌더링되는지 확인한다.
- 본문이 비어 있지 않아도 `보고서에 액세스할 수 없음`, 외부 사이트 보기 사용 중지, Looker Studio 시스템 오류 문구가 있으면 skip한다.
- 썸네일은 카드 이미지의 `thumbnail?sz=w320-h240-p-k-nu` URL을 사용한다.
- Tableau와 달리 Share 패널을 열 필요가 없었다.

검증:

- `docs/curation/looker_studio_gallery/all.csv` rows 80
- `docs/curation/looker_studio_gallery/skipped.csv` rows 81
- missing embed 0
- missing thumbnail 0
- Supabase public Looker Studio projects 80, CSV와 URL 기준 일치

### 완료: 레퍼런스 네비게이션과 홈 플랫폼 필터 (2026-08-11)

수집/등록한 공개 콘텐츠를 플랫폼별로 탐색할 수 있도록 `Reference` 라우트와 헤더의 `레퍼런스` 메뉴를 추가했다. 서브메뉴는 `Tableau`, `Power BI`, `Data Studio`, `Streamlit`이며 URL 파라미터 `platform`으로 현재 플랫폼을 유지한다.

- `folio_app/services/project_references.py`가 플랫폼 분류 기준을 담당한다.
- 분류는 태그와 URL marker를 함께 본다. 예: Tableau/Public Tableau URL, PowerBI/PBI/app.powerbi.com, Looker Studio/Data Studio/datastudio.google.com, Streamlit/streamlit.app.
- 홈 갤러리는 레퍼런스와 일반 프로젝트를 함께 노출한다. 검색 패널의 라디오 필터로 `전체`, `기타`, `Tableau`, `Power BI`, `Data Studio`, `Streamlit` 중 하나를 선택한다.
- 홈 인기 태그 TOP10은 선택된 플랫폼 범위의 레퍼런스 콘텐츠까지 포함해 집계하되, 플랫폼 선택 메뉴와 중복되는 태그(`Tableau`, `Power BI`, `Data Studio`, `Streamlit`, `Looker Studio`, `Other` 등)는 제외한다.
- 레퍼런스 페이지는 카드 그리드와 상세 페이지를 재사용한다. 상세에서 돌아갈 때 `platform` 파라미터를 유지한다.
- 레퍼런스 페이지는 최초 12개 카드를 보여주고, 하단 스크롤 시 `visible` 쿼리 파라미터를 12개씩 늘려 Streamlit rerun으로 다음 묶음을 렌더링한다. 자동 스크롤 스크립트는 `components.html` iframe에서 실행되므로 상위 URL을 직접 변경하지 않고, 화면에 있는 Streamlit "더 보기" 버튼을 클릭해 같은 콜백을 태운다.
- 브라우저 검증 교훈: Streamlit 페이지의 실제 스크롤 컨테이너는 `window`가 아니라 `section.stMain`일 수 있다. 무한스크롤이나 sticky UI를 고칠 때는 먼저 Selenium/브라우저 계측으로 `scrollHeight`, `clientHeight`, `scrollTop`, sentinel 위치, iframe sandbox 오류를 확인한다.
- 레퍼런스 히어로는 홈 히어로 shell 기준(surface, border, 16px radius, grid, `28px 42px 34px` padding, `220px` min-height)을 따른다. eyebrow/title/description의 타이포그래피도 홈 히어로와 맞춘다.
- 레퍼런스 히어로 타이틀은 숫자 span만 파랑, 나머지 문장은 네이비다. Streamlit Markdown heading이 내부 span을 추가할 수 있으므로 class를 분리해 색을 고정한다.
- 우측 플랫폼 로고는 헤더 nav 우측 기준선에 맞춘다. 로고 이미지는 `width: auto`와 `max-width`/`max-height`를 사용한다. 고정 width와 `object-fit: contain` 조합은 Power BI처럼 내부 여백이 없는 에셋에서도 이미지 박스 내부 여백을 만들 수 있다.
- 프로젝트 등록/수정 폼에는 `플랫폼` 라디오를 태그 입력 아래에 둔다. 별도 DB 컬럼이 아직 없으므로 선택한 플랫폼은 공식 플랫폼 태그로 정규화해 저장한다. 예: `Data Studio` 선택 + `고객 분석` 태그 입력 → `["Data Studio", "고객 분석"]`.

검증:

- 앱 서비스 기준 공개 프로젝트 368개 중 파워BI 99개, 스트림릿 163개, 태블로 23개, 데이터스튜디오 80개, 기타 1개로 분배
- `python -m compileall -q folio_app tests`
- `python -m unittest tests.test_project_form tests.test_project_references tests.test_detail_components tests.test_project_queries -v`
- `http://localhost:8501/?page=Reference&platform=datastudio`에서 무한스크롤 `12 -> 36 -> 48 -> 60 -> 72 -> 80` 로드 확인. 마지막에는 "더 보기" 버튼이 사라지고 "모든 레퍼런스를 불러왔습니다."만 표시된다.
- `powerbi`, `datastudio`, `tableau`, `streamlit` 레퍼런스 히어로에서 로고 우측 기준과 타이틀 색상 확인. Power BI 로고는 실제 렌더 폭 약 358px로 줄고, 로고 우측과 wrapper 우측 차이는 0px이다.

### 완료: PBIX 업로드와 Power BI 게시 foundation (2026-08-11)

- `supabase/schema.sql`에 `projects.project_type`, `status`, `embed_status`, `published_at`, `deleted_at`과 `powerbi_reports` 테이블을 추가했다. 공개 프로젝트 RLS는 `is_public=true`와 `status='published'`를 함께 만족해야 한다.
- 프로젝트 삭제는 물리 삭제에서 soft delete로 바꿨다. 앱은 `status='deleted'`, `deleted_at`, `is_public=false`로 숨기며, 작성자 목록과 상세에서도 deleted 프로젝트를 제외한다.
- Power BI 설정은 `POWERBI_TENANT_ID`, `POWERBI_CLIENT_ID`, `POWERBI_CLIENT_SECRET`, `POWERBI_WORKSPACE_ID`를 사용한다. PBIX 기본 상한은 `PBIX_MAX_UPLOAD_MB=100`, Import polling 기본값은 `POWERBI_IMPORT_POLL_SECONDS=100`, PBIX 게시 후 캡처 대기 기본값은 `POWERBI_CAPTURE_READY_WAIT_SECONDS=10`이다.
- `services/powerbi.py`가 Entra client credentials token, PBIX Import API, Import polling, Report metadata 조회, Embed Token 발급, `powerbi_reports` upsert를 담당한다. Client Secret과 Embed Token은 DB에 저장하지 않는다.
- 등록 폼에서 플랫폼을 Power BI로 선택하면 PBIX 파일 업로드 필드가 보인다. PBIX 확장자와 크기 검증, Power BI 설정 누락은 프로젝트 생성 전에 중단한다.
- 신규 PBIX 등록은 프로젝트를 `processing`으로 먼저 생성한 뒤 Import를 실행한다. Import 성공 시 `published`와 `embed_status='supported'`로 전환하고, 실패/timeout은 `failed`로 표시한다.
- 상세 페이지는 PBIX 게시본이면 `powerbi_reports` 메타데이터로 Embed Token을 동적 발급해 Power BI JS SDK Viewer를 렌더한다. 기존 공개 iframe 레퍼런스는 기존 iframe fallback을 유지한다.
- PBIX 게시 성공 후 썸네일 모드가 자동 캡처이면 보고서 렌더링 준비 대기 후 Power BI report HTML을 직접 렌더링해 캡처한다. Streamlit 내부 페이지 iframe을 캡처하지 않아 Power BI JS SDK 로딩 경합과 중첩 iframe 문제를 피한다.
- 등록/수정 폼의 우측 카드 미리보기는 상세 히어로 우측 썸네일 영역과 같은 Home 카드 구조를 쓴다. 별도 미리보기 섹션은 두지 않고, 기본 정보 좌측 열의 플랫폼 선택 아래에는 PBIX 업로드를, 우측 열의 산출물 링크 아래에는 썸네일 설정을 배치한다.
- 홈/레퍼런스 카드 hover iframe preview는 제거했다. hover 시 카드는 작게 떠오르고, `cards.py`의 `::after` 오버레이가 5px 파란 테두리를 표시한다. stretched link 레이어보다 높은 z-index를 써서 썸네일/그라데이션에 묻히지 않게 한다.
- 상세 페이지 작성자 화면에는 프로젝트 삭제 버튼을 둔다. 삭제는 soft delete이며 `status='deleted'`, `deleted_at`, `is_public=false`로 즉시 목록과 상세 접근에서 숨긴다.
- 수정 화면에서 PBIX 교체, failed 프로젝트 재시도 버튼, Power BI Report/Semantic Model 30일 cleanup job은 아직 후속이다.
- 테스트용 `test1` 프로젝트(`fbe01cc3-75e3-4b6b-a5d3-f2ba564d6976`)는 마감 시점에 `is_public=false`, `status='deleted'` 상태로 확인했다.

검증:

- `python -m unittest tests.test_project_editor tests.test_powerbi tests.test_project_form tests.test_detail_components tests.test_config tests.test_project_queries tests.test_ui_cards -v`
- `python -m pyflakes folio_app app.py tests\test_project_editor.py tests\test_powerbi.py`
- `python -m compileall -q app.py folio_app tests`

### 완료: 썸네일 업로드와 PBIX 수정 UX (2026-08-15)

- 프로젝트 등록/수정 폼의 썸네일 설정에 `이미지 업로드` 모드를 추가했다. JPG, PNG, WebP를 최대 5MB까지 받으며 서버에서 960x540 JPEG로 정규화해 `project-thumbnails` Storage bucket의 기존 프로젝트 썸네일 경로에 저장한다.
- 수정 화면에서는 기존 썸네일을 삭제해 기본 커버로 되돌릴 수 있고, 새 이미지 파일을 선택하면 같은 Storage 경로를 upsert해 교체한다.
- Power BI 프로젝트 수정 화면에서도 PBIX 파일 업로드를 허용한다. 새 PBIX를 업로드하면 기존 프로젝트 ID와 상세 URL은 유지하고 `powerbi_reports` 메타데이터를 새 Import 결과로 갱신한다.
- 수정 화면에서 기존 Power BI 게시본 연결 삭제를 선택하면 FOLIO의 `powerbi_reports` row와 `projects.power_bi_url` 연결을 제거한다. Power BI Workspace의 Report/Semantic Model 물리 삭제는 30일 cleanup 정책과 별도로 남겨둔다.
- `projects.thumbnail_mode` 체크 제약에 `upload` 값이 추가됐으므로 원격 Supabase에 최신 `supabase/schema.sql` 재적용이 필요하다.
- 기존 썸네일이 있는 수정 화면에서 `이미지 업로드`는 기존 썸네일 삭제 체크박스를 먼저 선택해야 새 업로드 컴포넌트가 나타난다. PBIX도 기존 게시본 연결 삭제를 선택해야 새 PBIX 업로드 컴포넌트가 나타난다.
- 썸네일 모드 `자동 캡처`는 기존 캡처본을 삭제하고 새로 캡처할 수 있다. 수정 저장 완료 후에는 홈 갤러리로 이동한다.
- 산출물 링크의 `Web Application URL` 라벨은 `Web App URL`로 통일했다.

검증:

- `python -m unittest tests.test_project_editor tests.test_powerbi tests.test_project_form tests.test_detail_components tests.test_config tests.test_project_queries tests.test_ui_cards -v`
- `python -m pyflakes folio_app app.py tests`
- `python -m compileall -q app.py folio_app tests`

### 완료: 홈 로딩 최적화와 푸터 버전 표시 (2026-08-15)

- 홈 기본 화면은 `list_home_project_snapshot(limit=6, tag_limit=40)`을 사용해 최근/조회/좋아요 레일에 필요한 프로젝트만 가져온다. 레일당 최대 카드 수는 6개다.
- 공개 프로젝트 조회 컬럼은 `PUBLIC_PROJECT_LIST_COLUMNS`로 제한한다. `select("*")`는 홈 공개 목록 경로에서 피한다.
- 댓글 통계는 `comment_stats_by_project()`로 댓글 수와 최신 댓글 시각을 한 번에 조회한다.
- 홈 인기 태그는 스냅샷 경로와 프로젝트 기반 집계 경로 모두 `_filter_platform_tags()` / `_platform_tag_exclusions()`를 통과한다. `reference`, `references`, `레퍼런스`, `참고`는 인기 태그에서 제외한다.
- 푸터는 좌측 저작권, 중앙 `APP_VERSION`, 우측 정책 링크 묶음으로 배치한다. 버전 문자열은 배포 때만 갱신한다.

검증:

- `python -m unittest tests.test_project_references -v`
- `python -m unittest discover -s tests`
- `python -m compileall -q folio_app tests`
- `python -m pyflakes folio_app app.py tests`

### 완료: 홈 최초 로딩 성능 1차 개선 (2026-08-23)

- Streamlit Community Cloud 배포본에서 첫 진입 시 흰 화면 또는 Streamlit wrapper/footer만 보이다가, 헤더/히어로가 먼저 뜨고 갤러리가 뒤늦게 따라오는 현상을 확인했다.
- 원인 후보는 크게 두 가지였다. 하나는 `EncryptedCookieManager.ready()` 전 `st.stop()` 때문에 공개 Home도 본문을 그리지 못하는 초기 공백이고, 다른 하나는 홈 기본 snapshot이 여러 Supabase 조회를 직렬로 수행하는 구조다.
- 공개 Home 기본 진입에서는 쿠키 매니저가 아직 준비되지 않아도 `render_header()`와 `home.render_loading_shell()`을 먼저 렌더한다. 상세, 로그아웃, 비밀번호 재설정, 인증 code 처리 경로는 shell을 표시하지 않는다.
- `visitor_id` 쿠키 생성은 모든 홈 첫 방문에서 하지 않고, `project_id`가 있는 상세 페이지 진입에서만 수행한다. 조회수 집계에 필요한 익명 ID는 상세에서만 필요하기 때문이다.
- 홈 좋아요 레일은 `likes` 테이블 전체를 읽지 않고 최근 좋아요 샘플만 읽어 프로젝트별 빈도를 계산한다. MVP 홈의 목적은 정확한 전체 기간 랭킹보다 첫 화면 체감 속도다.
- 홈의 전체 프로젝트 수와 인기 태그는 `home_tag_summary()`로 통합했다. 별도 count 쿼리를 제거하고, 공개 프로젝트 tag rows 한 번으로 count와 popular tags를 함께 계산한다.
- 쿠키 대기 중 보이는 로딩 shell은 기존 홈 히어로와 검색 패널 톤을 맞춘 skeleton이다. 쿠키가 준비되기 전의 초기 공백을 줄이는 목적이다.
- 후속 측정에서 같은 Streamlit run 안에서 `st.empty()`로 그렸다가 바로 비우는 데이터 조회 중 skeleton은 실제 배포 DOM에 안정적으로 남지 않는 것을 확인했다. 해당 왕복 렌더는 제거하고, 좋아요 후보 조회를 홈 카드 limit 기준으로 줄여 초기 쿼리량을 더 낮췄다.
- 댓글 통계 생략은 배포 측정에서 갤러리 표시 시간을 의미 있게 줄이지 못해 되돌렸다. 원인 분석은 `python tools\profile_home_snapshot.py --warm-runs 1`로 홈 snapshot 단계별 시간을 먼저 확인한다.
- 홈 snapshot RPC 1차 구현은 `public.home_project_snapshot(p_limit, p_tag_limit, p_like_sample_limit)`이다. 코드에는 RPC 우선/fallback 경로가 있지만, 원격 DB에 함수가 없는 상태에서 배포하면 누락된 RPC 호출이 먼저 실패해 초기 로딩이 더 느려질 수 있다. 반드시 Supabase SQL Editor에서 최신 `supabase/schema.sql`의 RPC를 적용한 뒤 앱 코드를 배포하고 계측한다.
- Streamlit Community Cloud는 공식 문서 기준 12시간 무트래픽 후 sleep 상태가 되므로 30분 반복 ping은 운영 목적 대비 과하다. `.github/workflows/keepalive.yml`의 KST 08:00 전후 wake 작업만 유지하고, 30분 간격 `keepalive-ping.yml`은 제거했다.
- 공개 Home 기본 진입은 쿠키 복원보다 첫 렌더 속도를 우선해 CookieManager를 마운트하지 않는다. 새 브라우저 세션의 저장된 로그인 쿠키 복원은 상세/보호/인증 흐름으로 들어갈 때 수행된다. 기본 홈에서 CookieManager iframe과 ready 대기 rerun을 제거하는 목적이다.
- 런칭 모드는 Power BI-first다. Tableau/Looker Studio/Streamlit 레퍼런스 분류와 수집 데이터는 유지하되, UI 노출 플랫폼은 `VISIBLE_REFERENCE_PLATFORM_KEYS = ("powerbi",)`로 제한한다. 홈 콘텐츠 유형 필터는 숨기고 Power BI로 고정하며, 상단 독립 `레퍼런스` 메뉴는 숨긴다. Power BI 메뉴의 공식 레퍼런스 링크와 직접 `Reference` URL은 Power BI 레퍼런스만 보여준다.
- 로컬 브라우저 검증 중 8501에 여러 Streamlit 리스너가 생기며 캡처가 최신 코드와 맞지 않는 상태를 확인했다. 서버 검증이 10초 이상 애매하면 추가 서버를 띄우지 말고 `netstat -ano | Select-String ':8501'`로 리스너 수를 확인한다.

검증:

- `python -m unittest tests.test_view_count tests.test_project_queries -v`
- `python -m unittest tests.test_project_queries -v`
- `python -m unittest tests.test_view_count tests.test_project_queries tests.test_ui_cards -v`
- `python -m compileall -q app.py folio_app tests`
- `python -m pyflakes folio_app app.py tests`
- `python -m unittest discover -s tests -v`

### 진행 중: Power BI-first UI 정리와 레퍼런스 UX 개선 (2026-08-23)

- 작업트리 기준 푸터 버전은 `v2026.08.23.10`이다. 이 변경은 아직 커밋되지 않았다.
- 레퍼런스 페이지 히어로에서 "공식" 문구를 제거했다. Power BI 메뉴 안의 `공식 레퍼런스` 라벨도 `레퍼런스`로 바꿨다.
- 레퍼런스 페이지 우상단에 정렬 버튼 `최신`, `좋아요`, `조회수`를 추가했다. 정렬 기준은 홈 갤러리의 `최신순`, `좋아요순`, `조회수순`을 재사용한다.
- 레퍼런스 정렬 버튼은 Streamlit rerun이 아니라 클라이언트 JS로 카드 DOM을 재정렬한다. 카드 슬롯에는 `data-created-at`, `data-like-count`, `data-view-count`가 들어간다.
- 레퍼런스 정렬 클릭 시 URL의 `sort`만 `history.pushState`로 갱신하고, 상세 카드 링크에도 현재 정렬값을 반영한다.
- 레퍼런스 `더 보기`는 아직 기존 방식이다. 자동 스크롤이 Streamlit 버튼을 클릭하고 `visible` query parameter가 늘면서 rerun된다.
- 홈 히어로 설명 문구를 서비스 방향성에 맞게 조정했다. 설명은 쉼표 뒤 줄바꿈으로 첫 줄을 짧게, 아래 줄을 길고 무겁게 받치는 구도를 우선한다.
- 현재 홈 히어로 설명:
  - `FOLIO는 좋은 시각화를 발견하고,` / `직접 경험하며 토론하고 함께 성장하는 커뮤니티입니다.`
  - `각자의 시각화 경험을 나누고,` / `댓글과 피드백으로 더 나은 관점을 만들어갑니다.`
  - `PBIX 파일을 간편하게 게시하고,` / `누구나 열어볼 수 있는 보고서 페이지로 프로젝트를 공유합니다.`
  - `스터디 클럽에서 함께 실습하고,` / `보고서 디자인과 DAX, 경영정보시각화 실기를 토론하며 성장합니다.`

검증:

- `python -m pyflakes folio_app app.py tests`
- `python -m unittest tests.test_project_references tests.test_core_flows tests.test_ui_cards -v`
- `python -m pyflakes folio_app\pages\home.py`

### 완료: Power BI 콘텐츠 허브 리팩토링 (2026-08-15)

- `folio_app/pages/powerbi.py`는 Streamlit 화면 조합, hero, 카드 HTML, 페이지네이션만 담당하도록 축소했다.
- Power BI 큐레이션 CSV 로딩, 커뮤니티/학습 탭 그룹핑, 월간 업데이트와 패치 로그를 하나의 게시판 아이템으로 병합하는 로직은 `folio_app/services/powerbi_content.py`로 분리했다.
- 업데이트/패치로그의 한국어 라벨과 요약 변환 규칙은 `folio_app/services/powerbi_i18n.py`로 분리했다.
- `tools/collect_powerbi_all.py`는 `Collector` registry 구조로 정리했다. 새 수집원이 생기면 개별 수집기, `COLLECTORS`, `CSV_OUTPUTS`, 검증 규칙을 함께 갱신한다.
- 프로젝트 등록/수정 공용 폼은 제출/공개 액션 영역을 `_render_project_form_actions()`로 분리해 `render_project_form()`의 책임을 줄였다.
- 홈 히어로 배너는 마지막 슬라이드에서 첫 번째 슬라이드 clone으로 한 번 더 우측 진행한 뒤 원래 첫 번째 슬라이드로 snap back하는 구조로 수정했다. 이 변경은 Playwright 화면 확인 전에는 배포 판단에 포함하지 않는다.

검증:

- `python -m compileall -q folio_app\pages\powerbi.py folio_app\services\powerbi_content.py folio_app\services\powerbi_i18n.py folio_app\components\project_form.py tools\collect_powerbi_all.py`
- `python tools\collect_powerbi_all.py --dry-run --skip-validation --skip-reference-check --skip-thumbnail-cleanup`
- `python -m unittest tests.test_project_form tests.test_project_editor`
- `python -m unittest tests.test_powerbi`
- `python -m unittest tests.test_powerbi_content`
- `python -m unittest discover -s tests`

### 다음 할 일

1. 현재 작업트리 정리 여부를 결정한다.
   - 미커밋 변경: 레퍼런스 정렬 UX, 홈 히어로 문구, 푸터 버전, `docs/FOLIO_Community_PRD.md`, `docs/FOLIO_Admin_PRD.md`, 문서 갱신.
   - 콘텐츠 번역 작업과 UI 작업 diff가 섞이지 않도록 커밋/배포 여부를 먼저 정한다.

2. Power BI 콘텐츠 번역 품질 개선을 위한 구조 분석을 먼저 한다.
   - `docs/curation/powerbi_CONTENT_OPS.md`
   - `docs/curation/powerbi_desktop_download/`, `docs/curation/powerbi_updates/`, `docs/curation/powerbi_changelog/`, `docs/curation/powerbi_community/`, `docs/curation/powerbi_learning/`
   - `folio_app/services/powerbi_content.py`
   - `folio_app/services/powerbi_i18n.py`
   - `tools/collect_powerbi_all.py`
   - `tests/test_powerbi_content.py`, `tests/test_powerbi.py`

3. 바로 번역을 수정하지 말고 번역 대상/방식/우선순위 계획을 먼저 세운다.
   - 어떤 CSV 컬럼이 화면에 노출되는지 확인한다.
   - 현재 번역 규칙이 코드 기반(`powerbi_i18n.py`)인지, CSV 저장값 기반인지 구분한다.
   - 자동 수집을 다시 돌릴 때 기존 수동 수정 번역이 덮이는지 확인한다.
   - 샘플 20~30개를 뽑아 어색한 번역 유형을 분류한다.

4. 번역 개선 방향 후보를 비교한다.
   - 빠른 규칙 보강: `powerbi_i18n.py`의 용어/패턴 매핑 보강.
   - 데이터 보정: 이미 수집된 CSV의 `title_ko`, `summary_ko`, `feature_description_ko`를 선별 보정.
   - 운영 가능 구조: 용어집/문장 패턴을 CSV 또는 JSON으로 분리해 반복 수정 가능하게 만든다.

5. 새 PRD 기반 커뮤니티/Admin 구현은 번역 작업 이후 별도 컨텍스트에서 다룬다.
   - 커뮤니티는 하나의 게시판으로 공지/질문/팁·노하우/기타를 처리한다.
   - Admin은 승인 시스템이 아니라 사후 관리 도구다.
   - 두 기능 모두 기존 프로젝트/댓글/조회수/권한 구조를 먼저 분석한 뒤 최소 변경 계획을 세운다.

6. 홈/레퍼런스 UI 변경을 배포한다면 배포 후 직접 확인한다.
   - 레퍼런스 정렬 버튼 클릭 시 페이지 전체 리로드 없이 카드 순서가 바뀌는지 확인한다.
   - 상세 진입/복귀 시 `sort` 상태가 유지되는지 확인한다.
   - 홈 히어로 설명 줄바꿈이 첫 줄 짧게, 아래 줄 길게 보이는지 확인한다.
