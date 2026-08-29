# FOLIO 문서 안내

문서는 현재 작업에 필요한 기준 문서만 루트에 둔다. 초안, 완료 기록, 오래된 와이어프레임은 `legacy/`에 보관한다.

## 먼저 읽을 문서

| 문서 | 설명 |
|---|---|
| [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md) | 현재 코드 구조, 기능 상태, 최근 작업 기록 |
| [ENGINEERING_PLAYBOOK.md](ENGINEERING_PLAYBOOK.md) | 작업 원칙, 검증 기준, 반복 실수 방지 규칙 |
| [DESIGN_SYSTEM.md](DESIGN_SYSTEM.md) | 현재 UI 취향, 토큰, 컴포넌트 사용 기준 |

## 제품과 설계

| 문서 | 설명 |
|---|---|
| [MVP_PRD.md](MVP_PRD.md) | 제품 문제, 사용자, MVP 범위와 성공 기준을 통합한 현재 기준 PRD |
| [FOLIO_Community_PRD.md](FOLIO_Community_PRD.md) | Power BI 사용자 커뮤니티 게시판 MVP 범위와 정책 |
| [FOLIO_Admin_PRD.md](FOLIO_Admin_PRD.md) | FOLIO 통합 운영 Admin MVP 범위와 정책 |
| [SVELTE_MIGRATION_PRD.md](SVELTE_MIGRATION_PRD.md) | Streamlit MVP를 Svelte로 단계 이전하기 위한 화면 우선순위, 데이터 계약, 마이그레이션 계획 |
| [SVELTE_PHASE0_DATA_CONTRACTS.md](SVELTE_PHASE0_DATA_CONTRACTS.md) | Svelte 구현 전 홈/상세/콘텐츠 RPC와 타입 계약 점검 |
| [ARCHITECTURE.md](ARCHITECTURE.md) | 시스템 구성, 계층, 인증·캐시·배포 구조 |
| [USER_FLOWS.md](USER_FLOWS.md) | 회원가입, 온보딩, 프로젝트 등록·탐색·관리 사용자 여정 |
| [DATA_MODEL.md](DATA_MODEL.md) | ERD, 관계·삭제 규칙, RLS 행렬, trigger와 RPC |
| [DECISIONS.md](DECISIONS.md) | 주요 기술·제품 결정 기록 |

## 운영과 검증

| 문서 | 설명 |
|---|---|
| [SUPABASE_SETUP.md](SUPABASE_SETUP.md) | Supabase 스키마·Auth·RLS 설정과 검증 절차 |
| [PAAS_DEPLOYMENT.md](PAAS_DEPLOYMENT.md) | Docker 기반 PaaS 배포와 운영 전환 절차 |
| [CLOUDFLARE_DEPLOYMENT.md](CLOUDFLARE_DEPLOYMENT.md) | SvelteKit 앱을 Cloudflare Workers/Pages 런타임에 올리기 위한 배포 기준과 제약 |
| [STREAMLIT_CLOUD_DEPLOYMENT.md](STREAMLIT_CLOUD_DEPLOYMENT.md) | 이전 Streamlit Community Cloud 배포 기준과 캡처 실험 기록 |
| [INTEGRATION_VALIDATION.md](INTEGRATION_VALIDATION.md) | 실제 계정과 원격 Supabase 통합 검증 결과 |
| [SVELTE_E2E_READINESS.md](SVELTE_E2E_READINESS.md) | SvelteKit 전환 전 운영 환경·E2E go/no-go 체크리스트 |
| [SVELTE_STAGING_QA_RUNBOOK.md](SVELTE_STAGING_QA_RUNBOOK.md) | SvelteKit staging 배포 후 실제 계정으로 확인할 수동 QA 실행 순서 |
| [SVELTE_DEVELOPMENT_ENVIRONMENT.md](SVELTE_DEVELOPMENT_ENVIRONMENT.md) | Streamlit 원본, Svelte 개발 서버, Cloudflare preview, UIUX capture 환경 기준 |
| [SVELTE_MIGRATION_RETROSPECTIVE.md](SVELTE_MIGRATION_RETROSPECTIVE.md) | Streamlit에서 SvelteKit으로 이전하며 얻은 전환 교훈과 남은 리스크 |
| [UI_LAYOUT_HARMONY_DEEP_DIVE.md](UI_LAYOUT_HARMONY_DEEP_DIVE.md) | Streamlit 원본 대비 Svelte 컴포넌트 위치·배치·균형·조화 전수 조사 |
| [UIUX_FOCUS_PAGE_STATIC_AUDIT_2026-08-28.md](UIUX_FOCUS_PAGE_STATIC_AUDIT_2026-08-28.md) | 마이페이지·알림·등록/수정·상세의 원본/Svelte 정적 구조 대조 |
| [UIUX_CAPTURE_EVIDENCE_REVIEW_2026-08-28.md](UIUX_CAPTURE_EVIDENCE_REVIEW_2026-08-28.md) | Desktop Browser와 Playwright 캡처를 합친 페이지별 증거표와 현재 판정 |
| [UIUX_FOCUS_CAPTURE_COMPARISON_2026-08-28.md](UIUX_FOCUS_CAPTURE_COMPARISON_2026-08-28.md) | 네 핵심 페이지의 최신 원본/Svelte 캡처 시각 비교와 반응형 차이 |
| [COLLABORATION_RETROSPECTIVE.md](COLLABORATION_RETROSPECTIVE.md) | AI 협업 방식과 교훈 회고 |
| [curation/powerbi_CONTENT_OPS.md](curation/powerbi_CONTENT_OPS.md) | Power BI 업데이트·커뮤니티·학습 콘텐츠 정기 수집과 점검 절차 |

## 큐레이션 데이터

| 위치 | 설명 |
|---|---|
| [curation/tableau_gallery/](curation/tableau_gallery/) | Tableau Gallery 수집 결과와 수집 방식 |
| [curation/looker_studio_gallery/](curation/looker_studio_gallery/) | Looker Studio/Data Studio Gallery 수집 결과와 skip 로그 |
| [curation/streamlit_gallery/](curation/streamlit_gallery/) | Streamlit Gallery 수집 결과 CSV |
| [curation/powerbi_*](curation/powerbi_CONTENT_OPS.md) | Power BI Desktop, 업데이트, 변경 로그, 공식 영상, 커뮤니티 블로그, 학습 영상 수집 결과 |

## Legacy

| 위치 | 설명 |
|---|---|
| [legacy/](legacy/) | 초안, 완료 체크리스트, 이전 와이어프레임, 과거 상세 개선 기록, 이전 PRD |

`legacy/` 문서는 당시 맥락 보존용이다. 현재 구현 기준과 충돌하면 `PROJECT_CONTEXT.md`, 실제 코드, 스키마 순으로 확인한다.
