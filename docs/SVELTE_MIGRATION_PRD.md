# FOLIO Svelte 단계적 재구축 PRD

- 문서 버전: v0.1
- 작성일: 2026-08-24
- 기준 자료: `README.md`, `docs/ARCHITECTURE.md`, `docs/DATA_MODEL.md`, `docs/USER_FLOWS.md`, `docs/MVP_PRD.md`, `docs/PROJECT_CONTEXT.md`, 실제 `folio_app/` 코드와 `supabase/schema.sql`
- 목적: 현재 Streamlit MVP를 유지하면서, 공개 사용자 경험부터 Svelte 기반 웹앱으로 단계 이전하기 위한 화면 우선순위와 데이터 계약을 먼저 정의한다.

---

## 1. 배경

현재 FOLIO는 Streamlit + Supabase 기반 MVP다. Streamlit은 빠른 실험과 운영에는 유리했지만, 홈 첫 로딩, 상세 전환, 모바일 UI, 커뮤니티/Admin 확장성, 커스텀 도메인 운영 관점에서 한계가 있다.

Svelte 전환은 기존 제품을 한 번에 갈아엎는 작업이 아니다. 현재 Supabase Auth, PostgreSQL, RLS, 프로젝트/댓글/좋아요/신고/알림 모델을 최대한 유지하고, 공개 조회 화면부터 별도 프론트엔드로 이전한다.

핵심 원칙:

1. Streamlit 앱은 전환 기간 동안 계속 운영한다.
2. Supabase 스키마와 RLS를 단일 진실 공급원으로 유지한다.
3. Svelte 1차 범위는 공개 조회 경험 개선이다.
4. 등록/수정/PBIX/썸네일 캡처는 데이터 계약이 안정된 뒤 옮긴다.
5. 새 기능을 추가하기보다 현재 홈/상세/콘텐츠 흐름을 먼저 동일하게 재현한다.

---

## 2. 현재 Streamlit 앱 구조

### 실행 구조

```text
streamlit run app.py
  -> app.py
  -> folio_app.app.main()
  -> apply_global_styles()
  -> Supabase/Auth/Cookie 준비
  -> render_header()
  -> page query 기반 화면 렌더
  -> footer
```

루트 `app.py`는 얇은 실행 진입점이고, 실제 라우팅과 인증 복구는 `folio_app/app.py`가 담당한다. 파일 기반 멀티페이지가 아니라 `st.query_params["page"]`로 화면을 선택한다.

### 주요 라우트

| 현재 query | 현재 화면 | Svelte 전환 시 권장 URL | 우선순위 |
|---|---|---|---:|
| `?page=Home` | 홈, 검색, 태그, 프로젝트 레일 | `/` | P0 |
| `?page=Home&project_id=:id` | 프로젝트 상세 | `/projects/:id` | P0 |
| `?page=Reference&platform=powerbi` | Power BI 레퍼런스 목록 | `/references/powerbi` | P1 |
| `?page=Power BI` | Power BI 콘텐츠 허브 | `/powerbi` | P1 |
| `?page=Login` | 로그인 | `/login` | P2 |
| `?page=Sign+Up` | 회원가입 | `/signup` | P2 |
| `?page=Submit` | 프로젝트 등록 | `/submit` | P3 |
| `?page=My+Page` | 프로필, 내 프로젝트 관리 | `/me` | P3 |
| `?page=Notifications` | 알림 목록 | `/notifications` | P4 |
| `?page=About` | 서비스 소개 | `/about` | P2 |
| `?page=Policy&type=...` | 정책 본문 | `/policy/:type` | P2 |

### 주요 계층

| 계층 | 현재 위치 | Svelte 이전 대응 |
|---|---|---|
| 화면 조합 | `folio_app/pages/` | SvelteKit routes |
| 반복 UI | `folio_app/components/` | Svelte components |
| 데이터 접근 | `folio_app/services/` | Supabase client + server routes |
| 스타일 | `folio_app/styles/` | CSS tokens + component styles |
| DB/RLS/RPC | `supabase/schema.sql` | 유지 |
| 큐레이션 CSV | `docs/curation/**/all.csv` | 초기에는 정적 import 또는 빌드 산출물 |

