# FOLIO Data Visualization Community PRD v1.1

> **Status:** Development Baseline\
> **Purpose:** Codex가 기존 FOLIO 저장소를 먼저 분석한 후, 데이터 시각화
> 커뮤니티 MVP를 단계적으로 구현하기 위한 제품·개발 기준 문서.

------------------------------------------------------------------------

## 0. Codex 작업 원칙

구현 전에 반드시 현재 Repository를 먼저 분석한다.

1.  디렉터리 구조와 주요 모듈 확인
2.  현재 데이터 저장 방식과 프로젝트 모델 확인
3.  기존 **Supabase Auth** 인증 구조 확인
4.  갤러리·프로젝트 상세·프로젝트 등록 화면 확인
5.  댓글·공지·Q&A·관리자 기능의 기존 구현 여부 확인
6.  Streamlit 배포 및 환경변수 관리 방식 확인
7.  기존 기능과 코드를 최대한 재사용
8.  PRD와 기존 구현이 충돌하면 임의로 대규모 리팩터링하지 않음
9.  충돌·변경 필요사항을 먼저 보고한 뒤 최소 변경으로 구현
10. 각 Sprint를 독립적으로 실행·검증 가능한 단위로 개발

**원칙: Simple is Best. MVP 수요 검증에 필요하지 않은 기능은 선행
개발하지 않는다.**

------------------------------------------------------------------------

# 1. Product Vision

FOLIO를 단순 포트폴리오 갤러리에서 **데이터 시각화 프로젝트를
발견·체험·공유하고 관련 실무 콘텐츠를 탐색하는 커뮤니티**로 발전시킨다.

핵심 경험:

-   실제 데이터 시각화 프로젝트 발견
-   인터랙티브 대시보드 직접 체험
-   제작자의 프로젝트 직접 등록
-   프로젝트에 대한 질문·의견 교환
-   Power BI, Tableau, Looker 등 생태계 콘텐츠 탐색
-   행사·자격·공모전·채용 등 실무 정보 탐색

초기 목표는 완성형 플랫폼 구축이 아니라 **서비스 수요 검증**이다.

------------------------------------------------------------------------

# 2. Validation Goal

-   **H1 Project Discovery:** 사용자는 다른 사람의 데이터 시각화
    프로젝트를 발견하기 위해 FOLIO를 방문하는가?
-   **H2 Interactive Visualization:** 실제 인터랙티브 대시보드가
    프로젝트 탐색 가치를 높이는가?
-   **H3 Creator Supply:** 제작자는 자신의 프로젝트를 직접 등록하는가?
-   **H4 Community:** 사용자는 프로젝트에 질문·의견·피드백을 남기는가?
-   **H5 Recurring Content:** 업데이트·행사·자격·공모전·채용 콘텐츠가
    재방문을 만드는가?

------------------------------------------------------------------------

# 3. Target Users

-   Power BI / Tableau / Looker Studio 사용자
-   데이터 분석가 / BI Analyst / BI Developer
-   데이터 엔지니어
-   데이터 기반 웹서비스 개발자
-   포트폴리오 레퍼런스를 찾는 취업 준비생
-   대시보드 사례를 찾는 실무자
-   데이터/BI 인재를 탐색하는 기업

------------------------------------------------------------------------

# 4. Core User Journey

## Visitor

``` text
FOLIO
→ 프로젝트 갤러리
→ 프로젝트 상세
→ Interactive Dashboard
→ 프로젝트 설명/보고서
→ 댓글 또는 다른 프로젝트 탐색
```

## Creator

``` text
Supabase Auth 로그인
→ 프로젝트 등록
→ 프로젝트 유형 선택
→ 프로젝트 정보 + 썸네일 입력
→ Power BI인 경우 PBIX 업로드
→ 자동 처리
→ 즉시 공개
```

## Future Content Consumer

``` text
FOLIO
→ Feed
→ 제품 업데이트 / 행사 / 자격 / 공모전 / 채용
→ 원문 또는 관련 프로젝트 탐색
```

------------------------------------------------------------------------

# 5. Infrastructure Constraint --- Supabase Free

MVP는 **Supabase Free Tier 범위 내 운영**을 기본 원칙으로 한다.

현재 계획상 고려 한도:

-   Database: 500MB
-   File Storage: 1GB
-   MAU: 50,000
-   Project: 최대 2개

운영 원칙:

