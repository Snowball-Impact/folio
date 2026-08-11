# FOLIO MVP PRD

## 데이터 시각화 프로젝트 발견, 체험, 게시 커뮤니티

- 문서 버전: MVP 통합본 v1.0
- 제품 단계: MVP 재정렬
- 작성일: 2026-08
- 통합 출처: `docs/legacy/FOLIO_Data_Visualization_Community_PRD_v1.1.md` + `docs/legacy/PRD.md`
- 현재 제품 기준 문서: 이 문서

---

## 0. Codex 작업 원칙

구현 전에 반드시 현재 Repository를 먼저 분석한다.

1. 디렉터리 구조와 주요 모듈을 확인한다.
2. 현재 Supabase Auth, RLS, 프로젝트 모델, 댓글, 알림, 배포 구조를 확인한다.
3. 기존 기능과 코드를 최대한 재사용한다.
4. PRD와 기존 구현이 충돌하면 임의로 대규모 리팩터링하지 않는다.
5. 충돌과 변경 필요사항을 먼저 보고한 뒤 최소 변경으로 구현한다.
6. 각 Sprint는 독립적으로 실행, 검증 가능한 단위로 개발한다.
7. MVP 수요 검증에 필요하지 않은 기능은 선행 개발하지 않는다.

원칙: **Simple is Best.**

---

## 1. 제품 개요

FOLIO는 데이터 시각화 프로젝트를 발견하고, 직접 체험하며, 제작자가 자신의 프로젝트를 게시하고, 사용자들이 의견을 나누는 커뮤니티다.

v1.5는 두 흐름을 함께 다룬다.

1. **Power BI 제품화 흐름**
   - Power BI Embedded Viewer
   - PBIX 기반 프로젝트 게시
   - 프로젝트 상태 처리
   - 대표 썸네일 업로드

2. **Visual Gallery 흐름**
   - Tableau, Streamlit, Looker Studio, Power BI 공개 프로젝트 탐색
   - 주제와 플랫폼 기반 발견
   - 프로젝트 상세, 원본 링크, 댓글
   - 향후 실무 콘텐츠 Feed

최종 목표는 완성형 플랫폼이 아니라 다음 질문을 검증하는 것이다.

> 사람들은 FOLIO에서 다른 사람의 데이터 시각화 프로젝트를 발견하고, 직접 체험하고, 다시 방문하는가?

---

## 2. 제품 비전

AI 시대에도 사람의 질문과 해석은 중요한 자산이다.

FOLIO는 프로젝트 파일이나 링크만 모으는 공간이 아니라, 데이터 시각화 프로젝트의 문제의식, 분석 과정, 인터랙티브 결과물, 사용자 의견을 함께 축적한다. 장기적으로 데이터 시각화에서 시작해 AI 데이터 앱, 분석형 웹서비스, 실무 콘텐츠 큐레이션까지 확장한다.

---

## 3. 검증 가설

- **H1 Project Discovery:** 사용자는 다른 사람의 데이터 시각화 프로젝트를 발견하기 위해 FOLIO를 방문하는가?
- **H2 Interactive Visualization:** 실제 인터랙티브 대시보드가 프로젝트 탐색 가치를 높이는가?
- **H3 Creator Supply:** 제작자는 자신의 프로젝트를 직접 등록하는가?
- **H4 Community:** 사용자는 프로젝트에 질문, 의견, 피드백을 남기는가?
- **H5 Recurring Content:** 업데이트, 행사, 자격, 공모전, 채용 콘텐츠가 재방문을 만드는가?

---

## 4. 핵심 사용자

### 콘텐츠 탐색자

우수한 데이터 시각화 사례, 대시보드 구조, 분석 주제, 구현 아이디어를 찾는 사용자다.

### 학습자와 취업 준비생

Power BI, Tableau, Looker Studio, Streamlit 사례를 참고해 포트폴리오와 프로젝트 주제를 찾는다.

### 프로젝트 제작자

자신의 Power BI, Tableau, Streamlit, 웹 앱 프로젝트를 공개하고 피드백과 외부 유입을 얻고 싶어 한다.

