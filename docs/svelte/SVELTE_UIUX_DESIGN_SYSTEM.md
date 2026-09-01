# Svelte UIUX Design System

작성일: 2026-09-01

이 문서는 `svelte_app/` UI를 수정할 때 사용하는 시각 기준과 QA 루틴이다. 현재 기준은 `svelte_app/src/app.css`의 token을 우선하며, 화면별 예외는 token 위에서 좁게 둔다.

## 원칙

- Svelte 화면을 기준으로 작업한다. Streamlit은 원본 비교용이며 새 UI 기준이 아니다.
- 폰트 크기와 간격은 `px` token을 사용한다. 새 `rem`, `em`, viewport 기반 폰트 크기는 추가하지 않는다.
- 한국어 본문과 작은 UI 텍스트는 가독성을 우선한다. 읽어야 하는 라벨·메타·버튼은 최소 `13px` 이상을 기본값으로 본다.
- 굵기는 필요한 계층에만 쓴다. placeholder, input text, 일반 메타, 태그칩은 과한 bold를 피한다.
- 새 UI를 만들 때는 landing copy보다 실제 사용 화면을 우선한다.

## Typography

기본 폰트는 로컬 asset으로 포함한 Pretendard Variable이다.

```css
font-family: "Pretendard Variable", "Pretendard", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", "Apple SD Gothic Neo", "Malgun Gothic", sans-serif;
```

사용 token:

- `--font-size-2xs: 11px`: 보조 배지, 매우 짧은 상태값
- `--font-size-xs: 12px`: 장식성 chip, compact metadata
- `--font-size-sm: 13px`: 작은 라벨, 메타, 보조 버튼의 기본
- `--font-size-base: 14px`: 기본 UI 본문
- `--font-size-md: 15px`: 입력폼, 주요 본문 보조 문장
- `--font-size-lg: 16px`: hero 보조문, 카드 본문 강조
- `--font-size-title-*`, `--font-size-display`: 페이지 제목과 hero
- `--hero-eyebrow-font-size: 19px`: 홈, 서비스소개, 마이페이지, 등록, Power BI 등 주요 hero eyebrow
- `--hero-eyebrow-mobile-font-size: 13px`: 모바일 hero eyebrow
- `--hero-eyebrow-weight`, `--hero-eyebrow-letter-spacing`: 주요 hero eyebrow weight/자간 기준

사용 weight:

- `--font-weight-regular: 400`: input, placeholder, 일반 문장
- `--font-weight-medium: 500`: 보조 chip
- `--font-weight-semibold: 600`: 버튼, 라벨, 탭, 카드 메타 강조
- `--font-weight-bold: 700`: 제목, 주요 숫자, 중요한 카드 제목
- `--font-weight-strong: 800`: 특별한 숫자/브랜드 강조가 필요할 때만 제한적으로 사용

금지 기준:

- placeholder나 input text에 `600+` weight를 주지 않는다.
- 태그칩은 기본적으로 `600` 이하를 사용한다.
- 작은 한국어 문장을 `11px`에 두지 않는다.

## Spacing

간격은 `--space-*` token을 우선한다.

- `--space-2xs: 4px`
- `--space-xs: 6px`
- `--space-sm: 8px`
- `--space-md: 10px`
- `--space-lg: 12px`
- `--space-xl: 14px`
- `--space-2xl: 16px`
- `--space-3xl: 18px`
- `--space-4xl: 20px`
- `--space-5xl: 22px`
- `--space-6xl: 24px`
- `--space-7xl: 28px`
- `--space-8xl: 34px`
- `--space-9xl: 42px`

레이아웃 token:

- `--layout-page-x`, `--layout-page-y`: 페이지 shell 기본 여백
- `--layout-section-gap`: 섹션 사이 간격
- `--layout-panel-gap`: 카드 내부 기본 gap
- `--layout-panel-padding`: 패널 padding
- `--layout-hero-padding-x`, `--layout-hero-padding-y`: hero padding
- `--mobile-page-x`, `--mobile-panel-padding`: 모바일 기준 여백

새 화면에서는 직접값보다 이 token을 먼저 사용한다. 직접값은 이미지 비율, 고정 아이콘, 외부 embed처럼 포맷 자체가 중요한 경우에만 둔다.

## Controls

버튼과 입력폼은 `--control-*`, `--button-*` token을 사용한다.

- `--control-height-sm: 34px`: 작은 CTA, 댓글 버튼
- `--control-height-md: 38px`: 일반 보조 버튼
- `--control-height-lg: 42px`: 일반 CTA
- `--control-height-xl: 44px`: 로그인/검색 등 주요 입력폼
- `--control-radius: 8px`
- `--control-placeholder`
- `--control-focus-ring`
- `--control-disabled-opacity`

상태 기준:

- hover: primary는 더 진한 blue, secondary는 옅은 blue surface
- focus-visible: 모든 button, link, input, select, textarea, summary에 같은 ring 적용
- disabled/loading: opacity token과 cursor 상태를 같이 적용
- danger: border와 text color만 우선 바꾸고, destructive 확정 버튼일 때만 solid red를 쓴다.

## Cards And Lists

카드와 리스트는 `--card-*`, `--list-*`, `--meta-*`, `--chip-*` token을 사용한다.

- `--card-radius`: 일반 행/카드
- `--card-radius-lg`: 큰 빈 상태나 profile card
- `--card-border`, `--card-bg`
- `--card-hover-border`, `--card-hover-shadow`
- `--list-gap`, `--list-row-gap`, `--list-row-padding`
- `--meta-color`, `--meta-font-size`, `--meta-gap`
- `--chip-height`, `--chip-padding-x`

구조 기준:

- 프로젝트 카드는 visual-first 카드다. 썸네일, 제목, 한 줄 설명, 태그, 메타 순서를 유지한다.
- 뉴스/콘텐츠/커뮤니티는 row-first 리스트다. 날짜/출처 같은 메타는 작게, 제목은 한 단계 크게 둔다.
- 댓글은 dense list다. desktop은 행 단위 스캔, mobile은 작성자/본문/액션 순서가 자연스럽게 접히는 구조를 유지한다.
- 빈 상태는 단순 안내 문장만 둔다. 설명이 길어지면 카드가 아니라 페이지 copy에서 해결한다.

## Screen QA Checklist

공통:

- 수평 overflow가 0인지 확인한다.
- 모바일 `390x844`, 데스크톱 `1440x1000`에서 텍스트 겹침이 없는지 본다.
- 긴 한국어 제목이 줄바꿈되어도 버튼, chip, meta와 겹치지 않는지 본다.
- placeholder와 input text가 너무 두껍지 않은지 확인한다.
- keyboard focus ring이 잘 보이고 layout shift를 만들지 않는지 확인한다.

홈:

- hero H1이 첫 viewport에서 잘 읽히는지 본다.
- 검색 input, 검색 버튼, 인기 태그 chip의 밀도가 과하지 않은지 본다.
- 프로젝트 레일이 비어 있을 때 empty panel이 반복되어도 지저분하지 않은지 확인한다.

로그인/회원가입:

- label, input, placeholder가 모두 읽기 쉬운지 본다.
- primary 버튼이 충분히 크고, 하단 링크가 버튼처럼 과하게 보이지 않는지 확인한다.

프로젝트 제출/수정:

- 로그인 필요 panel의 primary/secondary 버튼 대비가 명확한지 본다.
- form field, disclosure, segmented option, progress state가 같은 control 문법을 쓰는지 확인한다.
- 모바일에서 toolbar와 editor control이 접혀도 텍스트가 잘리지 않는지 본다.

마이페이지/알림:

- project card list와 action button이 같은 행 문법을 유지하는지 본다.
- unread badge, date, action이 작은 화면에서 겹치지 않는지 확인한다.

Power BI:

- news row의 `No. 42` 같은 번호가 줄바꿈되지 않는지 본다.
- label chip, title, source link가 mobile에서 한 행 안에 무리하게 끼지 않는지 확인한다.
- external image나 iframe fallback이 빈 카드처럼 보이지 않는지 본다.

프로젝트 상세:

- hero, meta, action row, visual panel, report, comments 순서가 유지되는지 본다.
- Power BI iframe이나 fallback panel이 모바일에서 수평 overflow를 만들지 않는지 확인한다.
- 댓글 작성/답글/삭제 액션이 dense하지만 읽히는지 본다.

## Verification Routine

일반 UI 수정:

```powershell
cd C:\workspace\folio\svelte_app
npm.cmd run check
npm.cmd run test:ui
git diff --check
```

시각 검증이 필요한 UI 수정:

```powershell
npm.cmd run dev:managed -- --Port 5174
npm.cmd run capture:ui -- --base-url http://127.0.0.1:5174 --viewport mobile --route home=/
npm.cmd run capture:ui -- --base-url http://127.0.0.1:5174 --viewport mobile --route powerbi-news=/powerbi
```

성능이나 layout shift가 걱정되는 수정:

```powershell
$env:MEASURE_ROUTES = '/,/powerbi,/submit'
$env:MEASURE_SAMPLE_MS = '2000'
$env:MEASURE_TRANSITIONS = '1'
npm.cmd run measure:routes
```

인증·mutation UI는 fixture와 복구 조건이 준비된 경우에만 `test:ui:auth` 또는 mutation grep을 실행한다.

## Legacy Boundary

Svelte의 표준 검증, 캡처, 성능 측정은 Playwright를 사용한다.

Selenium은 다음 legacy 영역에만 남긴다.

- Streamlit 원본 캡처
- 외부 갤러리 수집
- 과거 migration evidence 재현

Svelte Selenium 스크립트는 `tools/legacy_selenium/`에 보관하며 새 작업에서는 사용하지 않는다.