1.  PostgreSQL에는 구조화 데이터와 메타데이터 중심으로 저장한다.
2.  PBIX를 Supabase Storage에 영구 보관하지 않는다.
3.  외부 콘텐츠 원문 HTML·대용량 본문·이미지 바이너리를 복제하지 않는다.
4.  콘텐츠는 제목·요약·출처·URL·날짜 등 필요한 최소 데이터만 저장한다.
5.  썸네일은 업로드 후 리사이징/압축한다.
6.  사용량이 한도에 근접한 경우 실제 서비스 수요를 확인한 후 유료 전환을
    판단한다.
7.  권장 운영 경고 기준: 70% 사용 시 점검, 85% 사용 시 정리/확장 판단.

------------------------------------------------------------------------

# 6. Target Architecture

``` text
Users
  ↓
FOLIO / Streamlit
  ├──────────────→ Power BI REST API / Embedded
  ↓
Supabase
├─ PostgreSQL
├─ Auth
└─ Storage (Thumbnail)
  ↑
Local Windows PC
└─ Python ETL (향후)
```

### 역할

**FOLIO** - UI - 갤러리/상세 - 프로젝트 등록 - 댓글 - Power BI Embedded
Viewer

**Supabase** - PostgreSQL: 서비스 영구 데이터 - Auth: 기존 사용자 인증
유지 - Storage: 최적화된 썸네일

**Power BI** - PBIX Import - Report / Semantic Model - Embed Token -
Interactive Rendering

**Local Windows Worker** - 향후 콘텐츠 수집 - Python ETL -
정제/검증/중복 제거 - Supabase 적재 - 실행 로그

------------------------------------------------------------------------

# 7. Database Strategy

로컬 SQLite가 아니라 **Supabase PostgreSQL**을 서비스 DB로 사용한다.

로컬 PC는 ETL 실행 환경이며 서비스 영구 데이터의 기준 저장소가 아니다.

## Core Tables

### profiles

``` text
id
display_name
avatar_url
bio
created_at
updated_at
```

기존 Supabase Auth 및 사용자 프로필 구조가 존재하면 이를 우선
재사용한다.

### projects

``` text
id
user_id
title
description
project_type
thumbnail_url
github_url
external_url
status
created_at
updated_at
published_at
deleted_at
```

`project_type` 예시:

``` text
powerbi
tableau
looker
streamlit
web
other
```

MVP `status`:

``` text
processing
published
failed
deleted
```

필요성이 확인될 때만 `draft`를 추가한다.

### powerbi_reports

``` text
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

기존 구현을 우선 확인한다.

``` text
id
project_id
user_id
content
is_edited
created_at
updated_at
```

### contents --- Future

``` text
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

------------------------------------------------------------------------

# 8. Thumbnail Policy

프로젝트 등록 시 **대표 썸네일 업로드를 필수**로 한다.

Flow:

``` text
User Image Upload
→ Format / Size Validation
→ Resize
→ Compression
→ Supabase Storage
→ thumbnail_url
→ projects
```

MVP 정책:

-   JPG / PNG / WebP 허용
-   원본 업로드 크기는 합리적인 상한을 둔다.
-   저장 전 리사이징/압축
-   최종 저장 파일은 가급적 500KB 이하를 목표
-   자동 대시보드 캡처는 MVP 제외
-   프로젝트 영구 삭제 시 연결 썸네일도 정리

------------------------------------------------------------------------

# 9. Publishing Policy

## Authentication

프로젝트 등록은 **Supabase Auth 로그인 사용자만 가능**하다.

기존 Supabase Auth 구현을 유지하며 불필요한 인증 재설계를 하지 않는다.

## Publication

관리자 사전 승인 기능을 만들지 않는다.

### 일반 프로젝트

``` text
등록 성공
→ published
→ 갤러리 즉시 공개
```

### Power BI 프로젝트

``` text
등록
→ processing
→ PBIX Import
→ Metadata 확보
→ 성공: published
→ 실패: failed
```

관리자는 사전 승인자가 아니라 **사후 관리 역할**만 가진다.

-   부적절한 프로젝트 비공개/삭제
-   필요한 경우 댓글 관리

승인 Queue, review 상태, 승인 알림은 구현하지 않는다.

------------------------------------------------------------------------

# 10. Phase 1 --- Power BI Embedded Viewer

## 목표