---

## 3. 현재 Supabase 데이터 모델 요약

실제 기준은 `supabase/schema.sql`이다. 문서화된 `DATA_MODEL.md`보다 현재 스키마가 더 확장되어 있다.

### 핵심 테이블

| 테이블 | 역할 | Svelte 계약 |
|---|---|---|
| `profiles` | 사용자 프로필, role | 본인 조회/수정은 인증 필요 |
| `public_profiles` | 공개 작성자 정보 view | 공개 카드/상세에서 사용 |
| `projects` | 프로젝트/레퍼런스 본문, 링크, 상태 | 공개 조회의 핵심 모델 |
| `powerbi_reports` | Power BI Embedded 메타데이터 | 서버 전용 token 발급과 결합 |
| `likes` | 사용자별 좋아요 | 로그인 사용자 mutation |
| `comments` | 상세 댓글과 1단계 답글 | 공개 조회, 로그인 작성 |
| `project_comment_reads` | 작성자 댓글 읽음 상태 | My Page/알림 단계에서 이전 |
| `content_reports` | 콘텐츠 신고 | 로그인 사용자 접수, Admin 조회 |
| `notifications` | 댓글 알림 | 로그인 사용자 전용 |
| `project_views` | 일간 중복 조회수 기록 | 직접 접근 금지, RPC만 사용 |
| `policy_versions`, `user_policy_consents` | 약관/개인정보 동의 | Auth 이전 단계에서 유지 |

### 프로젝트 주요 필드

| 필드 | 의미 | 공개 조회 사용 |
|---|---|---|
| `id` | 프로젝트 ID | 필수 |
| `author_id` | 작성자 profile FK | 필수 |
| `title` | 제목 | 필수 |
| `one_liner` | 카드/히어로 요약 | 필수 권장 |
| `problem`, `dataset`, `process`, `insights` | 상세 리포트 본문 | 상세에서 사용 |
| `power_bi_url` | iframe/embed URL 또는 원본 embed | 대표 결과물 |
| `report_url` | Web App/보고서 URL | 외부 링크 |
| `github_url` | GitHub URL | 외부 링크 |
| `thumbnail_url` | 카드/히어로 이미지 | 카드/상세 |
| `thumbnail_mode` | `auto_cover`, `manual_url`, `capture`, `upload` | 카드 표시 로직 |
| `project_type` | `powerbi`, `tableau`, `looker`, `streamlit`, `notebook`, `html_report`, `markdown_report`, `web`, `other` | 필터/상태 |
| `platform_key` | `powerbi`, `tableau`, `datastudio`, `streamlit` | 홈/레퍼런스 필터 |
| `status` | `processing`, `published`, `failed`, `deleted` | 공개 노출/상태 UI |
| `embed_status` | `supported`, `external_only`, `failed` | 상세 대표 결과물 분기 |
| `tags` | 탐색 태그 | 홈 검색/칩 |
| `view_count` | 누적 조회수 | 카드/상세 |
| `is_public` | 공개 여부 | 공개 조회 필터 |
| `published_at`, `deleted_at`, `created_at`, `updated_at` | 상태/정렬 | 목록/상세 |

### 현재 RPC 계약

| RPC | 용도 | Svelte 필요성 |
|---|---|---|
| `home_project_snapshot(p_limit, p_tag_limit, p_like_sample_limit, p_platform_key)` | 홈 첫 화면 레일/태그/총 개수 | P0에서 그대로 사용 |
| `project_detail_snapshot(p_project_id)` | 상세 한 번에 조회 | P0에서 그대로 사용 |
| `increment_project_view_count(project_id_input, anonymous_viewer_id_input)` | 중복 방지 조회수 증가 | P0 상세에서 사용 |

Svelte P0에서는 `home_project_snapshot`과 `project_detail_snapshot`을 우선 데이터 계약으로 삼는다. 테이블을 조합해 같은 결과를 만들면 초기에 성능/권한 차이가 생기기 쉽다.

---

## 4. 현재 홈/상세/콘텐츠 흐름

### 홈

현재 홈은 Power BI-first 기본 범위를 사용한다.

