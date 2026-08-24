# UI Layout And Harmony Deep Dive

작성일: 2026-08-24

이 문서는 기존 Streamlit 캡처와 현재 Svelte 코드/캡처를 다시 대조해, 기능 존재 여부가 아니라 컴포넌트의 위치, 배치, 균형, 조화 관점에서 차이를 정리한다.

## 조사 기준

이번 재조사는 지난 누락을 교훈으로 삼아 다음을 분리해서 봤다.

- Route가 있는가
- 메뉴에 노출되는가
- 로그인/비로그인 조건이 원본과 같은가
- 컴포넌트가 같은 위치와 정보 위계로 보이는가
- 첫 화면에서 시각 무게가 좌우/상하로 균형 잡혀 있는가
- 여백, 카드 크기, 버튼 위치가 원본 디자인 시스템과 조화를 이루는가
- 원본에 없던 badge, label, card, section이 추가되어 화면 밀도를 흐리는가

사용한 기준:

- Streamlit screenshots: `artifacts/ui-parity/streamlit/`
- Svelte screenshots: `artifacts/ui-parity/svelte-current/`
- Contact sheets: `artifacts/ui-parity/design-audit/`
- Design system: `docs/DESIGN_SYSTEM.md`
- Streamlit UI source: `folio_app/pages/*`, `folio_app/components/*`, `folio_app/styles/*`
- Svelte UI source: `svelte_app/src/routes/*`, `svelte_app/src/lib/components/*`, `svelte_app/src/app.css`

주의: `svelte-current` 캡처 일부는 최근 헤더/카드 뱃지 수정 전 상태일 수 있다. 따라서 최종 판단은 캡처 지표와 현재 소스 코드를 함께 대조했다.

## 핵심 결론

현재 Svelte는 기능 범위와 URL 구조는 많이 따라왔지만, 원본 Streamlit의 시각적 성격과 아직 다르다. 가장 큰 차이는 다음 세 가지다.

1. Svelte는 화면을 더 많이 펼쳐 보여준다.
2. 첫 viewport의 흰 여백 비율이 높아져 원본보다 덜 응집돼 보인다.
3. 원본은 히어로, 검색 패널, 레일, 액션 바가 명확한 정렬축을 공유하는데 Svelte는 일부 화면에서 컴포넌트가 섹션 단위로 흩어진다.

이 차이 때문에 Svelte는 더 현대적인 웹앱처럼 보이지만, FOLIO 원본의 “조밀하지만 차분한 갤러리/관리 도구” 감각은 약해진다.

## 정량 신호

대표 캡처 높이:

| 화면 | Streamlit desktop | Svelte desktop | 해석 |
| --- | ---: | ---: | --- |
| Home | 889px | 1683px | 홈이 거의 2배 길어짐. 첫 rail 도달감이 늦어질 수 있음 |
| Detail | 3622px | 6942px | 상세가 문서형으로 늘어남 |
| Submit | 1050px | 6849px | 등록 폼이 한 화면 관리 흐름보다 긴 입력 문서처럼 보임 |
| My Page | 1039px | 6818px | 관리 화면 밀도가 원본보다 크게 낮아짐 |
| Notifications | 1028px | 6787px | 단순 목록 화면치고 지나치게 김 |
| Power BI Learning | 3688px | 7066px | 탭/페이지 제어 대신 모든 콘텐츠를 펼친 영향 |

첫 900px very-light ratio:

| 화면 | Streamlit | Svelte | 해석 |
| --- | ---: | ---: | --- |
| Home desktop | 0.192 | 0.390 | Svelte 홈 첫 화면이 훨씬 밝고 느슨함 |
| Detail desktop | 0.585 | 0.795 | 상세 첫 화면의 시각 무게가 약함 |
| Submit desktop | 0.493 | 0.697 | 등록 첫 화면이 더 비어 보임 |
| Notifications desktop | 0.633 | 0.710 | 알림 패널의 밀도가 약함 |
| Reference desktop | 0.239 | 0.299 | 레퍼런스도 원본보다 약간 가벼움 |
| Power BI News desktop | 0.360 | 0.514 | 뉴스 첫 화면이 원본보다 흰 여백 위주 |

## 전역 배치 차이

### Header

현재 수정 후 맞아진 점:

- `회원가입`은 헤더에서 제거됨.
- `프로젝트 등록`은 비로그인 상태에서도 노출됨.
- 독립 `레퍼런스` 메뉴는 제거되고 Power BI 하위 메뉴 항목으로만 남음.
- 알림 `N` 배지가 복구됨.

남은 차이:

- Streamlit 알림은 header popover다. 최근 알림 preview, 보기, 모두 읽음, 모두 보기까지 헤더에서 해결한다.
- Svelte는 badge link만 있고 preview popover가 없다.
- Streamlit의 로그아웃과 알림 순서는 `로그아웃`, `알림`이다. Svelte는 현재 `알림`, 사용자명, `로그아웃`이라 시선 흐름이 다르다.
- Svelte는 사용자명이 헤더에 노출된다. 원본 헤더 nav에는 사용자명 텍스트가 없다.

수정 필요:

- P0: 사용자명 노출 여부를 원본 기준으로 재검토한다. 원본 parity면 숨긴다.
- P1: 알림 preview popover를 구현하거나, launch defer로 명시한다.
- P1: 인증 상태별 헤더 순서를 Streamlit과 맞춘다.

### Hero Balance

원본 디자인 시스템의 기준:

- desktop `28px 42px 34px`
- min-height 약 220px
- 좌측 copy, 우측 16:9 visual
- visual은 오른쪽 기준선에 붙고, 과한 카드 장식은 피함
- 모바일에서는 visual이 화면을 길게 만들면 숨김

Svelte가 맞는 점:

- 홈/레퍼런스/등록/마이페이지/알림 모두 이미지 또는 visual hero를 갖춤.
- 주요 asset은 복사되어 사용 중.

남은 차이:

- 일부 Svelte hero는 box-shadow가 강해 원본의 border-first surface보다 장식적으로 보인다.
- Detail 첫 viewport는 원본보다 흰 여백이 크고 visual/card와 copy 사이의 긴장감이 약하다.
- Submit/My/Notifications는 같은 hero asset을 쓰지만 아래 섹션과의 간격이 넓어 첫 화면이 느슨해진다.

개선 방향:

- P0: hero 아래 첫 작업 컴포넌트와의 margin을 줄인다.
- P1: hero shadow 사용을 줄이고 border/surface 중심으로 정리한다.
- P1: detail hero는 copy와 card preview의 비율을 다시 조정해 첫 viewport가 비어 보이지 않게 한다.

## 화면별 딥다이브

### Home

맞아진 점:

- 4-slide hero carousel, dots, Folio logo, browse panel, top 10 tags, horizontal rails, 16:9 project cards가 구현됨.
- 홈 카드 상단 플랫폼 badge는 제거됨.
- 인기 태그에서 reference 계열 tag는 제외됨.

남은 배치 차이:

- 원본 browse panel은 연한 blue surface이고 제목은 32px급 중앙 정렬이다. Svelte는 흰 surface, 24px 제목이라 검색 패널의 중심성이 약하다.
- 원본 browse panel의 padding은 `26px 42px 24px`, Svelte는 `22px`로 더 작고 네모난 카드처럼 보인다.
- 원본 인기 태그 라벨은 blue subtle pill로 오른쪽에 붙어 보조 라벨 역할을 한다. Svelte는 muted text라 시각적 anchor가 약하다.
- Svelte 홈은 전체 높이가 1683px로 원본 889px보다 길다. hero + browse + rail 간 수직 여백이 누적된 것으로 보인다.
- Svelte rail title에는 원본의 highlight span 효과가 빠져 있다. 원본은 `새로 공개`, `조회수`, `좋아요` 같은 핵심어만 blue로 강조한다.

수정 필요:

- P0: `.home-browse-panel`을 원본처럼 `#f3f7ff` 계열 surface, 12px radius, `26px 42px 24px` desktop padding으로 되돌린다.
- P0: `.home-search-heading h2`를 원본 32px/800/nowrap 기준으로 맞춘다. 모바일은 15px/normal wrap.
- P1: 인기 태그 라벨을 blue subtle pill로 만든다.
- P1: ProjectRail 제목에 highlight word를 받을 수 있게 API를 바꾸거나 title HTML 없이 안전한 split 렌더링을 구현한다.
- P1: 홈 hero/browse/first rail의 수직 거리와 first rail above-the-fold 여부를 실제 viewport에서 계측한다.

개선하면 좋은 점:

- 홈에는 플랫폼 필터 계약이 원본에 남아 있다. 현재 Svelte 홈은 기본 Power BI scope 중심이다. Reference platform routes가 살아났으므로 home `platforms` query를 유지할지 명확히 결정해야 한다.

### Project Card

맞아진 점:

- 16:9 overlay card, title 2 lines, summary 1 line, tag 최대 4개 + `+N`, footer meta 구조가 맞아짐.
- 상단 Power BI badge 제거됨.
- 24 auto-cover 변형이 구현됨.

남은 배치 차이:

- 원본 hover는 약한 상승과 5px blue border가 핵심이다. Svelte는 border가 1px이고 hover border-color만 바뀌어 원본보다 피드백이 약할 수 있다.
- Svelte 카드 body는 top meta 제거 후 title이 바로 상단 16px 지점에서 시작한다. 원본 카드의 최종 상단 여백과 비교가 필요하다.

수정 필요:

- P1: hover border 두께/box-shadow를 원본 `.folio-gallery-rail .folio-home-card:hover`와 비교해 조정한다.
- P2: 카드 내부 title/summary/tags/footer의 y-position을 캡처 기준으로 미세 조정한다.

### Project Detail

맞아진 점:

- hero + right ProjectCard preview + footer action row 구조가 생겼다.
- like/share/report/edit/delete가 기능적으로 존재한다.

남은 배치 차이:

- 원본 footer action row는 meta, action group, like가 한 horizontal container 안에서 sibling으로 흐른다.
- Svelte는 `.detail-footer-row` 안에 meta와 action bar가 grid row로 나뉘어 있다. 그래서 원본의 한 줄 액션 바보다 더 넓고 아래로 늘어진다.
- 원본 신고/삭제는 dialog로 뜬다. Svelte 신고 form은 footer 아래에 inline으로 펼쳐져 콘텐츠를 밀어낸다.
- 원본 contextual back label은 Reference에서 들어왔을 때 `레퍼런스로 돌아가기`를 유지한다. Svelte는 항상 홈 갤러리로 돌아간다.