기존 검증 가능한 Power BI 프로젝트를 FOLIO 상세페이지에 Embedded
방식으로 연결하여 실제 배포 환경에서 기술검증을 완료한다.

``` text
Visitor
→ Project Detail
→ Server-side Power BI Authentication
→ Generate Embed Token
→ reportId + embedUrl + token
→ Power BI JS SDK
→ Interactive Report
```

환경변수:

``` text
POWERBI_TENANT_ID
POWERBI_CLIENT_ID
POWERBI_CLIENT_SECRET
POWERBI_WORKSPACE_ID
```

### Requirements

-   Client Secret은 서버에서만 사용
-   Embed Token은 요청 시 동적 발급
-   Embed Token 영구 DB 저장 금지
-   비로그인 방문자도 Microsoft 로그인 없이 보고서 열람 가능
-   실패 시 빈 화면 대신 오류 UI 제공

### Acceptance Criteria

-   FOLIO 실제 배포 환경에서 렌더링
-   Chrome 시크릿 창에서 정상 표시
-   필터 등 기본 인터랙션 정상 작동
-   Microsoft 로그인 불필요
-   Client Secret 클라이언트 미노출

------------------------------------------------------------------------

# 11. Phase 2 --- Database Foundation

Embedded 실제 배포 검증 후 신규 Power BI 게시 기능에 필요한 DB 구조를
정리한다.

Requirements:

-   현재 Repository의 Supabase 구조 최대 재사용
-   `projects` 확장 필요성 확인
-   `powerbi_reports` 추가
-   환경변수/Secret 관리 확인
-   기존 프로젝트와 호환성 유지
-   필요한 DB migration을 최소 범위로 작성

### Acceptance Criteria

-   기존 프로젝트 갤러리 정상 작동
-   Supabase에서 Power BI 메타데이터 저장/조회 가능
-   기존 Auth 정상 유지
-   기존 프로젝트 데이터 손실 없음

------------------------------------------------------------------------

# 12. Phase 3 --- Power BI PBIX Publisher

## 목표

일반 사용자가 Power BI 내부 구조를 몰라도 PBIX를 통해 프로젝트를 등록할
수 있도록 한다.

### Registration UI

``` text
프로젝트 제목 *
설명 *
프로젝트 유형 *
태그
대표 썸네일 *

[Power BI 선택 시]
PBIX 파일 *

GitHub URL
기타 URL

[프로젝트 등록]
```

사용자에게 다음을 입력시키지 않는다.

-   Workspace ID
-   Dataset ID
-   Report ID
-   Embed URL

### Processing

``` text
PBIX Upload
→ project.status = processing
→ Power BI Import API
→ Import Status Polling
→ Dataset ID
→ Report ID
→ Embed URL
→ powerbi_reports 저장
→ project.status = published
→ 갤러리 즉시 공개
```

실패:

``` text
Import Failure
→ project.status = failed
→ 오류 정보 제공
```

------------------------------------------------------------------------

# 13. PBIX Storage Policy

PBIX는 영구 파일 저장소로 관리하지 않는다.

``` text
PBIX Upload
→ Temporary Processing
→ Power BI Import
→ Import 성공 확인
→ PBIX 임시 원본 삭제
```

Supabase Storage 1GB를 PBIX 보관 용도로 사용하지 않는다.

MVP에서는 게시된 PBIX의 교체/버전 관리 기능을 지원하지 않는다.

수정된 PBIX를 게시하려면 신규 프로젝트 등록을 기본 정책으로 한다.

------------------------------------------------------------------------

# 14. Power BI Workspace Policy

MVP에서는 **FOLIO 전용 Workspace 1개**를 사용한다.

``` text
FOLIO Workspace
├─ Project A Report / Semantic Model
├─ Project B Report / Semantic Model
└─ Project C Report / Semantic Model
```

사용자별 Workspace는 만들지 않는다.

리소스 이름 충돌 방지를 위해 내부 Naming Convention을 사용한다.

권장 예:

``` text
{project_id}_{original_name}
```

실제 API 제약과 기존 구현을 확인한 후 최종 적용한다.

------------------------------------------------------------------------

# 15. Project Deletion & Recovery

삭제는 즉시 물리 삭제하지 않고 **Soft Delete**를 기본으로 한다.

``` text
User Delete
→ project.status = deleted
→ deleted_at 기록
→ FOLIO에서 즉시 숨김
```