```text
Home
  -> hero carousel
  -> 기본 진입이면 home_project_snapshot(platform_key='powerbi')
  -> 검색/태그 필터가 있으면 list_public_projects 후 클라이언트 필터
  -> 최근/조회/좋아요 레일
  -> 카드 클릭 시 ?page=Home&project_id=:id
```

Svelte P0에서는 홈 기본 진입을 서버 로드 또는 edge 캐시 가능한 API로 빠르게 제공한다. 검색/태그는 초기에는 URL query 기반 클라이언트 상태로 구현하되, 데이터 수가 커지면 검색 RPC를 별도로 둔다.

### 상세

현재 상세는 홈 또는 레퍼런스 안에서 같은 `project_detail.render()`를 공유한다.

```text
Project Detail
  -> project_detail_snapshot
  -> hero card
  -> 대표 결과물
     -> status processing/failed 메시지
     -> Power BI project면 서버에서 embed token 발급 시도
     -> 실패하면 power_bi_url iframe fallback
  -> 프로젝트 리포트 본문
  -> 댓글
  -> 좋아요/신고/수정/삭제 액션
  -> increment_project_view_count
```

Svelte P0에서는 상세 조회, 대표 결과물, 조회수 증가까지만 필수다. 좋아요/댓글/신고는 P2에서 인증 이전과 함께 옮긴다.

### 콘텐츠 흐름

현재 콘텐츠는 세 갈래다.

1. 사용자 등록 프로젝트: `projects`에 저장되고 홈/상세에 노출된다.
2. 공개 레퍼런스 프로젝트: 동일한 `projects` 모델을 사용하되 태그, URL marker, `platform_key`로 분류된다.
3. Power BI 콘텐츠 허브: `docs/curation/powerbi_*` CSV를 `services/powerbi_content.py`가 로딩해 화면에 표시한다.

Svelte P1에서는 프로젝트형 콘텐츠와 큐레이션 CSV형 콘텐츠를 명확히 나눈다. 프로젝트 상세로 이어지는 것은 `projects` 모델, 업데이트/학습/커뮤니티 소식은 `content item` 계약으로 분리한다.

---

## 5. Svelte 재구축 목표와 비목표

### 목표

1. 공개 홈 첫 화면과 상세 전환을 빠르게 만든다.
2. URL 구조를 query 중심에서 경로 중심으로 바꾼다.
3. 모바일에서 카드/상세/대표 결과물이 자연스럽게 보이게 한다.
4. Supabase RLS를 유지하면서 클라이언트 공개 조회와 서버 전용 작업 경계를 명확히 한다.
5. Auth/댓글/등록/Admin을 단계적으로 옮길 수 있는 데이터 계약을 고정한다.

### 비목표

1. Supabase를 교체하지 않는다.
2. 모든 화면을 한 번에 Svelte로 다시 만들지 않는다.
3. 초기 단계에서 프로젝트 등록/수정 폼을 재구현하지 않는다.
4. Power BI Client Secret 또는 Embed Token을 브라우저에 저장하지 않는다.
5. PBIX 업로드/썸네일 캡처를 프론트엔드 단독 기능으로 만들지 않는다.

---

## 6. 화면 우선순위

### P0: 공개 조회 핵심

| 화면 | 목표 | 필수 데이터 |
|---|---|---|
| 홈 `/` | hero, 검색 진입, 인기 태그, 최근/조회/좋아요 레일 | `home_project_snapshot` |
| 상세 `/projects/:id` | 프로젝트 이해, 대표 결과물, 본문, 외부 링크 | `project_detail_snapshot`, `powerbi_reports` 서버 조회 |
| 404/오류 | 삭제/비공개/없는 프로젝트 처리 | status-aware error |

P0 완료 기준:

- 비로그인 사용자가 홈에서 프로젝트를 보고 상세로 이동할 수 있다.
- Power BI 프로젝트는 embedded viewer 또는 iframe fallback을 표시한다.
- 조회수 RPC가 중복 방지 기준으로 동작한다.
- Streamlit 홈/상세와 같은 프로젝트 집합을 보여준다.

### P1: 콘텐츠 발견 확장