수정 필요:

- P0: detail footer를 한 줄 flex/grid로 압축한다. 작성자/소속/등록일과 view/comment/public/copy/like가 같은 수평 축에 놓이도록 한다.
- P0: 신고 form은 기본 inline expansion이 아니라 dialog/modal 또는 compact disclosure로 바꾼다.
- P1: contextual back navigation을 query/referrer 계약으로 복구한다.
- P1: owner/non-owner 액션 버튼이 기본 화면에서 과밀하지 않도록 icon/pill hierarchy를 정리한다.

개선하면 좋은 점:

- 현재 Svelte의 share/report/delete 기능은 원본보다 명시적이다. 기능은 유지하되 기본 시각 상태는 원본처럼 작고 한 줄로 접는 것이 좋다.

### Submit

맞아진 점:

- submit hero asset과 copy는 원본과 맞다.
- PBIX, thumbnail upload/capture 등 기능 범위는 넓게 구현되어 있다.

남은 배치 차이:

- Streamlit 비로그인 submit은 hero + login required 안내로 짧다. Svelte는 onMount redirect라 로딩/전환 상태에서 원본과 다른 경험이 생길 수 있다.
- Svelte submit은 기본정보, 산출물, 프로젝트 내용이 모두 펼쳐진 긴 form이다.
- 원본 project form에는 intro/preview 성격의 구조가 있고, 섹션 header는 제목 왼쪽/설명 오른쪽 규칙을 더 명확히 따른다.
- Svelte form section은 카드가 반복되며 페이지가 길어진다. 기능은 많지만 입력 흐름의 시각적 부담이 커진다.

수정 필요:

- P0: 비로그인 submit은 즉시 redirect만 하지 말고 원본처럼 submit hero와 login-required panel을 보여줄지 결정한다.
- P0: submit form을 primary required fields와 advanced output/thumbnail/PBIX로 나눠 접힘 또는 단계적 disclosure를 둔다.
- P1: form section header를 원본처럼 제목-left/description-right로 맞춘다.
- P1: PBIX/thumbnail controls는 한 section 안에서 시각적으로 종속되게 정리한다.

### My Page

맞아진 점:

- My Page hero asset과 profile summary, stats, portfolio management 기능은 있다.

남은 배치 차이:

- 원본 profile summary는 bordered container 안에서 중앙 정렬되고, 작성자/소속/이메일 값은 20px 기준이다.
- Svelte는 profile summary와 stats grid가 분리되어 있어 원본의 “프로필 카드 하나” 느낌보다 섹션이 흩어진다.
- 원본 portfolio item은 프로젝트 정보 5 : actions 1 비율로 한 줄 관리 카드에 가깝다. Svelte portfolio card는 자체 article과 action column으로 구현됐지만 전체 높이가 길고 stats grid와 list 사이의 리듬이 다르다.
- Svelte는 사용자 관리 화면치고 전체 높이가 지나치게 길다.

수정 필요:

- P1: profile summary와 stats를 하나의 bordered overview surface 안으로 합치는 것을 검토한다.
- P1: portfolio card의 vertical padding과 tag/meta 행 높이를 줄인다.
- P1: 삭제 확인은 버튼 라벨 변경보다 원본 dialog에 가깝게 modal/confirm UI로 바꾼다.

### Notifications

맞아진 점:

- notifications hero asset과 list row 구조가 존재한다.
- 상태 pill, title, time, project button의 기본 구조는 있다.

남은 배치/semantic 차이:

- 원본 notifications page는 페이지를 열면 unread를 자동으로 read 처리한다.
- Svelte 문구는 “페이지를 열면 읽음 처리”라고 쓰지만 실제로는 `모두 읽음` 버튼을 눌러야 한다. 문구와 동작이 불일치한다.
- 원본 header notification popover가 없다.
- Svelte panel은 흰 surface 중심이라 첫 화면이 원본보다 더 비어 보인다.

수정 필요:

- P0: 알림 페이지 진입 시 자동 mark-all-read를 구현하거나 문구를 바꾼다. parity 기준이면 자동 처리다.
- P1: header notification popover preview를 구현한다.
- P1: notifications panel spacing을 더 compact하게 조정한다.

### Reference

맞아진 점:

- platform별 route와 hero logo/tabs가 있다.
- Power BI/Tableau/Data Studio/Streamlit 탭이 표시된다.

남은 배치 차이:

- 원본은 12개 단위 visible count와 scroll sentinel 기반 incremental loading이다. Svelte는 24개 단위 `더 보기` 버튼이다.
- 원본 sort tab은 button이며 JS로 현재 grid를 재정렬한다. Svelte는 link로 route reload 성격이 강하다.
- 원본 reference 캡처는 카드가 더 많이 차 있어 content-heavy하다. Svelte는 데이터 분류 품질에 따라 빈 platform이 발생할 수 있다.
- 원본 hero 로고는 오른쪽 기준선 정렬을 중요하게 다룬다. Svelte도 유사하지만 platform별 logo crop/size 실제 정렬은 다시 캡처가 필요하다.

