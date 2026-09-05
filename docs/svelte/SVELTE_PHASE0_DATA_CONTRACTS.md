# Svelte Phase 0 데이터 계약 점검

- 작성일: 2026-08-24
- 기준 브랜치: `docs/svelte-migration-prd`
- 목적: Svelte 구현 전에 홈/상세/콘텐츠 흐름이 의존하는 실제 Streamlit 서비스, Supabase RPC, 스키마 계약을 고정한다.

---

## 1. Phase 0 범위

Phase 0은 구현 스파이크가 아니라 계약 고정 단계다.

완료해야 할 일:

1. 홈 공개 조회가 사용하는 RPC와 fallback 경로 확인
2. 상세 공개 조회가 사용하는 RPC와 fallback 경로 확인
3. 카드/상세/댓글/신고/Power BI embed 타입 후보 확정
4. Svelte에서 클라이언트 직접 호출 가능한 작업과 서버 endpoint가 필요한 작업 분리
5. 실데이터 샘플 확보 방식 정의

이번 점검에서는 코드와 스키마 기준 계약을 확정했다. 운영 Supabase에서 실제 payload를 파일로 저장하는 작업은 다음 단계에서 진행한다.

2026-08-24 원격 Supabase 확인 결과:

- `home_project_snapshot(limit=6, tag_limit=40, platform_key='powerbi')`는 정상 호출됐다.
- Power BI scope 총 프로젝트 수는 101개였다.
- 홈 payload는 `recent=6`, `viewed=6`, `liked=1`, `popular_tags=40` 형태로 내려왔다.
- 공개 프로젝트 하나(`dd1ed00c-1458-4f8e-92cb-4f31e319625d`)로 상세 RPC를 확인했다.
- 원격 `project_detail_snapshot` 응답에는 로컬 `schema.sql`과 달리 `platform_key`가 빠져 있었다. Svelte P0 전에 원격 RPC 재적용 또는 클라이언트 fallback 처리가 필요하다.
- 전용 패치 파일은 `supabase/update_project_detail_snapshot_platform_key.sql`이다.

---

## 2. 홈 공개 조회 계약

현재 Streamlit 홈 기본 진입은 `folio_app/pages/home.py`에서 아래 조건일 때 fast path를 탄다.

```text
검색어 없음
태그가 전체
플랫폼 scope가 기본 Power BI
```

이때 호출:

```python
list_home_project_snapshot(
    limit=6,
    tag_limit=40,
    platform_key="powerbi",
)
```

서비스는 먼저 RPC를 호출하고 실패하면 테이블 조회 fallback으로 내려간다.

```text
home_project_snapshot
  -> 성공: RPC payload 사용
  -> 실패: projects / likes / public_profiles / comments 조회 조합
```

### RPC

```sql
public.home_project_snapshot(
  p_limit integer default 6,
  p_tag_limit integer default 10,
  p_like_sample_limit integer default 120,
  p_platform_key text default null
)
returns jsonb
```

Svelte P0 기본 요청:

```json
{
  "p_limit": 6,
  "p_tag_limit": 40,
  "p_like_sample_limit": 120,
  "p_platform_key": "powerbi"
}
```

### 응답 형태

```ts
type HomeSnapshot = {
  total_project_count: number;
  popular_tags: string[];
  recent_projects: ProjectCard[];
  viewed_projects: ProjectCard[];
  liked_projects: ProjectCard[];
};
```

현재 테스트가 보장하는 최소 payload:

```json
{
  "total_project_count": 2,
  "popular_tags": ["Power BI", "분석"],
  "recent_projects": [{ "id": "recent-1" }],
  "viewed_projects": [{ "id": "viewed-1" }],
  "liked_projects": [{ "id": "liked-1" }]
}
```

실제 RPC의 카드 payload는 `supabase/schema.sql`의 `project_cards` CTE가 만든다.

```ts
type ProjectCard = {
  id: string;
  author_id: string;
  title: string;
  one_liner: string | null;
  problem: string | null;
  dataset: string | null;
  process: string | null;
  insights: string | null;
  tags: string[];
  thumbnail_url: string | null;
  power_bi_url: string | null;
  report_url: string | null;
  github_url: string | null;
  platform_key: 'powerbi' | 'tableau' | 'datastudio' | 'streamlit' | null;
  project_type: ProjectType;
  status: ProjectStatus;
  embed_status: EmbedStatus;
  is_public: boolean;
  view_count: number;
  created_at: string;
  updated_at: string;
  author: PublicAuthor | Record<string, never>;
  like_count: number;
  comment_count: number;
  latest_comment_at?: string | null;
};
```