Power BI Report / Semantic Model은 즉시 삭제하지 않고 **30일 복구
기간**을 둔다.

30일 이내 복구:

``` text
deleted
→ restore
→ published
```

30일 경과 후:

``` text
Project Metadata Cleanup
Power BI Report Cleanup
Semantic Model Cleanup
Thumbnail Cleanup
```

MVP에서는 30일 자동 Cleanup Job을 반드시 구현할 필요는 없다.

초기에는 관리자 수동 정리도 허용하고, 삭제량이 증가하면 Cleanup Job을
추가한다.

PBIX 원본 파일은 이미 Import 후 삭제되므로 별도 PBIX 백업은 하지 않는다.

------------------------------------------------------------------------

# 16. Power BI MVP Restrictions

지원하지 않음:

-   사용자별 Power BI Workspace
-   여러 Capacity 자동 관리
-   PBIX 버전 관리
-   PBIX 다운로드
-   Dataset Credential 자동 구성
-   Gateway 자동 연결
-   Dataset 자동 Refresh 설정
-   RLS 자동 설정
-   DirectQuery 자동 구성
-   Power BI 편집 기능
-   Publish to Web 자동화
-   Playwright/Selenium 기반 게시 자동화
-   사용자 외부 DB Credential 관리

------------------------------------------------------------------------

# 17. Community --- Subsequent Phase

기존 구현을 먼저 확인하고 없는 기능만 추가한다.

MVP:

-   댓글 작성
-   댓글 수정
-   댓글 삭제
-   작성일
-   수정됨 표시
-   관리자 사후 삭제

공지사항/Q&A는 기존 구조를 최대한 재사용한다.

오류 제보는 복잡한 시스템 대신 이메일 기반을 우선한다.

후순위:

-   대댓글
-   좋아요
-   팔로우
-   DM
-   실시간 알림
-   복잡한 신고 시스템

------------------------------------------------------------------------

# 18. Content Feed --- Subsequent Phase

목표는 프로젝트 외에도 사용자의 재방문 이유를 만드는 것이다.

후보:

-   Power BI / Fabric Update
-   Tableau Update
-   Looker Update
-   데이터 시각화 News
-   행사 / Webinar
-   자격 / 시험 일정 및 변경
-   공모전
-   BI / Data Visualization 채용

콘텐츠 원문 저장 서비스가 아니라 **큐레이션/발견 서비스**로 설계한다.

저장 데이터는 최소화한다.

``` text
title
summary
source
source_url
content_type
published_at
thumbnail_url (필요 시)
```

초기에는 관리자 수동 등록도 허용한다.

------------------------------------------------------------------------

# 19. Content ETL --- Subsequent Phase

ETL은 당분간 남는 Windows PC에서 실행한다.

``` text
Windows Task Scheduler
→ Python
→ Collector
→ Transform
→ Validation
→ Deduplication
→ Supabase PostgreSQL
→ FOLIO Feed
```

원칙:

-   수집 Source를 하나씩 추가
-   하나의 Source를 End-to-End로 완성 후 다음 Source 개발
-   ETL 실행 환경과 DB를 분리
-   향후 필요하면 Render Cron / Cloud Run / Azure 등으로 Worker만 이전
    가능

향후 `collection_logs`:

``` text
id
source
job_name
started_at
finished_at
status
records_collected
records_inserted
records_updated
error_message
```

------------------------------------------------------------------------

# 20. Security

-   Supabase Key / Power BI Secret 등 비밀정보 Git Commit 금지
-   Power BI Client Secret은 서버 전용
-   Embed Token 영구 저장 금지
-   PBIX 장기 저장 금지
-   업로드 파일 형식/크기 검증
-   Supabase Auth 기존 구조 유지
-   실제 Repository 확인 후 RLS/권한 정책 최소 권한 적용
-   사용자가 소유한 프로젝트만 수정/삭제 가능하도록 보장

------------------------------------------------------------------------

# 21. Analytics

기존 GA 구조를 우선 활용한다.

후보 이벤트:

``` text
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
```

제품적 성공 여부는 실제 행동 데이터와 사용자 피드백으로 판단한다.

------------------------------------------------------------------------

# 22. UX Principles

