# FOLIO Portfolio — Pending Updates for Work

> Work 사용량 복구 후 기존 진행관리 문서와 저장소에 일괄 반영하기 위한 변경 요청서  
> 작성일: 2026-09-23  
> 상태: Pending

## 1. 목적

현재 Chat에서 추가 확인된 Evidence와 변경된 판단을 기록한다.

Work 사용이 가능해지면 아래 내용을 기준으로 다음 파일을 일괄 갱신한다.

- `FOLIO_PORTFOLIO_BASELINE.md`
- `EVIDENCE_INVENTORY.md`
- `CASE_STUDY_STORYBOARD.md`

가능하면 저장소의 `docs/portfolio/`에도 동일 내용을 반영한다.

---

## 2. Evidence Inventory 수정사항

### 2.1 Legacy Streamlit Evidence

기존 상태:
- `Missing`

변경:
- `Recoverable / Found`

근거:
- `archive/legacy/`
- `archive/streamlit_app_20260909.zip`
- Migration/UI parity 관련 문서 존재

관련 문서 후보:
- `UI_PARITY_CAPTURE_REPORT.md`
- `UIUX_CAPTURE_EVIDENCE_REVIEW_2026-08-28.md`
- `UIUX_DETAIL_PARITY_REAUDIT_2026-08-28.md`
- `UIUX_FOCUS_CAPTURE_COMPARISON_2026-08-28.md`
- `UIUX_STATE_CAPTURE_RUN_2026-08-25.md`

Work 작업:
- 실제 Legacy 화면을 추출
- Streamlit ↔ SvelteKit 비교에 사용할 최적 캡처 선정
- P10 Migration Evidence로 연결

### 2.2 Power BI Evidence

추가 Verified Supporting Evidence:
- Power BI Embed Health Check 관련 Report 존재
  - `artifacts/reports/embed-health-full-report.json`
  - `artifacts/reports/embed-health-public-report.json`

기존 Verified Evidence 유지:
- PBIX Upload 구현
- Authentication / Ownership
- File Validation
- Rate Limit
- Power BI Access Token
- Workspace Import
- Import Status Polling
- Report / Dataset Metadata
- Embed Token
- Publish State / Error Handling
- GA4 `pbix_import_success = 1`

여전히 Missing인 Visual Evidence:
- [ ] PBIX Upload → Processing → Success 상태 화면
- [ ] 실제 Project Detail의 Interactive Power BI Embedded Report 화면

주의:
- `artifacts/.../routes-powerbi.../powerbi.png`는 Power BI 콘텐츠/큐레이션 페이지이며 실제 Embedded Report 결과 화면으로 사용하지 않는다.

### 2.3 Thumbnail Automation Evidence

추가 Verified Supporting Evidence:
- `thumbnail-capture.ts`
- `capture-url-policy.ts`
- `ProjectHeroThumbnailPreview.svelte`
- `inspect-recent-thumbnails.mjs`
- `probe-thumbnail-storage.mjs`

변경된 해석:
- 단순 Capture 기능 구현뿐 아니라 Capture/Storage 상태 점검까지 포함한 운영 Evidence가 존재한다.

Work 작업:
- 실제 생성 Thumbnail Asset/화면 탐색
- Capture 전/후 Evidence 확보
- P09에서 `Automation → Storage → Operational Inspection` 흐름으로 표현할지 검토

### 2.4 실제 UI / QA Evidence

Verified:
- Playwright 기반 실제 Route 캡처
- 9 Routes × Desktop/Mobile = 18 Visual QA Cases

확인된 화면:
- Home
- Power BI
- References / Power BI
- Submit
- My Page
- Notifications
- Login
- Signup
- Reset Password

주요 파일:
- `artifacts/playwright/test-results/routes-home-renders-a-capture-ready-page-desktop/home.png`
- `artifacts/playwright/test-results/routes-powerbi-renders-a-capture-ready-page-desktop/powerbi.png`
- `artifacts/playwright/test-results/routes-submit-renders-a-capture-ready-page-desktop/submit.png`
- `artifacts/...`의 나머지 Desktop/Mobile Route 캡처
- `contact_sheet.jpg`

Portfolio 활용:
- P01 Cover → Home
- P04 Product Strategy → Home / Power BI Reference
- P11 UX/QA → Contact Sheet / Desktop-Mobile comparison
- Supporting → My Page / Notification / Auth

---

## 3. Storyboard 수정사항

### P08 — Power BI Integration