수정 필요:

- P1: page size를 원본 12 기준으로 맞출지, Svelte 24를 유지할지 결정한다.
- P1: infinite/near-bottom loading을 복구할지 결정한다.
- P1: platform별 card population을 실제 데이터로 검증한다.
- P2: sort tab의 active/interaction을 원본 버튼형에 더 가깝게 조정한다.

### Power BI Hub

라이브 비교 기준:

- 2026-08-24 로컬 Streamlit: `http://127.0.0.1:8501/?page=Power%20BI&topic=...`
- 2026-08-24 로컬 Svelte: `http://127.0.0.1:5173/powerbi?topic=...`
- Selenium 계측 결과: `artifacts/ui-parity/live-powerbi-uiux/report.json`
- 스크린샷: `artifacts/ui-parity/live-powerbi-uiux/*.png`

맞아진 점:

- topic별 hero와 visual asset은 구현되어 있다.
- news는 10개 단위 pagination이 있다.
- header Power BI submenu 항목은 가운데 정렬로 조정했다.
- 2026-08-24 요청 기준으로 Svelte의 `/powerbi` 내부 topic tabs는 제거했다.

라이브 UIUX 비교에서 확인한 핵심 차이:

- 업데이트 페이지 구조가 다르다. Streamlit은 첫 페이지에 `details.folio-powerbi-release-row` 10개가 모두 닫힌 상태로 보인다. 각 행 높이는 약 36px이고, summary에는 index, label, title, `원문` link만 있다.
- Svelte 업데이트는 `article.news-item` 10개가 모두 펼쳐진다. 첫 article 높이는 약 389px라 원본의 접힌 목록 10개를 훑는 UX와 완전히 다르다.
- Streamlit 업데이트 첫 항목을 펼치면 공식 업데이트 영상 카드(`folio-powerbi-news-video`)와 한국어 요약 bullet이 나온다. Svelte는 YouTube 영상 card UI가 없고, video link도 일반 action link로만 노출된다.
- Svelte 업데이트 요약에는 `원문 요약:`으로 시작하는 영어 기반 문장이 그대로 보인다. 원본은 `localize_fix`, `localize_update_feature` 계열 변환을 거쳐 한국어 bullet 중심으로 보인다.
- Streamlit news live height는 viewport 기준 749px로 첫 화면 안에 hero와 10개 접힌 행, pagination이 모두 들어온다. Svelte news live height는 3726px로 같은 정보가 긴 문서형 목록처럼 보인다.
- Learning 원본은 category tabs 5개가 실제로 존재한다. Svelte는 요청 반영으로 내부 tabs를 제거했기 때문에 원본과 달리 모든 category section이 한 번에 펼쳐진다. 결과적으로 Svelte learning live height는 4418px로 길다.
- Community 원본은 tabs 6개와 `folio-powerbi-community-card` 조밀한 card를 쓴다. Svelte는 tabs 없이 전체 `content-row`를 펼치며, 원문 보기 affordance가 원본보다 약하다.
- Certification은 가장 가까운 편이지만 원본 cert card는 로고형 내부 블록과 `공식 페이지 바로가기` CTA가 분리되어 있고, Svelte는 일반 `cert-card`에 summary 중심으로 단순화되어 있다.

수정 필요:

- P0: Svelte news를 Streamlit처럼 `details/summary` 접힘 목록으로 바꾼다. 기본 상태에서는 title이 모두 접혀 있어야 한다.
- P0: Svelte news body는 원문 영어 요약이 아니라 Streamlit의 한국어 변환 규칙을 이식해 한국어 bullet로 렌더링한다.
- P0: Svelte news에 공식 업데이트 영상 card를 복구한다. video thumbnail, `공식 업데이트 영상`, title, `영상 보기` CTA를 원본처럼 details body 상단에 둔다.
- P1: learning/community의 tabs 제거 요청과 원본 parity가 충돌한다. 제품 결정이 필요하다. 원본 parity라면 category tabs를 복구해야 하고, 탭 제거를 유지한다면 섹션별 노출 개수/접힘/pagination으로 길이를 제어해야 한다.
- P1: community row에 `원문 보기` CTA를 원본처럼 명시적으로 복구한다.
- P1: cert card의 내부 로고 블록과 CTA affordance를 원본에 가깝게 조정한다.

### Auth

맞아진 점:

- 회원가입은 헤더가 아니라 login card 내부 secondary action으로 남아 있다.
- login/signup/reset route는 존재한다.

남은 배치 차이:

- 원본 login secondary actions는 버튼 2개가 같은 폭 column으로 배치된다.
- Svelte는 text link 두 개다. 기능상 가능하지만 원본의 action affordance보다 약하다.
- 원본 reset flow는 login 화면 내부 toggle/update 흐름이다. Svelte는 별도 `/reset-password` route다.

수정 필요:

- P2: login secondary actions를 원본처럼 button-like 2-column으로 조정한다.
- P2: reset flow route 분리는 유지하더라도 login 화면에서 열리는 느낌을 줄지 결정한다.

## 우선순위