주의:

- 카드 렌더에는 `problem`, `dataset`, `process`, `insights`가 반드시 필요하지 않지만 현재 RPC가 포함한다.
- 홈 기본 scope는 Power BI-first다. Svelte P0도 `powerbi`를 기본으로 맞춘다.
- 검색/태그 필터는 현재 전체 공개 프로젝트를 받아 앱 메모리에서 필터링한다. Svelte P0에서는 데이터 수가 작다는 전제에서 같은 방식을 쓸 수 있지만, P1 이후에는 검색 RPC를 검토한다.
- 실제 홈 payload에는 `latest_comment_at`도 포함된다.

---

## 3. 상세 공개 조회 계약

현재 상세는 `folio_app/pages/project_detail.py`에서 홈과 레퍼런스가 함께 사용한다.

호출:

```python
get_project(project_id)
```

서비스 경로:

```text
project_detail_snapshot
  -> 성공: RPC payload 사용
  -> 실패: projects row + public_profiles + likes + comments 조합
  -> status == deleted 이면 None 처리
```

### RPC

```sql
public.project_detail_snapshot(p_project_id uuid)
returns jsonb
```

요청:

```json
{
  "p_project_id": "project-uuid"
}
```

### 응답 형태

```ts
type ProjectDetail = ProjectCard & {
  author_id: string;
  is_public: boolean;
};
```

현재 테스트가 보장하는 최소 payload:

```json
{
  "id": "project-1",
  "title": "상세",
  "author": { "name": "작성자" },
  "like_count": 1,
  "comment_count": 0
}
```

실제 상세 표시 순서:

1. 상세 hero: `title`, `one_liner`, 카드 preview
2. hero footer: 작성자, 소속, 등록일, 조회수, 댓글 수, 공개 상태, 링크 복사, 좋아요, 신고, 작성자 액션
3. 대표 결과물: `status`, `project_type`, `power_bi_url`, `report_url`, `github_url`, `powerbi_reports`
4. 프로젝트 리포트: `problem`, `dataset`, `process`, `insights`
5. 댓글
6. 목록 복귀 버튼
7. 조회수 RPC

주의:

- 현재 상세는 `project_detail_snapshot`에 `powerbi_reports`를 포함하지 않는다.
- Power BI Embedded Viewer는 상세 렌더 중 별도 서비스 `get_powerbi_embed_config(project["id"])`로 처리한다.
- Svelte에서는 상세 데이터와 Power BI embed token을 분리해야 한다.
- 로컬 `schema.sql` 기준 상세 RPC는 `platform_key`를 포함하지만, 2026-08-24 원격 확인에서는 상세 응답에 `platform_key`가 없었다. Svelte P0 구현 전 원격 스키마 적용 여부를 확인한다.
- 이 갭은 `supabase/update_project_detail_snapshot_platform_key.sql`로 원격 DB에 적용한다.
- 레거시 프로젝트는 `project_type='other'`여도 `power_bi_url`이 있으면 Power BI 결과물로 표시될 수 있다. Svelte 상세는 `project_type`만 믿지 말고 `power_bi_url`/URL marker도 함께 본다.

---

## 4. 조회수 계약

현재 상세 렌더 후 `_record_project_view(project_id)`가 호출된다.

RPC:

```sql
public.increment_project_view_count(
  project_id_input uuid,
  anonymous_viewer_id_input uuid
)
returns boolean
```

동작:

- 공개 프로젝트만 집계한다.
- 로그인 작성자 본인의 조회는 집계하지 않는다.
- 로그인 사용자는 `auth.uid()`를 우선한다.
- 비로그인은 익명 UUID를 `anonymous_viewer_id_input`으로 전달한다.
- 한국 시간 날짜 기준으로 같은 viewer/project/day 중복을 막는다.
- 원본 사용자 ID, 익명 UUID, IP, User-Agent는 `project_views`에 저장하지 않는다.

Svelte P0 결정:

- 비로그인 상세 진입 시 브라우저에 익명 UUID를 생성해 보관한다.
- 저장 위치는 `localStorage` 또는 cookie 중 하나로 정한다.
- 쿠키를 쓰면 도메인 전환과 개인정보 고지 문구를 함께 검토한다.

---

## 5. Enum 계약

현재 enum 후보는 `folio_app/services/project_normalizers.py`와 `supabase/schema.sql`이 일치한다.