### 실무자와 기업

BI 사례, 데이터 시각화 인재, 실무 콘텐츠, 행사와 채용 정보를 찾는다.

---

## 5. 현재 문제

### 초기 콘텐츠와 제작자 공급이 모두 어렵다

신규 플랫폼은 콘텐츠가 부족하면 방문자가 줄고, 방문자가 없으면 제작자가 등록할 이유가 약해진다. 따라서 초기에는 공개 레퍼런스 콘텐츠와 제작자 직접 등록을 함께 다룬다.

### 공개 프로젝트는 플랫폼별로 흩어져 있다

Tableau Public, Streamlit Gallery, Looker Studio Gallery, Power BI 공개 보고서는 각 플랫폼 안에 분산되어 있다. 사용자는 주제와 문제 중심으로 비교하기 어렵다.

### Power BI 프로젝트 게시 장벽이 높다

제작자는 PBIX, Workspace, Dataset, Report ID, Embed URL, Publish to web, Embedded 차이를 잘 모를 수 있다. FOLIO는 사용자가 Power BI 내부 기술 ID를 직접 다루지 않게 해야 한다.

### 파일형 산출물 등록 경로가 필요하다

Markdown, Notebook, HTML 리포트는 데이터 분석과 시각화 프로젝트에서 자주 쓰인다. FOLIO는 실행 환경을 직접 제공하기보다 안전하게 업로드, 링크, 읽기 전용 표시를 지원해야 한다.

### 임베드 실패는 정상 상태다

플랫폼과 프로젝트 설정에 따라 iframe 렌더링이 불가능할 수 있다. FOLIO는 `processing`, `published`, `failed`, `external_only` 같은 상태를 명확히 보여줘야 한다.

---

## 6. 제품 전략

v1.5의 우선순위는 **Power BI Embedded 제품화**와 **볼 만한 갤러리 경험 유지**다.

1. 기존 FOLIO의 Supabase Auth, 프로젝트 등록, 상세, 댓글 구조를 유지한다.
2. 먼저 검증 가능한 Power BI 보고서 1개를 Embedded 방식으로 실제 배포 환경에서 렌더링한다.
3. 이후 `powerbi_reports` 같은 최소 DB 구조를 추가한다.
4. 썸네일은 자동캡처보다 사용자 업로드를 우선한다.
5. PBIX Publisher는 Embedded Viewer 검증 후 단계적으로 구현한다.
6. 기존 큐레이션 레퍼런스는 홈/레퍼런스 탐색의 콘텐츠 기반으로 유지한다.

---

## 7. 인프라와 운영 제약

MVP는 Supabase Free Tier 범위 내 운영을 기본 원칙으로 한다.

고려 한도:

- Database: 500MB
- File Storage: 1GB
- MAU: 50,000
- Project: 최대 2개

운영 원칙:

1. PostgreSQL에는 구조화 데이터와 메타데이터 중심으로 저장한다.
2. PBIX를 Supabase Storage에 영구 보관하지 않는다.
3. 외부 콘텐츠 원문 HTML, 대용량 본문, 이미지 바이너리를 복제하지 않는다.
4. 콘텐츠는 제목, 요약, 출처, URL, 날짜 등 필요한 최소 데이터만 저장한다.
5. 썸네일은 저장 전 리사이징/압축한다.
6. 사용량이 70%에 도달하면 점검하고, 85%에 도달하면 정리 또는 유료 전환을 판단한다.

---

## 8. 목표 아키텍처

```text
Users
  ↓
FOLIO / Streamlit Community Cloud
  ├──────────────→ Power BI REST API / Embedded
  ↓
Supabase
├─ PostgreSQL
├─ Auth
└─ Storage (Thumbnail)
  ↑
Local Windows Worker / Future Worker
└─ Python ETL
```

역할:

- **FOLIO**: UI, 갤러리, 상세, 등록, 댓글, Power BI Embedded Viewer
- **Supabase**: 인증, PostgreSQL, RLS, 썸네일 Storage
- **Power BI**: PBIX Import, Report, Semantic Model, Embed Token, Interactive Rendering
- **Worker**: 향후 콘텐츠 수집, 썸네일 처리, 정제, 중복 제거, 로그