### P0: 원본과 다르면 바로 체감되는 문제

1. Home browse panel 색/크기/중심성 복구
2. Detail footer action row 한 줄 압축
3. Detail 신고 inline form을 dialog/compact disclosure로 변경
4. Notifications 문구와 자동 읽음 동작 일치
5. Power BI news pagination 복구
6. Submit 비로그인 경험과 form progressive disclosure 결정

### P1: 시각적 완성도와 구조적 조화

1. Header 사용자명/순서/notification popover parity
2. Home rail title highlight 복구
3. My Page profile summary + stats 통합 검토
4. Reference visible count/infinite loading 결정
5. Power BI content density를 탭 없이 제어
6. Card hover border/내부 y-position 미세 조정

### P2: 개선하면 더 좋아지는 polish

1. Auth secondary actions button-like layout
2. Shadow 사용 줄이고 border-first surface로 정돈
3. 플랫폼별 reference logo crop/size 재캡처 검증
4. 모바일 hero visual hiding 기준 재검증
5. Query compatibility와 contextual back behavior 보강


## 2026-08-24 P0 반영 기록

이번 조사 직후 원본과 다르면 바로 체감되는 항목부터 일부 반영했다.

- Home browse panel: 원본처럼 연한 blue surface, 12px radius, 넓은 desktop padding, 32px급 중앙 제목, blue subtle `인기 태그 TOP10` pill로 조정했다.
- Project Detail: footer row를 한 줄 flex 축으로 압축하고, 신고 입력은 inline expansion 대신 modal layer로 띄우도록 바꿨다.
- Notifications: “페이지를 열면 읽음 처리” 문구와 실제 동작을 맞추기 위해 진입 후 unread가 있으면 `markAllNotificationsRead()`를 호출한다.
- Power BI News: 원본처럼 한 화면에 모든 소식을 펼치지 않고 10개 단위 pagination을 추가했다.
- Submit: 비로그인 사용자를 즉시 redirect하지 않고, 원본처럼 hero 아래 로그인 필요 panel을 먼저 보여준다.

검증:

- `npm.cmd run check` 통과
- `npm.cmd run build` 통과
- `git diff --check` whitespace 오류 없음, CRLF 경고만 있음

## 이번 누락에서 얻은 실무 체크리스트

다음부터 UI parity를 볼 때는 항목별로 다음 질문을 반드시 통과시킨다.

1. 원본에는 이 메뉴/뱃지/라벨이 실제로 있었나?
2. 있었다면 어느 인증 상태에서 보였나?
3. 라우트는 있어도 헤더에는 숨겨야 하는가?
4. 같은 정보가 원본과 같은 컨테이너 안에 있는가?
5. 원본의 시선 시작점과 Svelte의 시선 시작점이 같은가?
6. 첫 viewport에서 가장 무거운 요소가 원본과 같은 위치에 있는가?
7. 카드/패널의 상단 라벨, metadata, helper text가 불필요하게 늘어나지 않았는가?
8. 긴 화면은 원본도 긴가, 아니면 Svelte가 모든 것을 펼쳐서 길어진 것인가?

## 다음 액션 제안

1. P0 항목 중 Home browse panel과 Detail footer부터 수정한다.
2. 그 다음 Notifications 자동 읽음과 Power BI pagination을 맞춘다.
3. 이후 Submit/My Page의 긴 화면 문제를 progressive disclosure와 compact management card로 줄인다.
4. 수정 후 `svelte-current`를 다시 캡처해서 이 문서의 정량 지표를 갱신한다.

## 2026-08-24 P1 반영 기록

P0 이후 원본과 비교했을 때 화면의 균형과 정보 밀도 차이가 계속 보이는 항목을 추가 반영했다.

- Header: 로그인 상태에서 사용자명 텍스트를 헤더에 노출하지 않고, 원본처럼 `마이 페이지` -> `로그아웃` -> 알림 순서로 정리했다. 알림은 배지만 두지 않고 최근 알림 preview popover와 `모두 읽음` action을 함께 제공한다.
- Home rails: `새로 공개`, `조회수`, `좋아요` 같은 핵심 단어를 blue highlight로 분리해 원본 rail title의 시선 포인트를 복구했다.
- My Page: profile summary와 stats를 따로 떨어진 카드처럼 보이지 않게 하나의 overview surface 안에 묶어, 원본의 “내 계정 현황” 덩어리감에 가깝게 정리했다.
- Power BI: 한때 learning/community 길이 제어를 위해 category/topic tabs를 추가했으나, 2026-08-24 후속 요청에서 header submenu로 이동축을 수렴하기 위해 `/powerbi` 내부 상단 tabs를 제거했다. 남은 과제는 탭 없이 content density를 줄이는 것이다.

검증:

- `npm.cmd run check` 통과
- `npm.cmd run build` 통과, Cloudflare adapter output 생성 확인
- `git diff --check` whitespace 오류 없음, CRLF 경고만 있음

## 다음 액션 갱신

1. 원본 Streamlit 캡처와 Svelte 현재 화면을 다시 캡처해 P0/P1 반영 후의 시각 차이를 재측정한다.
2. P1 잔여인 reference visible count/infinite loading, card hover/y-position 미세 조정을 확인한다.
3. P2 auth secondary actions, shadow/border surface polish, mobile hero visual 기준을 순서대로 다듬는다.