기존보다 Evidence 수준이 높아짐.

핵심 메시지 후보:

> 사용자의 PBIX 파일을 받아 외부 Power BI API의 비동기 배포 과정을 서비스 내부 Publishing Workflow로 추상화하고, 운영 상태까지 검증했다.

사용 Evidence:
- Backend/API implementation
- Git evolution
- Embed Health Check
- GA4 `pbix_import_success`
- Power BI 관련 실제 FOLIO 화면

Missing:
- 실제 PBIX Publish 상태 변화 화면
- 실제 Embedded Report 결과 화면

최종 Layout:
- 60~65% Publishing Pipeline
- 35~40% Actual Result Evidence
- 실제 Embed 캡처 확보 전에는 mock을 실제 Evidence처럼 사용하지 않는다.

### P10 — Streamlit → SvelteKit Migration

Evidence 상태:
- `Missing`에서 `Recoverable/Strong`으로 상향

추가 활용:
- Legacy archive
- UI parity documents
- Before/After screenshot
- 기존 Page Height Audit

대표 메시지:
> Migration ≠ Improvement by default.

### P09 — Thumbnail Automation

Evidence 상태 강화.

대표 흐름:
`Creator Task → Browser Automation → Storage → Operational Inspection`

단, Portfolio에서는 기술 세부보다 Creator 반복 작업 제거가 먼저 보이도록 유지.

---

## 4. 제작 우선순위 변경

다음 순서로 실제 Portfolio Page 제작:

1. **P08 Power BI Hero**
2. **P10 Streamlit → SvelteKit Migration**
3. **P09 Thumbnail Automation**
4. P06 Architecture
5. P07 Data & Backend
6. P11 UX / QA
7. P12 Production / Troubleshooting
8. 나머지 Product/Overview pages
9. P13 Result / Validation — 2026-10-01 최종 업데이트

---

## 5. Baseline Progress 수정

기존 Progress에 다음 내용을 반영:

- [x] ZIP 내부 Artifact 재검토
- [x] 실제 QA Screenshot 존재 확인
- [x] Power BI Embed Health Check Evidence 확인
- [x] Legacy Streamlit Archive 존재 확인
- [x] Thumbnail 운영 점검 Evidence 확인
- [ ] Legacy Streamlit 실제 화면 추출/선정
- [ ] PBIX Publish 상태 Visual Evidence 확보
- [ ] Actual Interactive Power BI Embed Screenshot 확보
- [ ] Thumbnail 실제 결과 Visual Evidence 선정
- [ ] P08 Power BI Hero Page 제작
- [ ] P10 Migration Page 제작
- [ ] P09 Thumbnail Page 제작
- [ ] 전체 14 Page Visual Design
- [ ] 2026-10-01 GA4/Meta 결과 반영
- [ ] Final QA

---

## 6. Work 복구 후 일괄 요청할 작업

Work에 아래 작업을 한 번에 요청한다.

1. `folio.zip` 원본과 `artifacts/`, `archive/`, 관련 Docs를 다시 검사한다.
2. 이 문서의 Pending 변경사항을 사실관계와 대조한다.
3. `FOLIO_PORTFOLIO_BASELINE.md`를 업데이트한다.
4. `EVIDENCE_INVENTORY.md`를 업데이트한다.
5. `CASE_STUDY_STORYBOARD.md`를 업데이트한다.
6. Legacy Streamlit 화면을 추출하고 SvelteKit과 비교할 Evidence를 선정한다.
7. Thumbnail 실제 결과 Evidence를 탐색/선정한다.
8. Power BI PBIX Publish 및 Embedded Report Visual Evidence가 저장소에 더 있는지 최종 확인한다.
9. 변경된 3개 Markdown 파일을 `docs/portfolio/` 구조로 정리한다.
10. 필요하면 기존 Worklog ZIP도 최신본으로 다시 생성한다.

---

## 7. Fact-check 원칙

- Mock/Diagram과 실제 서비스 Screenshot을 명확히 구분한다.
- 코드 구현 Evidence만으로 실제 사용자 사용을 주장하지 않는다.
- GA4 Event와 실제 사용자 수를 혼동하지 않는다.
- Community/Admin은 구현 검증 전 Result로 표현하지 않는다.
- Market Fit이 검증됐다고 표현하지 않는다.
- Missing Evidence는 Missing 상태로 명시한다.
- Portfolio에서는 기술 나열보다 `Problem → Decision → Build → Evidence → Learning`을 우선한다.
