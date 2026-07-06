# FOLIO 문서 안내

문서는 목적에 따라 제품·설계·운영·작업 기록으로 나뉜다.

## 포트폴리오용 설계 문서

| 문서 | 설명 |
|---|---|
| [ARCHITECTURE.md](ARCHITECTURE.md) | 시스템 구성, 계층, 인증·캐시·배포 구조와 Mermaid 다이어그램 |
| [USER_FLOWS.md](USER_FLOWS.md) | 회원가입, 온보딩, 프로젝트 등록·탐색·관리 사용자 여정 |
| [DATA_MODEL.md](DATA_MODEL.md) | ERD, 관계·삭제 규칙, RLS 행렬, trigger와 RPC |
| [DECISIONS.md](DECISIONS.md) | 기술·제품 선택의 맥락과 결과를 ADR 형식으로 기록 |
| [ENGINEERING_PLAYBOOK.md](ENGINEERING_PLAYBOOK.md) | 개발 정책, 검증 기준, 시행착오에서 얻은 교훈 |
| [COLLABORATION_RETROSPECTIVE.md](COLLABORATION_RETROSPECTIVE.md) | AI 협업 과정에서 관찰한 역량과 성장 기준을 날짜별로 기록 |

## 제품과 화면

| 문서 | 설명 |
|---|---|
| [PRD.md](PRD.md) | 제품 문제, 사용자, MVP 범위와 성공 기준 |
| [WIREFRAME.MD](WIREFRAME.MD) | 현재 화면 구조와 UI 규칙 |
| [PROJECT_DETAIL_PAGE_IMPROVEMENTS.md](PROJECT_DETAIL_PAGE_IMPROVEMENTS.md) | 프로젝트 상세 화면 개선 기록 |

## 개발과 운영

| 문서 | 설명 |
|---|---|
| [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md) | 새 작업을 시작할 때 가장 먼저 읽는 현재 컨텍스트 |
| [SUPABASE_SETUP.md](SUPABASE_SETUP.md) | Supabase 스키마·Auth·RLS 설정과 검증 절차 |
| [INTEGRATION_VALIDATION.md](INTEGRATION_VALIDATION.md) | 실제 계정과 원격 Supabase를 사용한 통합 검증 결과 및 미검증 범위 |

## 완료 기록

| 문서 | 설명 |
|---|---|
| [WEEK1_BUILD_CHECKLIST.md](WEEK1_BUILD_CHECKLIST.md) | 인증·프로필·앱 기반 구축 기록 |
| [WEEK2_BUILD_CHECKLIST.md](WEEK2_BUILD_CHECKLIST.md) | 프로젝트 CRUD·탐색·상세·좋아요 구축 기록 |

완료 기록은 당시 상태를 보존한다. 현재 구조와 작업 원칙이 충돌하면 `PROJECT_CONTEXT.md`, 실제 코드, 스키마 순으로 확인한 뒤 문서를 갱신한다.