현재 무료 배포 채널은 Streamlit Community Cloud다. Power BI Embedded/PBIX 처리, Chrome 실행, 배치 수집의 안정성이 Community Cloud 한계를 넘으면 앱 전체 이전보다 캡처·수집 worker를 Cloud Run, Azure, Render Cron 같은 별도 런타임으로 분리하는 방식을 먼저 검토한다.

---

## 9. 핵심 사용자 흐름

### Visitor

```text
FOLIO
→ 프로젝트 갤러리 또는 레퍼런스
→ 프로젝트 상세
→ Interactive Dashboard
→ 프로젝트 설명과 출처
→ 댓글 또는 다른 프로젝트 탐색
```

### Creator

```text
로그인
→ 프로젝트 등록
→ 프로젝트 유형 선택
→ 프로젝트 정보 + 썸네일 입력
→ Power BI인 경우 PBIX 업로드
→ processing
→ published 또는 failed
```

### Future Content Consumer

```text
FOLIO
→ Feed
→ 업데이트 / 행사 / 자격 / 공모전 / 채용
→ 원문 또는 관련 프로젝트 탐색
```

---

## 10. 정보 구조

### 홈

- 서비스 소개 Hero
- 최근 프로젝트
- 조회수 높은 프로젝트
- 좋아요 많은 프로젝트
- 플랫폼 필터
- 일반 프로젝트 기반 인기 태그
- 프로젝트 등록 CTA

### 레퍼런스

- Tableau
- Power BI
- Data Studio / Looker Studio
- Streamlit
- 플랫폼별 카드 목록과 상세

### 프로젝트 상세

```text
Hero
→ Interactive Preview / Embedded Report
→ Project Summary
→ Data & Analysis
→ Source & Links
→ Comments
```

### 프로젝트 등록

- 제목
- 설명
- 프로젝트 유형
- 태그
- 대표 썸네일
- Power BI 선택 시 PBIX
- HTML Report 선택 시 HTML 파일
- Markdown Report 선택 시 Markdown 파일 또는 URL
- GitHub URL
- 소셜미디어 링크
- 기타 URL

### Feed (후속)

- Power BI / Fabric 업데이트
- Tableau / Looker 업데이트
- 데이터 시각화 뉴스
- 행사 / Webinar
- 자격 / 시험 일정
- 공모전
- 채용

---

## 11. 데이터 모델 방향

현재 구현과 Supabase 스키마를 우선 재사용한다. 새 컬럼과 테이블은 필요성이 확인된 뒤 최소 범위로 추가한다.

### profiles

기존 Supabase Auth 및 `profiles` 구조를 유지한다.

### projects

현재 필드를 유지하되 다음 개념을 단계적으로 추가한다.

```text
id
author_id or user_id
title
description or one_liner
project_type
thumbnail_url
github_url
social_links
external_url
embed_url or power_bi_url
status
created_at
updated_at
published_at
deleted_at
```

`project_type` 후보:

```text
powerbi
tableau
looker
streamlit
notebook
html_report
markdown_report
web
other
```

MVP `status` 후보:

```text
processing
published
failed
deleted
```

필요성이 확인될 때만 `draft`, `review`, `hidden`을 추가한다.

### powerbi_reports

Power BI Embedded/PBIX Publisher를 위해 추가한다.

```text
id
project_id
workspace_id
report_id
dataset_id
embed_url
import_id
import_status
created_at
updated_at
```

Client Secret과 장기 Embed Token은 저장하지 않는다.

### comments

기존 댓글 구현을 우선 재사용한다. MVP 관점에서는 댓글 작성, 수정, 삭제, 작성일, 수정됨 표시, 관리자 사후 삭제가 핵심이다.

### contents (Future)

```text
id
content_type
title
summary
source
source_url
source_id
thumbnail_url
published_at
collected_at
status
created_at
updated_at
```

---

## 12. 썸네일 정책

프로젝트 등록 시 대표 썸네일 업로드를 우선한다.

