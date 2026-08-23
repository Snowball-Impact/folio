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
| [ARCHITECTURE.md](ARCHITECTURE.md) | 시스템 구성, 계층, 인증·캐시·배포 구조 |
| [USER_FLOWS.md](USER_FLOWS.md) | 회원가입, 온보딩, 프로젝트 등록·탐색·관리 사용자 여정 |
| [DATA_MODEL.md](DATA_MODEL.md) | ERD, 관계·삭제 규칙, RLS 행렬, trigger와 RPC |
| [DECISIONS.md](DECISIONS.md) | 주요 기술·제품 결정 기록 |

## 운영과 검증

| 문서 | 설명 |
|---|---|
| [SUPABASE_SETUP.md](SUPABASE_SETUP.md) | Supabase 스키마·Auth·RLS 설정과 검증 절차 |
| [PAAS_DEPLOYMENT.md](PAAS_DEPLOYMENT.md) | Docker 기반 PaaS 배포와 운영 전환 절차 |
| [STREAMLIT_CLOUD_DEPLOYMENT.md](STREAMLIT_CLOUD_DEPLOYMENT.md) | 이전 Streamlit Community Cloud 배포 기준과 캡처 실험 기록 |
| [INTEGRATION_VALIDATION.md](INTEGRATION_VALIDATION.md) | 실제 계정과 원격 Supabase 통합 검증 결과 |
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