```ts
type ThumbnailMode = 'auto_cover' | 'manual_url' | 'capture' | 'upload';

type ProjectType =
  | 'powerbi'
  | 'tableau'
  | 'looker'
  | 'streamlit'
  | 'notebook'
  | 'html_report'
  | 'markdown_report'
  | 'web'
  | 'other';

type ProjectStatus = 'processing' | 'published' | 'failed' | 'deleted';

type EmbedStatus = 'supported' | 'external_only' | 'failed';

type PlatformKey = 'powerbi' | 'tableau' | 'datastudio' | 'streamlit';
```

주의:

- Python normalizer는 입력값 `other`를 platform 후보로 받지만 DB `projects.platform_key`에는 `other`를 저장하지 않고 `null`로 저장한다.
- 폼 미리보기 태그는 최대 5개를 보여주지만, 저장 normalizer는 최대 10개를 보존한다.
- `tags_with_platform()`은 선택한 플랫폼 라벨을 태그 맨 앞에 자동 추가한다.

---

## 6. 공개 작성자 계약

현재 공개 화면은 `public_profiles` view를 사용한다.

```ts
type PublicAuthor = {
  id: string;
  name: string;
  organization: string | null;
  avatar_url?: string | null;
};
```

주의:

- 현재 RPC의 author object는 `id`, `name`, `organization`만 포함한다.
- `public_profiles` view 자체에는 `avatar_url`이 있다.
- Svelte 카드/상세에서 avatar가 필요하면 RPC 확장 또는 별도 조회가 필요하다.

---

## 7. 댓글 계약

현재 댓글 조회:

```python
list_project_comments(project_id)
  -> comments.select("*").eq("project_id", project_id).order("created_at")
  -> public_profiles.select("id, name")로 작성자 attach
```

타입:

```ts
type CommentItem = {
  id: string;
  project_id: string;
  author_id: string;
  parent_id: string | null;
  body: string;
  depth: 0 | 1;
  is_deleted: boolean;
  created_at: string;
  updated_at: string;
  author: {
    id?: string;
    name?: string;
  };
};
```

쓰기 규칙:

- 로그인 필요
- 본문은 trim 후 1~1000자
- 답글은 같은 프로젝트의 depth 0 댓글 아래에만 가능
- DB trigger `validate_comment_thread()`가 depth와 parent를 최종 검증한다.
- 작성 후 `notifications(type='project_comment')` 생성 시도

Svelte P2 결정:

- P0 상세에서는 댓글 수만 표시하고 댓글 목록은 P2로 미룰 수 있다.
- 댓글 목록을 P0에 포함하려면 공개 select만 먼저 구현하고 작성 UI는 숨긴다.

---

## 8. 신고 계약

테이블:

```text
content_reports
```

타입:

```ts
type ContentReportReason =
  | 'embed_broken'
  | 'wrong_content'
  | 'inappropriate'
  | 'other';

type ContentReportStatus =
  | 'open'
  | 'reviewing'
  | 'resolved'
  | 'dismissed';
```

쓰기 규칙:

- 로그인 필요
- `details`는 공백 정규화 후 최대 500자
- 사용자는 공개 프로젝트 또는 본인 프로젝트에 대해서만 신고 가능
- 신고 row는 프로젝트 소유자에게 직접 노출하지 않는다.
- Admin만 신고 목록을 조회/상태 변경한다.

---

## 9. Power BI Embedded 계약

현재 상세 대표 결과물 분기:

```text
status == processing -> 안내 메시지
status == failed -> 실패 메시지
project_type == powerbi -> get_powerbi_embed_config(project.id)
  -> 성공: Power BI JS SDK viewer
  -> 실패 또는 없음: power_bi_url iframe fallback
power_bi_url 있음 -> iframe fallback
report_url/github_url 있음 -> 외부 액션 버튼
```

Svelte endpoint 후보:

```text
GET /api/projects/:id/powerbi-embed
```

응답:

```ts
type PowerBIEmbedConfig = {
  report_id: string;
  embed_url: string;
  embed_token: string;
};
```

서버 규칙:

- `powerbi_reports`는 공개 프로젝트 또는 작성자 본인 프로젝트에 대해서만 조회한다.
- Power BI Client Secret은 서버 환경변수로만 읽는다.
- Embed Token은 요청 시 발급하고 저장하지 않는다.
- 실패하면 상태 코드와 사용자 표시용 메시지를 분리한다.

---

## 10. Power BI 콘텐츠 허브 계약

