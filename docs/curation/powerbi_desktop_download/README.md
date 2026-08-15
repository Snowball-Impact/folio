# Power BI Desktop Download Curation

Power BI 분석가가 PBIX 보고서를 준비할 때 참고할 최신 Desktop 다운로드 정보를 수집한다.

## 수집 대상

- 원문: Microsoft Power BI Desktop Download Center
- 기본 URL: `https://www.microsoft.com/ko-kr/download/details.aspx?id=58494`
- 저장 위치: `docs/curation/powerbi_desktop_download/all.csv`

## 실행

정기 운영에서는 통합 명령을 사용한다.

```powershell
python tools\collect_powerbi_all.py
```

개별 갱신이 필요할 때는 아래 명령을 사용한다.

```powershell
python tools\collect_powerbi_desktop_download.py
```

## CSV 필드

- `source_url`: 원문 링크
- `version`: 현재 수집된 Power BI Desktop 버전
- `published_at`: 게시일
- `file_name`, `file_size`: 설치 파일 정보
- `description_ko`: Microsoft 다운로드 페이지의 제품 설명
- `capabilities_ko`: 다운로드 페이지에 소개된 주요 작업
- `summary_ko`: FOLIO 콘텐츠 표시용 요약 초안
- `publication_status`: 기본값 `review`

## 활용 아이디어

- PBIX 웹 게시 전 준비 가이드
- "최신 Power BI Desktop으로 PBIX 저장하기" 안내 콘텐츠
- FOLIO의 `PBIX 보고서 무료 게시하기` CTA와 연결되는 도움말 콘텐츠