```text
User Image Upload
→ Format / Size Validation
→ Resize
→ Compression
→ Supabase Storage
→ thumbnail_url
→ projects
```

MVP 정책:

- JPG, PNG, WebP 허용
- 원본 업로드 크기 상한 설정
- 저장 전 리사이징/압축
- 최종 저장 파일은 가급적 500KB 이하 목표
- 자동 대시보드 캡처는 MVP 필수 기능에서 제외
- 프로젝트 영구 삭제 시 연결 썸네일도 정리

현재 자동캡처 코드가 존재하더라도, Power BI/PBIX MVP의 핵심 완료 조건으로 보지 않는다.

---

## 13. Power BI Embedded Viewer

### 목표

기존 검증 가능한 Power BI 프로젝트를 FOLIO 상세페이지에 Embedded 방식으로 연결하여 실제 배포 환경에서 기술 검증을 완료한다.

```text
Visitor
→ Project Detail
→ Server-side Power BI Authentication
→ Generate Embed Token
→ reportId + embedUrl + token
→ Power BI JS SDK
→ Interactive Report
```

환경변수:

```text
POWERBI_TENANT_ID
POWERBI_CLIENT_ID
POWERBI_CLIENT_SECRET
POWERBI_WORKSPACE_ID
```

요구사항:

- Client Secret은 서버에서만 사용한다.
- Embed Token은 요청 시 동적 발급한다.
- Embed Token은 DB에 영구 저장하지 않는다.
- 비로그인 방문자도 Microsoft 로그인 없이 보고서를 열람할 수 있어야 한다.
- 실패 시 빈 화면 대신 오류 UI를 제공한다.

Acceptance Criteria:

- 실제 배포된 FOLIO에서 렌더링된다.
- Chrome 시크릿 창에서 정상 표시된다.
- 필터 등 기본 인터랙션이 정상 작동한다.
- Microsoft 로그인이 필요 없다.
- Client Secret이 클라이언트에 노출되지 않는다.

---

## 14. PBIX Publisher

### 목표

일반 사용자가 Power BI 내부 구조를 몰라도 PBIX를 통해 프로젝트를 등록할 수 있도록 한다.

사용자에게 입력시키지 않는 값:

- Workspace ID
- Dataset ID
- Report ID
- Embed URL

처리 흐름:

```text
PBIX Upload
→ project.status = processing
→ Power BI Import API
→ Import Status Polling
→ Dataset ID
→ Report ID
→ Embed URL
→ powerbi_reports 저장
→ project.status = published
```

실패 흐름:

```text
Import Failure
→ project.status = failed
→ 오류 정보 제공
```

PBIX Storage Policy:

- PBIX는 영구 파일 저장소로 관리하지 않는다.
- 업로드 후 임시 처리한다.
- Power BI Import 성공 확인 후 PBIX 임시 원본을 삭제한다.
- Supabase Storage 1GB를 PBIX 보관 용도로 사용하지 않는다.
- MVP에서는 PBIX 교체와 버전 관리를 지원하지 않는다.

---

## 15. Power BI Workspace 정책

MVP에서는 FOLIO 전용 Workspace 1개를 사용한다.

```text
FOLIO Workspace
├─ Project A Report / Semantic Model
├─ Project B Report / Semantic Model
└─ Project C Report / Semantic Model
```

사용자별 Workspace는 만들지 않는다.

리소스 이름 충돌 방지를 위해 내부 Naming Convention을 사용한다.

권장 예:

```text
{project_id}_{original_name}
```

---

## 16. 게시와 삭제 정책

### Authentication

프로젝트 등록은 Supabase Auth 로그인 사용자만 가능하다.

### Publication

관리자 사전 승인 기능을 만들지 않는다.

일반 프로젝트:

```text
등록 성공
→ published
→ 갤러리 즉시 공개
```

Power BI 프로젝트:

```text
등록
→ processing
→ PBIX Import
→ Metadata 확보
→ 성공: published
→ 실패: failed
```

관리자는 사전 승인자가 아니라 사후 관리 역할만 가진다.

### Soft Delete

삭제는 즉시 물리 삭제하지 않고 Soft Delete를 기본으로 한다.