현재 `folio_app/services/powerbi_content.py`는 CSV를 읽어 `PowerBIContent`로 묶는다.

입력 파일:

```text
docs/curation/powerbi_desktop_download/all.csv
docs/curation/powerbi_updates/all.csv
docs/curation/powerbi_changelog/all.csv
docs/curation/powerbi_learning_videos/all.csv
docs/curation/powerbi_update_videos/all.csv
docs/curation/powerbi_learning_programs/all.csv
docs/curation/powerbi_community_blog/all.csv
```

Svelte P1 타입:

```ts
type ContentItem = {
  id: string;
  content_type:
    | 'desktop_download'
    | 'update'
    | 'changelog'
    | 'community_blog'
    | 'learning_video'
    | 'update_video'
    | 'learning_program';
  title: string;
  title_ko?: string | null;
  summary?: string | null;
  summary_ko?: string | null;
  source: string;
  source_url: string;
  thumbnail_url?: string | null;
  published_at?: string | null;
  collected_at?: string | null;
  category?: string | null;
  topic?: string | null;
};
```

결정 필요:

- P1에서는 CSV를 빌드 타임 JSON으로 변환할지, Supabase `contents` 테이블을 만들지 결정해야 한다.
- 현재 운영 원칙은 원문 복제가 아니라 제목, 요약, 출처, URL 중심의 최소 저장이다.

---

## 11. Svelte에서 직접 호출 가능한 것과 서버 전용 작업

### 클라이언트 직접 호출 가능

| 작업 | 근거 |
|---|---|
| `home_project_snapshot` | anon execute grant |
| `project_detail_snapshot` | anon execute grant |
| 공개 `projects` select | RLS: `is_public=true and status='published'` |
| `public_profiles` select | anon/authenticated grant |
| 공개 댓글 select | visible project 기준 RLS |
| 로그인 좋아요 insert/delete | RLS: `user_id = auth.uid()` |
| 로그인 댓글 insert/delete | RLS + trigger |
| 로그인 신고 insert | RLS |

### 서버 endpoint 또는 Worker 필요

| 작업 | 이유 |
|---|---|
| Power BI Embed Token 발급 | Client Secret 서버 전용 |
| PBIX Import / polling | Power BI API secret, 긴 작업 |
| 썸네일 이미지 최적화 | 파일 처리와 Storage 정책 |
| 자동 캡처 | Chromium/Playwright 런타임 |
| 이메일 알림 | SMTP secret 서버 전용 |
| Admin service role 작업 | 권한 상승 작업 |
| 콘텐츠 수집/GitHub Actions 트리거 | 운영 secret과 repository write 권한 |

---

## 12. 실데이터 샘플 확보 계획

다음 단계에서 아래 파일을 생성한다.

```text
docs/contracts/samples/home_project_snapshot.powerbi.sample.json
docs/contracts/samples/project_detail_snapshot.sample.json
```

샘플 생성 원칙:

- Supabase key, 이메일, 비밀정보를 포함하지 않는다.
- 실제 UUID와 URL은 공개 프로젝트 기준이면 유지 가능하다.
- 개인 이메일은 `public_profiles` view에 없어야 한다.
- 필요하면 title/url을 익명화하되 필드 shape는 유지한다.

권장 명령 후보:

```powershell
python tools\profile_home_snapshot.py --warm-runs 0
```

상세 샘플은 공개 프로젝트 ID 하나를 확보한 뒤 별도 작은 도구 또는 임시 Python one-liner로 `get_project(project_id)` 결과를 JSON 저장한다.

샘플 저장 전 선행 확인:

- `project_detail_snapshot` 원격 응답에 `platform_key`가 포함되는지 확인
- 샘플에 공개되지 않아야 할 작성자 정보가 없는지 확인
- `latest_comment_at`을 ProjectCard 타입에 포함할지 optional로 둘지 확정

---

## 13. Phase 0 남은 결정

1. 익명 visitor ID 저장 위치: cookie 또는 localStorage
2. Svelte P0에서 댓글 목록을 표시할지, 댓글 수만 표시할지
3. Power BI embed endpoint를 SvelteKit server route로 둘지 별도 API로 둘지
4. CSV 콘텐츠를 JSON 변환으로 시작할지 `contents` 테이블로 승격할지
5. `public_profiles.avatar_url`을 홈/상세 RPC에 포함할지
6. 원격 `project_detail_snapshot`을 최신 `schema.sql`과 맞출지, Svelte에서 `platform_key` 누락 fallback을 둘지