## 2026-08-24 소규모 UI 수정 지연 원인

nav font/underline/card footer처럼 작은 시각 수정도 예상보다 오래 걸릴 수 있음을 확인했다.

원인:

- 큰 `app.css` 누적 diff 속에서 이번 변경 범위를 분리하지 못하면, 실제 수정량보다 검증 비용이 커진다.
- `apply_patch`가 Windows sandbox helper 오류로 실패했고, PowerShell 치환은 quote와 LF/CRLF 차이에 취약했다.
- hover underline은 `a`뿐 아니라 nav direct `button`에도 적용되어야 했는데, 요소 타입 계약을 처음에 닫지 않아 추가 확인이 필요했다.
- 카드 footer는 단순 CSS만이 아니라 `ProjectCard.svelte` DOM 구조 변경이 필요했다. CSS만 먼저 보려 하면 한 번에 닫히지 않는다.

다음 교훈:

1. 사소한 UI 요청도 “DOM 변경인지 CSS 변경인지”를 먼저 나눈다.
2. selector 대상이 `a`, `button`, submenu, nested link 중 어디까지인지 먼저 적는다.
3. 카드 내부 배치는 grid area 이름과 DOM wrapper를 동시에 확인한다.
4. Windows 편집 환경에서는 줄바꿈/quote 문제가 보이면 즉시 좁은 파일 조각을 읽고 패턴을 맞춘다.

## 2026-08-24 Power BI 실제 localhost 재비교 기록

사용자 지적 후 Streamlit 원본(`127.0.0.1:8501`)과 Svelte 현재(`127.0.0.1:5173`)를 동시에 띄워 Power BI 화면을 다시 계측했다. 이전 비교는 캡처와 코드 구조 위주라서 실제 UI 상태, 특히 접힌 disclosure와 영상 카드 노출을 놓쳤다.

확인된 원본 기준:

- Update/news 목록은 `details` 행 10개가 기본 접힘 상태이며, 접힌 행은 약 36px 높이의 compact row다.
- 행을 열면 Microsoft 공식 업데이트 영상 카드와 한글 요약 bullet이 함께 나온다.
- `원문 요약:` 같은 번역 전 라벨이나 영어 설명을 그대로 보여주지 않는다.
- Learning/Community에는 원본 기준 category tab이 존재하지만, 현재 Svelte 방향은 header submenu로 축을 모으는 요청과 충돌하므로 별도 의사결정 항목으로 남긴다.

반영한 수정:

- `Power BI News`를 펼쳐진 article 목록에서 `details/summary` 기반 접힘 row로 변경했다.
- 공식 update video row를 뉴스 데이터 계약에 포함하고, 관련 release row 내부에서도 video card를 노출하도록 했다.
- Streamlit의 `powerbi_i18n.py` 규칙을 참고해 월간 업데이트/patch/changelog 요약을 한국어 문장으로 생성하도록 TypeScript 서버 데이터 변환을 보강했다.
- 접힌 행 grid를 화살표, 번호, 라벨, 제목, 원문 링크 5컬럼으로 정리해 원본의 한 줄 밀도를 맞췄다.

검증 결과:

- `tools/probe_svelte_powerbi_news.py` 재계측: `details=10`, `summary=10`, `englishSummary=false`, 첫 접힘 행 높이 `38px`, 첫 행 open 후 영상 카드 확인.
- `npm.cmd run check` 통과, `svelte-check` 0 errors/0 warnings.
- `git diff --check` whitespace 오류 없음, CRLF 경고만 있음.

교훈:

1. 원본 parity는 캡처 파일만으로 판단하지 말고, 반드시 실제 localhost에서 closed/open/hover/click state를 계측한다.
2. “화면이 비슷하다”가 아니라 row count, row height, default open state, body text language, media presence를 숫자와 DOM으로 확인한다.
3. Streamlit `st.expander`, `st.tabs`, custom HTML처럼 상태를 가진 UI는 Svelte에서 단순 card/article로 바꾸면 정보 밀도와 UX가 즉시 달라진다.
4. 데이터 계약에는 화면에 보이는 제목뿐 아니라 source URL, video URL, localized summary, standalone video item 여부까지 포함해야 한다.

## 2026-08-24 Power BI 하위 페이지 P1 반영 기록

업데이트 화면 parity를 맞춘 뒤, 원본과 충돌하지 않는 하위 페이지 UIUX 차이부터 반영했다.

반영한 수정:

- Community: 일반 `content-row` 대신 원본의 `folio-powerbi-community-card`에 가까운 전용 card 구조로 변경했다.
- Community: title row 우측에 `원문 보기` CTA를 복구하고, summary row 우측에는 topic tag를 분리 배치했다.
- Certification: 단순 텍스트 카드 대신 원본처럼 내부 logo block, certification name, `공식 페이지 바로가기` CTA로 구성했다.
- Certification: PL-300은 `Microsoft Certified / PL-300 / Power BI Data Analyst`, KCCI는 `KCCI / BI Specialist / 경영정보시각화능력` 시각 구조로 맞췄다.

