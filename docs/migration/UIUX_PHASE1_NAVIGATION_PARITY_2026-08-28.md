# UIUX Phase 1: My Page and Notifications

조사일: 2026-08-28

이 문서는 단계적 클로닝 작업의 1차 조사 기록이다. 브라우저 런타임이 제공되지 않아 이번 회차의 Svelte DOM/신규 캡처 판정은 일부 unknown 또는 partial로 남긴다.

## 조사 범위

- 원본 코드: folio_app/pages/protected.py, folio_app/pages/notifications.py, folio_app/components/layout.py, folio_app/styles/notifications.py, folio_app/styles/profile.py
- Svelte 코드: svelte_app/src/routes/my/+page.svelte, svelte_app/src/routes/notifications/+page.svelte, svelte_app/src/lib/components/AuthNav.svelte, svelte_app/src/app.css
- 기존 캡처/리포트: artifacts/ui-parity/my-comparison-20260827-154107/my-page-metrics.md, artifacts/uiux-svelte-my-current-20260827-154107/report.json, artifacts/uiux-svelte-notifications-current-20260825-214918/report.json

## 증거표

| 영역 | 원본 코드 근거 | 원본 캡처 근거 | Svelte 코드 근거 | Svelte DOM/캡처 근거 | 판정 |
|---|---|---|---|---|---|
| 마이페이지 프로필 요약 | protected.py:105-126, profile_summary.py:8-52에서 작성자/소속/이메일, 자기소개, 4개 통계와 편집 진입 제공 | 기존 비교 리포트 인증 상태에 동일 텍스트와 통계 존재 | my/+page.svelte:109-159에서 동일 정보·통계·프로필 편집 제공 | 기존 report.json 기본 상태에 해당 텍스트와 controls 존재 | pass (구조) |
| 마이페이지 프로젝트 관리 | protected.py:128-172에서 프로젝트별 보기/수정/삭제와 빈 상태 제공 | my-page, my-delete-confirm, my-unread-badge-fixture 상태 캡처 존재 | my/+page.svelte:183-253에 카드, 상태/NEW, 보기/수정/삭제와 삭제 다이얼로그 구현 | 기존 리포트에서 populated/delete/unread 상태와 overflow 없음 확인. 신규 DOM 실측은 미실행 | partial |
| 마이페이지 프로필 수정 | protected.py:190-244에서 이름/소속/자기소개, 300자 제한, 취소/저장 제공 | 기존 인증 캡처의 my-profile-edit-open 상태 | my/+page.svelte:80-107, 140-181에서 동일 입력·제한·저장 처리 | 기존 리포트에서 form 1개, input 3개, profile_edit 1개 확인. 저장 왕복 신규 실측은 미실행 | partial |
| 알림 목록/자동 읽음 | notifications.py:19-62에서 최근 알림 목록, 프로젝트 보기, 페이지 진입 후 전체 읽음 처리 | 기존 Streamlit/Svelte 알림 캡처와 상태 리포트에 populated 목록 존재 | notifications/+page.svelte:22-60에서 로드 후 unread 전체 읽음, 113-143에서 목록/프로젝트 이동 제공 | 기존 Svelte 리포트에서 notifications 4개와 프로젝트 보기 버튼 존재. 현재 DOM 신규 실측은 미실행 | partial |
| 헤더 알림 팝오버 | layout.py:154-198의 최근 5개, 상태/프로젝트 보기/모두 읽음/모두 보기 | 기존 desktop/mobile-notifications-header-popover 캡처와 report에 open 상태 존재 | AuthNav.svelte:87-180에서 클릭 토글, 최근 5개, 읽음/모두 읽음/모두 보기 제공 | 기존 모바일 리포트에서 팝오버 rect가 left=-206, right=54로 화면 밖으로 나간 증거 확인 | partial -> 수정 반영, 재캡처 필요 |

## 이번 회차 수정

- AuthNav.svelte에 팝오버 DOM 측정과 수평 경계 보정 추가. 열릴 때 viewport 안쪽 12px 여백을 확보한다.
- app.css의 열린 팝오버 transform에 --notification-popover-shift 적용.
- 서버/데이터 계약과 알림 읽음 의미는 변경하지 않았다.

## 검증

- npm.cmd run check: 0 errors, 0 warnings
- npm.cmd run build: 통과
- git diff --check: exit 0, CRLF 변환 경고만
- 브라우저 런타임: 사용 가능한 browser 0개. 따라서 이번 수정의 신규 DOM 좌표와 신규 데스크톱/모바일 캡처는 아직 unknown.

## 다음 단계

1. 브라우저 런타임 복구 후 모바일 헤더 팝오버 좌표가 viewport 내부인지 재측정한다.
2. 동일 인증 fixture로 마이페이지 저장 왕복과 프로젝트 삭제 취소/확정을 재검증한다.
3. 동일 알림 fixture로 페이지 진입 전/후 unread 상태, 개별 프로젝트 이동, 모두 읽음을 재검증한다.
4. 그 뒤 상세페이지와 수정페이지의 남은 브라우저 기반 검증으로 이동한다.

## 환경 제약 기록

확인용 dev server는 실행되었으나 Cloudflare dev runtime이 사용자 프로필의 Wrangler registry 경로에 쓰기 권한이 없어 HTTP 500을 반환했다. 이는 제품 기능 판정이 아닌 실행 환경 문제로 분류한다. 확인에 사용한 5174/5175 포트 프로세스는 종료했고 현재 포트는 비어 있다.

## 실행 환경 정상화

프로젝트 내부의 XDG_CONFIG_HOME 및 MINIFLARE_REGISTRY_PATH를 지정하면 Wrangler registry/log 권한 오류 없이 dev server가 실행된다. 현재 http://127.0.0.1:5174/ 에서 /, /my, /notifications, /submit SSR 스모크가 모두 HTTP 200을 반환했다.