| 화면 | 목표 | 필수 데이터 |
|---|---|---|
| 레퍼런스 `/references/powerbi` | Power BI 레퍼런스 목록, 정렬, 더 보기 | `projects` 공개 목록 또는 전용 RPC |
| Power BI 허브 `/powerbi` | 업데이트/학습/커뮤니티 콘텐츠 탐색 | `docs/curation/powerbi_*` 변환 데이터 |
| About/Policy | 공개 정적 정보 | Markdown 또는 정적 컴포넌트 |

P1 완료 기준:

- 현재 Power BI-first 정책과 동일하게 Power BI 레퍼런스만 노출한다.
- 정렬은 최신/좋아요/조회수를 지원한다.
- 콘텐츠 허브는 원문 URL과 출처를 명확히 표시한다.

### P2: 인증 기반 참여

| 화면/기능 | 목표 | 필수 데이터 |
|---|---|---|
| 로그인/회원가입 | Supabase Auth 전환 | Auth session |
| 온보딩 | 정책 동의 유지 | `policy_versions`, `user_policy_consents` |
| 좋아요 | 상세/카드 반응 | `likes` |
| 댓글/답글 | 상세 커뮤니티 | `comments`, `notifications` |
| 신고 | 운영자 접수 | `content_reports` |

P2 완료 기준:

- Supabase Auth 세션이 SvelteKit SSR/CSR에서 일관되게 복구된다.
- 기존 RLS 정책을 바꾸지 않고 좋아요/댓글/신고가 동작한다.
- 댓글 작성 시 프로젝트 작성자 알림 생성 계약을 유지한다.

### P3: 제작자 기능

| 화면/기능 | 목표 | 필수 데이터 |
|---|---|---|
| Submit | 프로젝트 등록 | `projects`, Storage |
| Edit | 프로젝트 수정/삭제 | `projects`, `powerbi_reports` |
| My Page | 프로필과 내 프로젝트 관리 | `profiles`, `projects` |
| 썸네일 업로드 | 이미지 업로드/최적화 | Supabase Storage |
| PBIX 게시 | Power BI Import | 서버 API, `powerbi_reports` |

P3 완료 기준:

- 기존 Streamlit 등록/수정 기능과 동등한 필수 입력, URL 검증, 태그 규칙을 제공한다.
- PBIX와 자동 캡처는 서버 전용 API/Worker에서 처리한다.
- 실패 시 프로젝트/기존 게시본 보존 정책이 현재와 동일하다.

### P4: 운영 확장

| 화면/기능 | 목표 |
|---|---|
| Admin | 프로젝트/댓글/신고/사용자 사후 관리 |
| Notifications | 알림 목록/읽음 처리 |
| Community 게시판 | 별도 게시판 PRD 기반 확장 |
| 콘텐츠 운영 | GitHub Actions 기반 큐레이션 업데이트 트리거 |

---

## 7. 데이터 계약

### 7.1 ProjectCard

홈, 레퍼런스, 상세 히어로에서 같은 카드 계약을 사용한다.

```ts
type ProjectCard = {
  id: string;
  title: string;
  one_liner: string | null;
  tags: string[];
  thumbnail_url: string | null;
  thumbnail_mode: 'auto_cover' | 'manual_url' | 'capture' | 'upload';
  platform_key: 'powerbi' | 'tableau' | 'datastudio' | 'streamlit' | null;
  project_type: 'powerbi' | 'tableau' | 'looker' | 'streamlit' | 'notebook' | 'html_report' | 'markdown_report' | 'web' | 'other';
  status: 'processing' | 'published' | 'failed' | 'deleted';
  embed_status: 'supported' | 'external_only' | 'failed';
  view_count: number;
  like_count: number;
  comment_count: number;
  created_at: string;
  author?: {
    id?: string;
    name?: string;
    organization?: string | null;
    avatar_url?: string | null;
  };
};
```

### 7.2 HomeSnapshot

`home_project_snapshot` RPC 결과를 그대로 반영한다.

```ts
type HomeSnapshot = {
  total_project_count: number;
  popular_tags: string[];
  recent_projects: ProjectCard[];
  viewed_projects: ProjectCard[];
  liked_projects: ProjectCard[];
};
```

요청 파라미터:

```ts
type HomeSnapshotRequest = {
  p_limit: number;              // 기본 6
  p_tag_limit: number;          // 기본 40
  p_like_sample_limit: number;  // 기본 limit * 20
  p_platform_key?: 'powerbi' | 'tableau' | 'datastudio' | 'streamlit';
};
```

P0 기본값은 `p_platform_key='powerbi'`다.

### 7.3 ProjectDetail

```ts
type ProjectDetail = ProjectCard & {
  author_id: string;
  problem: string | null;
  dataset: string | null;
  process: string | null;
  insights: string | null;
  power_bi_url: string | null;
  report_url: string | null;
  github_url: string | null;
  is_public: boolean;
  updated_at: string;
  latest_comment_at?: string | null;
};
```

상세 본문 표시 순서:

1. 대표 결과물
2. 문제 정의: `problem`
3. 사용 데이터: `dataset`
4. 분석 및 시각화: `process`
5. 주요 관찰 포인트: `insights`
6. Source & Links: `power_bi_url`, `report_url`, `github_url`
7. 댓글

### 7.4 PowerBIEmbedConfig

Embed Token 발급은 서버 전용 API에서만 수행한다.

```ts
type PowerBIEmbedConfig = {
  report_id: string;
  embed_url: string;
  embed_token: string;
};
```

계약:

- 클라이언트는 `/api/projects/:id/powerbi-embed` 같은 서버 endpoint만 호출한다.
- 서버는 `powerbi_reports`에서 `report_id`, `dataset_id`, `embed_url`을 조회한다.
- 서버는 Power BI API로 embed token을 발급해 응답한다.
- token과 client secret은 DB, localStorage, 브라우저 쿠키에 저장하지 않는다.

### 7.5 Like

```ts
type LikeState = {
  project_id: string;
  user_id: string;
  liked: boolean;
  like_count: number;
};
```

계약:

- 비로그인 사용자는 좋아요 버튼 클릭 시 `/login`으로 이동한다.
- 로그인 사용자는 `likes(project_id, user_id)`를 insert/delete한다.
- 중복 insert는 이미 좋아요 상태로 처리한다.

### 7.6 Comment

```ts
type CommentItem = {
  id: string;
  project_id: string;
  author_id: string;
  parent_id: string | null;
  depth: 0 | 1;
  body: string;
  is_deleted: boolean;
  created_at: string;
  updated_at: string;
  author?: {
    id?: string;
    name?: string;
    organization?: string | null;
    avatar_url?: string | null;
  };
  replies?: CommentItem[];
};
```

계약:

- depth는 0 또는 1만 허용한다.
- 삭제는 현재 구현처럼 본인 댓글 delete 정책을 따른다.
- 작성 성공 시 프로젝트 작성자에게 `notifications(type='project_comment')`를 생성한다.

### 7.7 Content Item

Power BI 허브의 CSV 기반 콘텐츠를 Svelte에서 다루기 위한 별도 계약이다. P1에서는 DB 테이블로 만들지 않고 빌드 시 JSON으로 변환해도 된다.

```ts
type ContentItem = {
  id: string;
  content_type: 'desktop_download' | 'update' | 'changelog' | 'community_blog' | 'learning_video' | 'learning_program';
  title: string;
  title_ko?: string | null;
  summary?: string | null;
  summary_ko?: string | null;
  source: string;
  source_url: string;
  thumbnail_url?: string | null;
  published_at?: string | null;
  collected_at?: string | null;
};
```

---

## 8. 권한과 서버 경계

### 클라이언트에서 직접 호출 가능

- 공개 프로젝트 목록/상세 조회
- `public_profiles` 조회
- 공개 댓글 조회
- 로그인 사용자 본인 좋아요/댓글/신고 mutation
- 로그인 사용자 본인 profile/my projects 조회

단, RLS가 최종 권한이다.

### 서버 endpoint 또는 Worker 필요

- Power BI Embed Token 발급
- PBIX Import와 polling
- 썸네일 이미지 리사이징/압축
- 자동 캡처
- SMTP 이메일 발송
- Admin 운영 action 중 service role이 필요한 작업
- 콘텐츠 수집/CSV 갱신/GitHub Actions 트리거

### 쿠키/Auth 재설계 원칙