검증 결과:

- `npm.cmd run check` 통과, `svelte-check` 0 errors/0 warnings.
- `git diff --check` whitespace 오류 없음, CRLF 경고만 있음.
- Selenium localhost 계측: Community `communityLinks=20`, Certification `certLogos=2`, KCCI label 확인.

남은 판단 지점:

- Learning/Community 원본은 내부 category tabs가 있지만, 현재 Svelte는 header submenu 중심 요청에 따라 내부 tabs를 제거한 상태다. 원본 parity를 더 우선하면 tabs를 복구해야 하고, 현재 IA를 유지하면 section별 접힘 또는 pagination으로 길이와 스캔성을 줄이는 방향이 맞다.

## 2026-08-24 Power BI 밀도 조정 반영 기록

Power BI 하위 페이지의 내부 category tabs는 복구하지 않고, header submenu 중심 IA를 유지하면서 화면 길이와 스캔성을 줄였다.

반영한 수정:

- Learning: 모든 category를 한 번에 펼치던 구조를 `details/summary` 기반 category disclosure로 바꿨다.
- Learning: 첫 category만 기본 open, 나머지는 50px 안팎의 compact summary row로 접어 첫 화면 밀도를 낮췄다.
- Community: 20개 전체 노출 대신 10개 단위 pagination을 추가했다.
- Community: 기존 원본형 card 구조와 `원문 보기` CTA는 유지했다.

검증 결과:

- Selenium localhost 계측: Learning `learning-section=5`, 첫 section만 open, body height 약 `1149px`.
- Selenium localhost 계측: Community 첫 page `community-card=10`, `community-link=10`, page indicator `1 / 2`, body height 약 `1697px`.
- `npm.cmd run check` 통과, `svelte-check` 0 errors/0 warnings.
- `git diff --check` whitespace 오류 없음, CRLF 경고만 있음.

남은 판단 지점:

- 원본 Streamlit의 tab UI 자체를 복구할지는 아직 제품 결정 항목으로 남긴다. 현재 구현은 “원본의 정보 밀도”와 “Svelte의 상단 submenu IA” 사이의 절충안이다.

## 2026-08-24 Power BI 재캡처 결과

업데이트/Community/Certification/Learning 수정 후 Streamlit 원본(`127.0.0.1:8501`)과 Svelte 현재(`127.0.0.1:5173`)를 다시 live 비교했다.

생성 artifact:

- `artifacts/ui-parity/live-powerbi-uiux/report.json`
- `artifacts/ui-parity/live-powerbi-uiux/streamlit-*.png`
- `artifacts/ui-parity/live-powerbi-uiux/svelte-*.png`
- `artifacts/ui-parity/live-powerbi-uiux/powerbi-live-contact-sheet.png`

재측정 요약:

- News: 원본/Svelte 모두 접힌 `details` 10개, source link 17개. 첫 행 높이는 원본 `36px`, Svelte `38px`, hero 높이는 `235px` vs `232px`로 근접했다.
- Learning: 원본은 category tabs 5개, Svelte는 disclosure 5개다. 첫 section만 open으로 바꿔 Svelte body height를 약 `1146px`까지 줄였지만, tab UI 자체는 제품 결정상 복구하지 않았다.
- Community: 원본 card 높이 약 `107px`, Svelte card 높이 약 `105px`로 카드 구조는 거의 맞았다. 원본은 tabs 6개, Svelte는 tabs 없이 10개 pagination(`1 / 2`)으로 절충했다.
- Certification: card 2개, 첫 card 높이 원본/Svelte 모두 약 `244px`. hero는 원본 `297px`, Svelte `261px`로 Svelte가 더 낮다.

남은 시각 차이:

1. Learning/Community의 내부 tabs 존재 여부: 원본 parity만 보면 tabs 복구가 맞지만, 현재 IA 결정은 header submenu 중심이다.
2. Certification hero 높이: Svelte cert hero가 원본보다 약 `36px` 낮아 badge/poster visual의 여백감이 약간 다르다.
3. Svelte content width: Svelte main content가 `x=28`, 원본 Streamlit content가 `x=80` 부근이라 Svelte가 더 넓게 펼쳐진다. 전역 layout 폭 결정과 연결되어 별도 판단이 필요하다.

## 2026-08-24 Power BI 폭/Certification Hero 조정 기록

Power BI live 재캡처에서 남은 즉시 수정 가능한 시각 차이였던 content width와 certification hero height를 조정했다.

반영한 수정:

- Power BI 전용 hero와 content section에 `width: min(100%, 1238px)`와 중앙 정렬을 적용했다.
- 전역 `.page-shell` 폭은 유지해 다른 화면 영향은 피했다.
- Certification hero `min-height`를 원본과 같은 약 `297px`로 조정했다.

검증 결과:

- Svelte News hero/card: `w=1238`, `x=78`, 첫 news row `h=38`.
- Svelte Community card: `w=1238`, `x=78`, 첫 card `h=105`.
- Svelte Certification hero: `h=297`, 첫 card `y=421`, 원본 기준 hero `h=297`, 첫 card `y=419`에 근접.
- `npm.cmd run check` 통과, `svelte-check` 0 errors/0 warnings.
- `git diff --check` whitespace 오류 없음, CRLF 경고만 있음.