```text
User Delete
→ project.status = deleted
→ deleted_at 기록
→ FOLIO에서 즉시 숨김
```

Power BI Report와 Semantic Model은 즉시 삭제하지 않고 30일 복구 기간을 둔다. MVP에서는 자동 Cleanup Job을 반드시 구현하지 않아도 된다.

---

## 17. Visual Gallery와 큐레이션 정책

v1.5는 Power BI 제품화를 우선하지만, 기존 큐레이션 갤러리 흐름을 버리지 않는다.

초기 레퍼런스 소스:

- Tableau Public
- Streamlit Gallery
- Looker Studio / Data Studio Gallery
- 공개 Power BI 보고서

운영 원칙:

1. 원본 프로젝트, 제작자, 원본 플랫폼, 원본 URL을 명확히 표시한다.
2. 콘텐츠 전체를 복제하지 않는다.
3. FOLIO 편집 설명은 원본과 구분한다.
4. 임베드 실패는 정상 상태로 취급한다.
5. 플랫폼보다 주제와 문제를 우선한다.
6. 자동 수집보다 수동 검증과 운영 가능성 확인을 먼저 한다.

---

## 18. File Report 정책

Power BI 외 파일형 산출물은 프로젝트 등록 장벽을 낮추기 위해 단계적으로 지원한다.

### HTML Report

- HTML 파일 업로드를 허용한다.
- FOLIO 본문 DOM에 직접 삽입하지 않는다.
- Supabase Storage 또는 별도 저장소에 저장한 뒤 sandbox iframe으로 표시한다.
- 스크립트가 필요한 Plotly 등은 표시 가능성을 검증하되, 위험한 권한은 허용하지 않는다.

### Markdown Report

- Markdown 파일 업로드 또는 Markdown URL 등록을 허용한다.
- 렌더링 전 sanitize를 적용한다.
- 이미지와 외부 링크는 안전한 URL만 허용한다.

### Notebook

- MVP에서는 `.ipynb` 파일 실행과 서버 변환을 지원하지 않는다.
- GitHub 또는 nbviewer URL 등록을 우선한다.
- Notebook 파일 업로드/HTML 변환은 후순위 Todo로 둔다.

---

## 19. Community

기존 구현을 먼저 확인하고 없는 기능만 추가한다.

MVP:

- 댓글 작성
- 댓글 수정
- 댓글 삭제
- 작성일
- 수정됨 표시
- 관리자 사후 삭제

기존에 구현된 알림, 답글, 이메일 알림은 유지하되, PBIX MVP의 선행 조건으로 보지는 않는다.

후순위:

- 댓글 신고
- 구조화 댓글
- 팔로우
- DM
- 실시간 알림

---

## 20. Content Feed (후속)

프로젝트 외 재방문 이유를 만드는 콘텐츠 영역이다.

후보:

- Power BI / Fabric Update
- Tableau Update
- Looker Update
- 데이터 시각화 News
- 행사 / Webinar
- 자격 / 시험 일정
- 공모전
- BI / Data Visualization 채용

콘텐츠 원문 저장 서비스가 아니라 큐레이션/발견 서비스로 설계한다.

저장 데이터는 최소화한다.

```text
title
summary
source
source_url
content_type
published_at
thumbnail_url
```

초기에는 관리자 수동 등록도 허용한다.

---

## 21. Content ETL (후속)

ETL은 당분간 Windows PC 또는 별도 Worker에서 실행한다.

```text
Windows Task Scheduler / Worker
→ Python
→ Collector
→ Transform
→ Validation
→ Deduplication
→ Supabase PostgreSQL
→ FOLIO Feed
```

원칙:

- 수집 Source를 하나씩 추가한다.
- 하나의 Source를 End-to-End로 완성한 후 다음 Source를 개발한다.
- ETL 실행 환경과 서비스 DB를 분리한다.
- 향후 필요하면 Render Cron, Cloud Run, Azure 등으로 Worker만 이전한다.

---

## 22. Security