현재 Streamlit은 `session_state`와 암호화 쿠키로 토큰을 복구한다. SvelteKit에서는 Supabase SSR 방식으로 session cookie를 관리하고, 인증 필요한 서버 load/action에서 session을 확인한다.

마이그레이션 중에는 Streamlit 쿠키와 Svelte 쿠키를 공유하려고 하지 않는다. 같은 Supabase Auth 사용자를 쓰되, 앱별 로그인은 별도 세션으로 시작하는 편이 안전하다.

---

## 9. 라우팅 전환 규칙

| 기존 URL | 새 URL | 처리 |
|---|---|---|
| `/?page=Home` | `/` | 301 또는 내부 rewrite |
| `/?page=Home&project_id=:id` | `/projects/:id` | 301 |
| `/?page=Reference&platform=powerbi` | `/references/powerbi` | 301 |
| `/?page=Reference&project_id=:id&platform=powerbi` | `/projects/:id?from=references&platform=powerbi` | 301 |
| `/?page=Power%20BI` | `/powerbi` | 301 |
| `/?page=About` | `/about` | 301 |
| `/?page=Policy&type=privacy` | `/policy/privacy` | 301 |
| `/?page=Policy&type=terms` | `/policy/terms` | 301 |

초기 배포에서는 Streamlit과 Svelte가 서로 다른 서브도메인에 있을 수 있으므로, 실제 301은 도메인 통합 시점에 적용한다.

---

## 10. 단계별 마이그레이션 계획

### Phase 0: 계약 고정

범위:

- 이 문서를 기준으로 P0/P1 데이터 타입을 확정한다.
- `home_project_snapshot`, `project_detail_snapshot` 응답 샘플을 저장한다.
- 공개 조회에 필요한 컬럼과 RLS를 다시 검증한다.
- 디자인 토큰을 Svelte CSS 변수로 옮길 수 있게 정리한다.

완료 기준:

- ProjectCard, HomeSnapshot, ProjectDetail 계약이 코드/스키마와 일치한다.
- Streamlit 홈/상세가 어떤 RPC와 컬럼을 쓰는지 문서화되어 있다.

### Phase 1: Svelte P0 스파이크

범위:

- 별도 디렉터리 또는 브랜치에 SvelteKit 앱 생성
- Supabase public client 연결
- `/` 홈 레일 렌더
- `/projects/:id` 상세 렌더
- 조회수 RPC 호출
- Power BI iframe fallback 표시

제외:

- 로그인
- 좋아요
- 댓글 작성
- 프로젝트 등록/수정

완료 기준:

- 운영 Supabase의 공개 데이터로 홈/상세를 볼 수 있다.
- Streamlit과 동일한 공개 프로젝트가 표시된다.
- 모바일/데스크톱 레이아웃이 깨지지 않는다.

### Phase 2: Power BI 상세 완성

범위:

- 서버 endpoint에서 `powerbi_reports` 조회
- Power BI Embed Token 동적 발급
- Power BI JS SDK 렌더
- `processing`, `failed`, `external_only`, `supported` 상태 UI
- embed 실패 fallback

완료 기준:

- 비로그인 방문자가 Microsoft 로그인 없이 embedded report를 조작할 수 있다.
- token/secret이 클라이언트 저장소와 HTML source에 남지 않는다.

### Phase 3: P1 콘텐츠와 레퍼런스

범위:

- `/references/powerbi`
- 레퍼런스 정렬과 더 보기
- `/powerbi` 콘텐츠 허브
- 큐레이션 CSV를 JSON 모듈 또는 정적 asset으로 변환

완료 기준:

- 현재 Power BI-first 노출 정책과 일치한다.
- 원본 URL, 출처, 발행일이 명확히 보인다.

### Phase 4: Auth와 참여 기능

범위:

- 로그인/회원가입/비밀번호 재설정
- 온보딩 정책 동의
- 좋아요
- 댓글/답글
- 신고 접수

완료 기준:

- 기존 Supabase 사용자가 Svelte 앱에서도 로그인할 수 있다.
- RLS 우회 없이 mutation이 동작한다.
- 댓글 알림 생성이 유지된다.

### Phase 5: 제작자 기능

범위:

- 프로젝트 등록/수정/삭제
- 임시저장
- 썸네일 업로드
- PBIX 업로드/게시
- My Page

완료 기준:

- Streamlit Submit/Edit과 동등한 데이터 검증을 제공한다.
- PBIX 실패 시 기존 프로젝트 보존 정책을 지킨다.
- 자동 캡처는 별도 Worker/API에서 처리한다.

### Phase 6: 운영 기능과 전환 마감

범위:

- Admin
- Notifications
- 커뮤니티 게시판
- 도메인 라우팅 전환
- Streamlit read-only 또는 운영 백업화

완료 기준:

- 새 도메인에서 핵심 사용자 흐름이 Svelte로 처리된다.
- Streamlit로 남은 기능이 명확히 제한된다.
- 롤백 경로가 문서화되어 있다.

---

## 11. 검증 계획

### 데이터 검증

- 홈 snapshot의 프로젝트 수, 인기 태그, 각 레일 ID가 Streamlit과 일치하는지 비교한다.
- 상세 snapshot의 제목, 본문, 작성자, 좋아요 수, 댓글 수가 Streamlit과 일치하는지 비교한다.
- 삭제/비공개 프로젝트가 공개 Svelte 화면에 노출되지 않는지 확인한다.

### UX 검증

- 모바일 360px, 태블릿 768px, 데스크톱 1440px에서 홈/상세를 확인한다.
- 카드 제목 2줄, 요약 1줄, 태그 최대 4개 규칙을 유지한다.
- 대표 결과물 iframe/embedded 영역의 aspect ratio와 fallback 문구를 확인한다.

### 보안 검증

- anon key 외 secret이 클라이언트 번들에 들어가지 않는지 확인한다.
- Power BI Embed Token이 저장되지 않는지 확인한다.
- RLS 정책으로 비공개/삭제 프로젝트 접근이 막히는지 확인한다.
- 댓글/좋아요/신고 mutation이 타 사용자 ID로 실패하는지 확인한다.

---

## 12. 주요 리스크와 대응

| 리스크 | 영향 | 대응 |
|---|---|---|
| Streamlit `session_state` 의존 흐름 재구현 | Auth/폼 이전 비용 증가 | 공개 조회부터 이전하고 Auth는 별도 phase |
| RPC 응답과 Svelte 타입 불일치 | 화면 오류 | Phase 0에서 샘플 payload와 타입 테스트 작성 |
| Power BI token 처리 실수 | secret/token 노출 | 서버 endpoint만 허용, 응답/로그 점검 |
| PBIX/캡처 런타임 제약 | 업로드 실패 | Worker/API 분리 |
| 큐레이션 CSV 처리 방식 혼재 | 콘텐츠 허브 유지보수 난이도 증가 | P1에서 `ContentItem` 변환 계약 고정 |
| 두 앱 병행 운영 중 URL 혼란 | 사용자 이탈 | 경로 매핑과 canonical URL을 먼저 정의 |

---

## 13. 우선 의사결정 필요 항목

1. SvelteKit 배포 대상: Cloudflare Pages, Vercel, Fly.io 중 선택
2. Svelte 앱 위치: monorepo 내부 `svelte_app/` 또는 별도 repo
3. Power BI embed endpoint 런타임: SvelteKit server route 또는 별도 API
4. 콘텐츠 CSV 변환 방식: 빌드 타임 JSON 또는 Supabase `contents` 테이블
5. 도메인 전환 방식: 서브도메인 검증 후 루트 전환 또는 path 단위 proxy

---

## 14. 최초 구현 전 체크리스트

Svelte 구현을 시작하기 전 아래가 완료되어야 한다.

- [ ] `home_project_snapshot` 실제 응답 샘플 확보
- [ ] `project_detail_snapshot` 실제 응답 샘플 확보
- [ ] `ProjectCard`, `ProjectDetail`, `HomeSnapshot` 타입 확정
- [ ] 공개 조회에서 필요한 Supabase RLS 재검증
- [ ] 홈/상세 모바일 기준 스크린샷 또는 레이아웃 기준 확정
- [ ] Power BI embed server boundary 확정
- [ ] Svelte 배포 타깃과 앱 디렉터리 결정