## 원본 클로닝 파악법

Streamlit 원본을 Svelte로 클로닝할 때는 “비슷한 기능을 구현했는가”보다 “원본 화면이 어떤 조건에서 어떤 상태로 보였는가”를 먼저 닫아야 한다. 이번 작업에서 놓친 항목들은 대부분 route, 컴포넌트, 데이터 존재 여부를 본 뒤 실제 화면 상태 계약을 늦게 확인해서 생겼다.

권장 순서:

1. 원본을 실제 localhost로 띄운다. 캡처 파일만 보지 말고 `127.0.0.1:8501`에서 인증 상태, query param, hover, open/closed, pagination, tab state를 직접 확인한다.
2. Svelte도 같은 viewport와 같은 데이터 조건으로 띄운다. 이번 Power BI 비교는 `1424x900` desktop 기준으로 Streamlit/Svelte를 동시에 계측했다.
3. 화면별로 “기본 상태”를 먼저 기록한다. 예: row가 접혀 있는가, 첫 tab은 무엇인가, 첫 section은 열려 있는가, 몇 개 카드가 첫 화면에 노출되는가.
4. DOM 계약을 숫자로 기록한다. 예: hero `x/y/w/h`, 첫 카드 `x/y/w/h`, row height, card count, source link count, tab count, scrollHeight.
5. 텍스트 계약을 확인한다. 원본에 없는 메뉴, badge, eyebrow, helper text, 플랫폼 라벨이 추가되지 않았는지 본다. 반대로 원본에 있던 `프로젝트 등록`, 알림 badge, `원문 보기`, 영상 CTA가 빠지지 않았는지 본다.
6. 데이터 계약을 화면 계약과 분리한다. title/source/date/topic뿐 아니라 thumbnail, video URL, localized summary, standalone item 여부가 UI를 바꾼다.
7. interactive state를 별도로 연다. Streamlit `st.expander`, `st.tabs`, popover, hover submenu는 닫힌 상태와 열린 상태가 서로 다른 화면이다. closed/open을 둘 다 캡처한다.
8. 인증 상태를 나눠 본다. 비로그인/로그인에서 nav, 알림, submit, my page, action button이 다르게 보이면 별도 baseline으로 남긴다.
9. 원본과 다른 결정을 의도적으로 내렸다면 “미구현”이 아니라 “제품 결정”으로 문서화한다. 이번 Learning/Community 내부 tabs 제거가 여기에 해당한다.
10. 수정 후 다시 같은 script로 재캡처한다. 구현 완료는 `npm.cmd run check`가 아니라, 원본 대비 live report 수치가 좁혀졌을 때 선언한다.

클로닝 체크리스트:

- Navigation: 메뉴 이름, 순서, 숨김 여부, hover submenu 접근성, underline 범위, 인증별 노출 조건이 같은가.
- Hero: 첫 viewport의 주인공이 같은가. asset, logo crop, visual side, height, content width, CTA 위치를 비교했는가.
- Cards: 원본에 없는 badge/metadata를 추가하지 않았는가. footer/action/tag 배치가 같은 행과 같은 모서리에 있는가.
- Lists: 원본이 tab/pagination/disclosure/infinite loading 중 무엇을 쓰는가. Svelte가 모든 항목을 펼쳐 화면 길이를 늘리지 않았는가.
- Copy: 한글 요약, CTA label, source label, policy/footer label이 원본과 같은가. 번역 전 라벨이나 영어 요약이 새지 않는가.
- Media: hero image, thumbnail, YouTube card, certification badge/poster, logo asset이 실제로 렌더링되는가.
- Layout: 원본 content `x/w`, 첫 카드 y, row height, gap, section rhythm을 숫자로 확인했는가.
- State: hover/open/click/pagination/empty/loading/error 상태를 기본 캡처와 분리해 확인했는가.
- Data: Supabase/CSV/local static asset 중 어느 출처가 화면을 구성하는지 추적했는가.
- Verification: screenshot, DOM report, contact sheet, `npm.cmd run check`, `git diff --check`를 모두 남겼는가.

이번 작업의 핵심 교훈:

- “전수 조사했다”는 말은 파일과 route를 봤다는 뜻이 아니라, 화면 상태와 DOM 수치를 같은 조건에서 비교했다는 뜻이어야 한다.
- 원본 클로닝에서 가장 위험한 착시는 기능이 더 좋아 보이는 Svelte UI다. 원본에 없던 회원가입 메뉴, reference 메뉴, Power BI badge, extra metadata는 개선이 아니라 parity 위반일 수 있다.
- 반대로 원본의 어색한 구현도 사용자가 익숙한 계약일 수 있다. 접힌 업데이트 행, category tabs, notification badge처럼 작은 요소가 화면 인식을 결정한다.
- 캡처만 보면 접힘/hover/열림 상태를 놓친다. 반드시 live localhost에서 상태를 조작하고 계측해야 한다.
- 디자인 parity는 색상만 맞추는 일이 아니다. 위치, 폭, 첫 시선, 카드 안의 좌하단/우하단 균형, 한 줄 배치, 정보 밀도가 더 먼저 체감된다.