- Supabase Key, Power BI Secret 등 비밀정보 Git Commit 금지
- Power BI Client Secret은 서버 전용
- Embed Token 영구 저장 금지
- PBIX 장기 저장 금지
- HTML Report는 sandbox iframe으로만 표시
- Markdown은 sanitize 후 렌더링
- Notebook은 MVP에서 서버 실행 금지
- 업로드 파일 형식과 크기 검증
- Supabase Auth 기존 구조 유지
- RLS와 권한 정책은 최소 권한 적용
- 사용자가 소유한 프로젝트만 수정/삭제 가능해야 함
- 공개 게시 전 개인정보, 사내 데이터, 민감정보 포함 여부를 사용자에게 경고

---

## 23. Analytics

기존 GA 구조를 우선 활용한다.

후보 이벤트:

```text
project_view
dashboard_view
project_submit
comment_submit
search
feed_view
feed_click
powerbi_embed_load
powerbi_embed_success
powerbi_embed_error
pbix_upload
pbix_import_success
pbix_import_failed
```

제품적 성공 여부는 실제 행동 데이터와 사용자 피드백으로 판단한다.

---

## 24. UX Principles

1. UI는 간결하게 유지한다.
2. 프로젝트 자체가 화면의 중심이다.
3. 상세페이지는 기본 1열 구조를 우선한다.
4. Hero는 좌측 텍스트, 우측 대표 이미지를 기준으로 한다.
5. 상세는 대시보드, 보고서/설명, 댓글 순서를 따른다.
6. 사용자에게 Power BI 내부 기술 ID를 요구하지 않는다.
7. `processing`과 `failed` 상태를 명확히 표시한다.
8. 신규 기능 때문에 기존 프로젝트 유형 사용성을 훼손하지 않는다.
9. 등록 절차는 가능한 짧게 유지한다.
10. 관리자 승인 절차는 만들지 않는다.

---

## 25. MVP 제외 범위

- AI 추천/평가/챗봇
- 사용자 DM
- 팔로우
- Reputation 시스템
- 결제/광고
- PBIX 버전 관리
- PBIX 다운로드
- Power BI 자동 Refresh
- 사용자 DB Credential 관리
- Dataset Credential 자동 구성
- Gateway 자동 연결
- RLS 자동 설정
- DirectQuery 자동 구성
- Power BI 편집 기능
- Publish to Web 자동화
- Playwright/Selenium 기반 Power BI 게시 자동화
- GitHub OAuth 연동
- GitHub App 기반 자동 동기화
- private GitHub repository import
- Notebook 서버 실행/변환
- 복잡한 DW
- Kafka / Spark / Kubernetes
- 과도한 MSA
- 모든 콘텐츠 수집처 동시 개발
- 자동 썸네일 캡처를 MVP 필수 조건으로 삼는 것

---

## 26. Implementation Roadmap

### Sprint 0 - Repository Audit

```text
Repository 분석
→ 기존 Supabase/Auth 구조
→ 프로젝트 모델
→ 상세페이지
→ 등록 UI
→ 댓글/관리자 기능
→ 배포 구조
→ Power BI 통합 영향도
→ Gap Report
```

코드를 수정하기 전에 결과를 보고한다.

### Sprint 1 - Power BI Embedded Viewer

기존 검증 가능한 Power BI 프로젝트 1개를 실제 FOLIO 상세페이지에 연결한다.

Done: 실제 배포된 FOLIO에서 비로그인 방문자가 보고서를 조작할 수 있다.

### Sprint 2 - Database Foundation

기존 DB 구조를 최대한 유지하면서 `powerbi_reports`와 필요한 프로젝트 필드를 추가한다.

Done: Power BI 프로젝트 메타데이터가 Supabase에 안정적으로 저장/조회된다.

### Sprint 3 - Thumbnail Upload

썸네일 업로드, 검증, 최적화, Supabase Storage 저장, 프로젝트 연결을 구현한다.

Done: 프로젝트 등록 시 최적화된 대표 이미지가 저장되고 갤러리에 표시된다.

### Sprint 4 - PBIX Publisher

PBIX 업로드, Import, Polling, Report/Dataset/Embed Metadata 저장을 구현한다.

