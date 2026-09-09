# Power BI Content Operations

Power BI 메뉴에 노출하는 외부 콘텐츠 수집/가공 기준입니다.

## 운영 원칙

- 원문은 항상 `source_url` 또는 `video_url`로 남긴다.
- FOLIO에는 한국어 제목과 요약을 보여준다.
- 수집 결과는 기본적으로 `publication_status=review`로 둔다.
- Microsoft 공식 문서, 공식 커뮤니티, 공식 YouTube, 신뢰할 수 있는 실무 크리에이터를 우선한다.
- 정기 수집 후 화면에 노출되는 CSV와 정적 썸네일이 함께 커밋되어야 한다.

## 정기 수집 순서

정기 운영에서는 통합 명령을 먼저 사용한다.

```powershell
python tools\collect_powerbi_all.py
```

이 명령은 Desktop 다운로드, 업데이트 소식, 커뮤니티 소식, 학습 콘텐츠를 순서대로 수집하고,
Power BI 공식 레퍼런스 설정을 검증한 뒤 CSV/썸네일 출력물을 점검한다.

`tools\collect_powerbi_all.py`의 수집 대상은 `Collector` registry에 등록한다. 새 수집원을 추가할 때는
개별 스크립트를 먼저 만들고, 통합 명령의 `COLLECTORS`, `CSV_OUTPUTS`, 필요한 검증 규칙을 함께 갱신한다.
개별 소스만 다시 수집해야 할 때는 아래 세부 스크립트를 사용한다.

## 콘텐츠별 출력물

| 메뉴 | 수집 대상 | 실행 스크립트 | 출력 |
| --- | --- | --- | --- |
| 업데이트 소식 Hero | Power BI Desktop 다운로드 | `tools\collect_powerbi_all.py` / `tools\collect_powerbi_desktop_download.py` | `docs\curation\powerbi_desktop_download\all.csv` |
| 업데이트 소식 | Microsoft Learn 월간 업데이트 | `tools\collect_powerbi_all.py` / `tools\collect_powerbi_updates.py` | `docs\curation\powerbi_updates\all.csv` |
| 업데이트 소식 | Power BI Desktop QFE 변경 로그 | `tools\collect_powerbi_all.py` / `tools\collect_powerbi_changelog.py` | `docs\curation\powerbi_changelog\all.csv` |
| 업데이트 소식 | Microsoft Power BI 공식 업데이트 영상 | `tools\collect_powerbi_all.py` / `tools\collect_powerbi_learning_videos.py` | `docs\curation\powerbi_update_videos\all.csv` |
| 커뮤니티 소식 | Microsoft Fabric Community Blog RSS | `tools\collect_powerbi_all.py` / `tools\collect_powerbi_community_blog.py` | `docs\curation\powerbi_community_blog\all.csv` |
| 학습 콘텐츠 | YouTube 학습 영상 RSS | `tools\collect_powerbi_all.py` / `tools\collect_powerbi_learning_videos.py` | `docs\curation\powerbi_learning_videos\all.csv` |
| 학습 콘텐츠 | 공식/한국어 과정형 플레이리스트 | `tools\collect_powerbi_all.py` / `tools\collect_powerbi_learning_videos.py` | `docs\curation\powerbi_learning_programs\all.csv` |
| 공식 레퍼런스 | Power BI 레퍼런스 정적 로고/출력물 검증 | `tools\collect_powerbi_all.py` | `static\reference-powerbi-logo-cropped.webp` |

## 현재 수집 기준

- 업데이트/변경 로그는 2025년 이후 항목을 기본 수집한다.
- 커뮤니티 블로그는 RSS 최신 글을 기본 30개까지 수집한다.
- YouTube 학습 콘텐츠는 공식 채널, 해외 실무 채널, 한국 크리에이터를 함께 수집한다.
- 어니언 BI의 과정형 플레이리스트는 `한국 크리에이터` 탭 상단 프로그램 카드로 사용한다.
- Microsoft Power BI 공식 업데이트 영상은 학습 콘텐츠가 아니라 `업데이트 소식`의 월간 업데이트 항목에 연결한다.
- 공식 레퍼런스는 별도 RSS/CSV 수집 대상이 아니라 기존 레퍼런스 프로젝트 DB를 `powerbi` 플랫폼으로 필터링한다.

## 수집 후 점검

```powershell
python -m py_compile tools\collect_powerbi_all.py tools\collect_powerbi_learning_videos.py
npm.cmd run check
npm.cmd run test:unit
npm.cmd run build
```

작은 문구/간격 변경은 화면 테스트를 생략할 수 있다. 구조 변경, 새 카드/탭/HTML 마크업 변경, 스크롤/레이아웃 이슈는 Playwright로 확인한다.

## 화면 반영 구조

- `src/routes/powerbi/+page.svelte`: Power BI 허브 화면, hero, 카드/행 목록을 렌더링한다.
- `src/routes/powerbi/+page.server.ts`: topic별 서버 데이터를 로드한다.
- `src/lib/server/powerbi-content.ts`: CSV 로딩, 커뮤니티/학습 탭 그룹핑, 월간 업데이트와 패치 로그 병합을 담당한다.
- `tests/unit/`: 입력/서식/태그 같은 순수 계약을 보호한다.

## 통합 명령 옵션

```powershell
python tools\collect_powerbi_all.py --dry-run
python tools\collect_powerbi_all.py --since-year 2026
python tools\collect_powerbi_all.py --skip-community
python tools\collect_powerbi_all.py --community-limit 50
```

`--dry-run`은 네트워크 수집을 실행하지 않고 수행 계획과 검증 결과만 확인한다.
