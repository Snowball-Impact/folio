# FOLIO 문서 안내

문서는 문서가 설명하는 실행 환경과 시간적 성격에 따라 나눈다. 새 컨텍스트에서는 먼저 이 문서를 읽고, 작업 대상에 맞는 하위 폴더의 README와 기준 문서를 선택한다.

## 빠른 시작

| 작업 대상 | 먼저 읽을 문서 |
|---|---|
| 공통 제품·데이터·개발 원칙 | [common/README.md](common/README.md) |
| Streamlit 원본·기존 운영 | [streamlit/README.md](streamlit/README.md) |
| 현재 SvelteKit·Cloudflare | [svelte/README.md](svelte/README.md) |
| Streamlit↔Svelte 전환·UIUX 증거 | [migration/README.md](migration/README.md) |
| 과거 초안·완료 기록 | [legacy/README.md](legacy/README.md) |

## 공통 기준

제품, 데이터, 인증, 디자인, 개발 규칙처럼 두 구현이 함께 참고하는 문서다.

- [common/PROJECT_CONTEXT.md](common/PROJECT_CONTEXT.md): 제품 전체 맥락과 장기 작업 기록
- [common/ENGINEERING_PLAYBOOK.md](common/ENGINEERING_PLAYBOOK.md): 작업 원칙과 검증 기준
- [common/MVP_PRD.md](common/MVP_PRD.md): 제품 문제와 MVP 범위
- [common/ARCHITECTURE.md](common/ARCHITECTURE.md): 시스템 구성과 계층
- [common/DATA_MODEL.md](common/DATA_MODEL.md): ERD, 관계, RLS, RPC
- [common/SUPABASE_SETUP.md](common/SUPABASE_SETUP.md): Supabase 설정과 공통 백엔드 계약
- [common/DESIGN_SYSTEM.md](common/DESIGN_SYSTEM.md): UI 토큰과 디자인 원칙
- [common/USER_FLOWS.md](common/USER_FLOWS.md): 공통 사용자 여정
- [common/DECISIONS.md](common/DECISIONS.md): 기술·제품 결정 기록
- [common/FOLIO_Community_PRD.md](common/FOLIO_Community_PRD.md): 커뮤니티 게시판 PRD
- [common/FOLIO_Admin_PRD.md](common/FOLIO_Admin_PRD.md): 운영 Admin PRD
- [common/COMMENT_FEATURE_PLAN.md](common/COMMENT_FEATURE_PLAN.md): 댓글 기능 계획
- [common/COLLABORATION_RETROSPECTIVE.md](common/COLLABORATION_RETROSPECTIVE.md): AI 협업 회고

## Streamlit

`folio_app/`와 루트 `app.py`의 원본 실행·배포·통합 검증 문서다.

- [streamlit/PAAS_DEPLOYMENT.md](streamlit/PAAS_DEPLOYMENT.md): Docker 기반 Streamlit PaaS 배포
- [streamlit/STREAMLIT_CLOUD_DEPLOYMENT.md](streamlit/STREAMLIT_CLOUD_DEPLOYMENT.md): Streamlit Community Cloud 기록
- [streamlit/INTEGRATION_VALIDATION.md](streamlit/INTEGRATION_VALIDATION.md): Streamlit 기준 원격 Supabase 검증

## SvelteKit

현재 `svelte_app/` 구현과 Cloudflare runtime의 기준 문서다.

- [svelte/CLOUDFLARE_DEPLOYMENT.md](svelte/CLOUDFLARE_DEPLOYMENT.md): Cloudflare Pages/Workers 배포 기준과 제약
- [svelte/SVELTE_DEVELOPMENT_ENVIRONMENT.md](svelte/SVELTE_DEVELOPMENT_ENVIRONMENT.md): 개발·테스트 환경
- [svelte/SVELTE_E2E_READINESS.md](svelte/SVELTE_E2E_READINESS.md): E2E go/no-go 기준
- [svelte/SVELTE_STAGING_QA_RUNBOOK.md](svelte/SVELTE_STAGING_QA_RUNBOOK.md): staging 수동 QA
- [svelte/SVELTE_PHASE0_DATA_CONTRACTS.md](svelte/SVELTE_PHASE0_DATA_CONTRACTS.md): 구현 전 데이터 계약
- [svelte/SVELTE_REFACTOR_CHECKLIST_2026-08-29.md](svelte/SVELTE_REFACTOR_CHECKLIST_2026-08-29.md): 리팩토링·최적화 실행 기록
- [svelte/SVELTE_REFACTOR_OPTIMIZATION_HANDOFF_2026-08-29.md](svelte/SVELTE_REFACTOR_OPTIMIZATION_HANDOFF_2026-08-29.md): 새 컨텍스트 인수인계
- [svelte/SVELTE_RUM_CONTRACT_2026-08-29.md](svelte/SVELTE_RUM_CONTRACT_2026-08-29.md): 선택형 RUM 계약

## Migration

두 구현을 비교하거나 SvelteKit 이전 과정의 UIUX·기능 증거를 기록한 문서다.

- [migration/SVELTE_MIGRATION_PRD.md](migration/SVELTE_MIGRATION_PRD.md): SvelteKit 단계적 재구축 계획
- [migration/SVELTE_MIGRATION_RETROSPECTIVE.md](migration/SVELTE_MIGRATION_RETROSPECTIVE.md): 이전 과정 회고
- [migration/UI_PARITY_CAPTURE_REPORT.md](migration/UI_PARITY_CAPTURE_REPORT.md): 전체 UI parity 판정
- [migration/UIUX_CAPTURE_EVIDENCE_REVIEW_2026-08-28.md](migration/UIUX_CAPTURE_EVIDENCE_REVIEW_2026-08-28.md): 캡처 증거 재검토
- [migration/UIUX_DEEP_DIVE_AUDIT.md](migration/UIUX_DEEP_DIVE_AUDIT.md): Streamlit 원본과 현재 Svelte 비교 감사
- [migration/UI_LAYOUT_HARMONY_DEEP_DIVE.md](migration/UI_LAYOUT_HARMONY_DEEP_DIVE.md): 레이아웃·조화 조사
- [migration/UIUX_FOCUS_PAGE_STATIC_AUDIT_2026-08-28.md](migration/UIUX_FOCUS_PAGE_STATIC_AUDIT_2026-08-28.md): 핵심 페이지 정적 대조
- [migration/UIUX_PHASE1_NAVIGATION_PARITY_2026-08-28.md](migration/UIUX_PHASE1_NAVIGATION_PARITY_2026-08-28.md): 탐색 parity 기록

나머지 날짜별 UIUX 재감사·캡처 실행 기록도 이 폴더에 보관한다.

## 큐레이션

- [curation/powerbi_CONTENT_OPS.md](curation/powerbi_CONTENT_OPS.md): Power BI 콘텐츠 수집·검증·운영
- [curation/tableau_gallery/](curation/tableau_gallery/): Tableau Gallery
- [curation/looker_studio_gallery/](curation/looker_studio_gallery/): Looker Studio Gallery
- [curation/streamlit_gallery/](curation/streamlit_gallery/): Streamlit Gallery

## Legacy

[legacy/](legacy/)에는 초안, 완료 체크리스트, 이전 와이어프레임과 당시의 상세 개선 기록을 보관한다. 현재 구현과 충돌하면 공통 기준 문서, 실제 코드, 스키마 순서로 확인한다.