1.  UI는 간결하게 유지
2.  프로젝트 자체가 화면의 중심
3.  상세페이지 기본 1열 구조
4.  Hero: 좌측 텍스트 / 우측 대표 이미지
5.  상세: 대시보드 → 보고서/설명 → 댓글
6.  사용자에게 Power BI 내부 기술 ID를 요구하지 않음
7.  processing / failed 상태를 명확히 표시
8.  신규 기능 때문에 기존 프로젝트 유형 사용성을 훼손하지 않음
9.  등록 절차는 가능한 짧게 유지
10. 관리자 승인 절차 없음

------------------------------------------------------------------------

# 23. Out of Scope

현재 MVP 제외:

-   AI 추천/평가/챗봇
-   사용자 DM
-   팔로우
-   실시간 알림
-   Reputation 시스템
-   결제/광고
-   PBIX 버전 관리
-   Power BI 자동 Refresh
-   사용자 DB Credential 관리
-   복잡한 DW
-   Kafka / Spark / Kubernetes
-   과도한 MSA
-   모든 콘텐츠 수집처 동시 개발
-   자동 썸네일 캡처

------------------------------------------------------------------------

# 24. Implementation Roadmap

## Sprint 0 --- Repository Audit

``` text
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

**코드를 수정하기 전에 결과를 보고한다.**

## Sprint 1 --- Embedded Viewer

기존 검증 가능한 Power BI 프로젝트 1개를 실제 FOLIO 상세페이지에
연결한다.

**Done:** 실제 배포된 FOLIO에서 비로그인 방문자가 보고서를 조작할 수
있다.

## Sprint 2 --- Database Foundation

기존 DB 구조를 최대한 유지하면서 `powerbi_reports` 및 필요한 프로젝트
필드를 추가한다.

**Done:** Power BI 프로젝트 메타데이터가 Supabase에 안정적으로
저장/조회된다.

## Sprint 3 --- Thumbnail Upload

썸네일 업로드 → 검증 → 최적화 → Supabase Storage → 프로젝트 연결.

**Done:** 프로젝트 등록 시 최적화된 대표 이미지가 저장되고 갤러리에
표시된다.

## Sprint 4 --- PBIX Publisher

PBIX → Import → Polling → Report/Dataset/Embed Metadata → Supabase.

**Done:** Power BI 서비스에 수동 접속하지 않고 게시 가능한 상태가 된다.

## Sprint 5 --- Registration UX

로그인 사용자:

``` text
프로젝트 정보
→ Thumbnail
→ Power BI 선택 시 PBIX
→ processing
→ 자동 published / failed
```

**Done:** 일반 사용자가 Power BI 기술 ID를 몰라도 등록할 수 있다.

## Sprint 6 --- Soft Delete / Recovery

삭제 → 즉시 숨김 → 30일 복구 가능 구조.

자동 Cleanup은 후순위.

## Sprint 7 --- Community

기존 구현 Gap만 보완.

## Sprint 8 --- Feed Foundation

`contents` → 관리자 수동 등록 → Feed → Filter → Source 이동.

## Sprint 9+ --- ETL

가치와 난이도에 따라 Source를 하나씩 추가한다.

------------------------------------------------------------------------

# 25. Current Priority

``` text
1. Repository Audit
2. Power BI Embedded Viewer
3. Supabase DB 구조 보완
4. Thumbnail Upload
5. PBIX Publisher
6. Registration UX
7. Soft Delete / Recovery
8. Community
9. Feed
10. Content ETL
```

콘텐츠 자동수집보다 **Power BI Embedded 제품화**를 우선한다.

------------------------------------------------------------------------

# 26. Definition of MVP Success

기술적 성공:

-   기존 Supabase Auth 유지
-   로그인 사용자가 프로젝트 등록 가능
-   썸네일 업로드 및 표시
-   Power BI 프로젝트 PBIX 등록 가능
-   Power BI Workspace 자동 Import
-   Power BI 메타데이터 Supabase 저장
-   등록 성공 후 관리자 승인 없이 즉시 공개
-   비로그인 방문자가 Embedded Report 이용 가능
-   프로젝트 Soft Delete 가능
-   비밀정보 클라이언트 미노출
-   Supabase Free 범위 중심 운영

제품적 성공은 다음 질문으로 판단한다.

> **사람들은 FOLIO에서 다른 사람의 데이터 시각화 프로젝트를 실제로
> 발견하고, 체험하고, 다시 방문하는가?**

이 수요가 확인되기 전까지 인프라와 기능을 과도하게 확장하지 않는다.