Done: 사용자가 Power BI 서비스에 직접 접속하지 않고 게시 가능한 상태가 된다.

### Sprint 5 - Registration UX

프로젝트 유형별 등록 흐름을 정리한다.

```text
프로젝트 정보
→ Thumbnail
→ Power BI 선택 시 PBIX
→ HTML Report 선택 시 HTML 파일
→ Markdown Report 선택 시 Markdown 파일 또는 URL
→ processing
→ 자동 published / failed
```

### Sprint 6 - Soft Delete / Recovery

삭제 즉시 숨김, 30일 복구 가능 구조를 만든다. 자동 Cleanup은 후순위다.

### Sprint 7 - Community

기존 구현 Gap만 보완한다.

### Sprint 8 - File Report Foundation

HTML Report와 Markdown Report의 업로드, 저장, 안전한 렌더링을 구현한다.

### Sprint 9 - Feed Foundation

`contents` 테이블, 관리자 수동 등록, Feed, Filter, Source 이동을 만든다.

### Sprint 10+ - ETL

가치와 난이도에 따라 Source를 하나씩 추가한다.

---

## 27. Current Priority

```text
1. Repository Audit
2. Power BI Embedded Viewer
3. Supabase DB 구조 보완
4. Thumbnail Upload
5. PBIX Publisher
6. Registration UX
7. Soft Delete / Recovery
8. HTML/Markdown Report Foundation
9. Community Gap 보완
10. Feed
11. Content ETL
```

콘텐츠 자동수집보다 **Power BI Embedded 제품화**를 우선한다. 단, 기존 레퍼런스 갤러리와 댓글 경험은 서비스 발견/체험 가설 검증을 위해 유지한다.

---

## 28. Todo

### Social Links

프로젝트 제작자와 관련 콘텐츠의 외부 접점을 넓히기 위해 소셜미디어 링크를 후속 기능으로 검토한다.

후보:

```text
Instagram
YouTube
Threads
Facebook
Blog / Brunch / Medium
LinkedIn
X
Kaggle
기타 개인 웹사이트
```

범위 원칙:

- 프로젝트 링크와 제작자 프로필 링크를 구분한다.
- MVP에서는 URL 입력과 안전한 외부 링크 표시부터 검토한다.
- 팔로우, 자동 임베드, 소셜 피드 수집은 후순위다.
- 사용자 입력 URL은 `http://` 또는 `https://`만 허용한다.

### GitHub URL Import

GitHub 연동은 현재 구현 범위에 포함하지 않고 Todo로 둔다.

초기 아이디어:

```text
Public GitHub repo/file URL 입력
→ README.md 또는 지정 파일 감지
→ 제목/설명/태그/링크 자동 채움
→ 사용자가 확인 후 등록
```

범위 원칙:

- OAuth 없이 public URL 기반 import부터 검토한다.
- Private repository 접근은 MVP 제외다.
- GitHub OAuth, GitHub App, 자동 동기화는 후순위다.
- Markdown, Notebook, HTML 파일 감지는 등록 보조 기능으로 다룬다.

---

## 29. MVP 성공 기준

기술적 성공:

- 기존 Supabase Auth 유지
- 로그인 사용자가 프로젝트 등록 가능
- 썸네일 업로드 및 표시
- Power BI Embedded Viewer 실제 배포 렌더링
- 비로그인 방문자가 Microsoft 로그인 없이 Embedded Report 이용 가능
- Power BI Workspace 자동 Import 기반 PBIX 등록 가능
- Power BI 메타데이터 Supabase 저장
- 등록 성공 후 관리자 승인 없이 즉시 공개
- 프로젝트 Soft Delete 가능
- 비밀정보 클라이언트 미노출
- Supabase Free 범위 중심 운영

제품적 성공:

- 사용자가 갤러리에서 프로젝트 상세로 이동한다.
- 사용자가 실제 대시보드를 조작한다.
- 제작자가 프로젝트를 직접 등록한다.
- 일부 프로젝트에 댓글과 피드백이 발생한다.
- 사용자가 업데이트/레퍼런스/Feed를 이유로 재방문한다.
