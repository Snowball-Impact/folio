from __future__ import annotations

import json
import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

OUT = Path('artifacts/ui-parity/live-powerbi-uiux')
OUT.mkdir(parents=True, exist_ok=True)

chrome = Path(r'C:\Program Files\Google\Chrome\Application\chrome.exe')
options = Options()
options.add_argument('--headless=new')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--window-size=1424,900')
if chrome.exists():
    options.binary_location = str(chrome)

URLS = {
    'streamlit-news': 'http://127.0.0.1:8501/?page=Power%20BI&topic=news',
    'svelte-news': 'http://127.0.0.1:5173/powerbi',
    'streamlit-learning': 'http://127.0.0.1:8501/?page=Power%20BI&topic=learning',
    'svelte-learning': 'http://127.0.0.1:5173/powerbi?topic=learning',
    'streamlit-community': 'http://127.0.0.1:8501/?page=Power%20BI&topic=community',
    'svelte-community': 'http://127.0.0.1:5173/powerbi?topic=community',
    'streamlit-cert': 'http://127.0.0.1:8501/?page=Power%20BI&topic=certifications',
    'svelte-cert': 'http://127.0.0.1:5173/powerbi?topic=certifications',
}

SCRIPT = r'''
const text = document.body ? document.body.innerText : '';
const pick = (sel) => Array.from(document.querySelectorAll(sel)).map((el) => ({
  tag: el.tagName,
  text: (el.innerText || el.textContent || '').trim().slice(0, 260),
  href: el.href || '',
  open: !!el.open,
  cls: typeof el.className === 'string' ? el.className : ''
}));
const rects = (sel) => Array.from(document.querySelectorAll(sel)).slice(0, 10).map((el) => {
  const r = el.getBoundingClientRect();
  return {
    text: (el.innerText || el.textContent || '').trim().slice(0, 160),
    x: Math.round(r.x),
    y: Math.round(r.y),
    w: Math.round(r.width),
    h: Math.round(r.height),
    tag: el.tagName,
    cls: typeof el.className === 'string' ? el.className : ''
  };
});
return {
  title: document.title,
  url: location.href,
  bodySample: text.slice(0, 3000),
  scrollHeight: Math.max(document.body.scrollHeight, document.documentElement.scrollHeight),
  details: pick('details'),
  summary: pick('summary'),
  newsItems: pick('.news-item'),
  newsVideos: pick('.folio-powerbi-news-video, .news-video, a[href*=youtube], a[href*=youtu]'),
  sourceLinks: pick('a').filter(a => /원문|영상|YouTube|공식/.test(a.text)).slice(0, 24),
  tabs: pick('[role=tab], .stTabs button, .content-tabs a, .category-tabs button'),
  learningSections: pick('.learning-section'),
  communityCards: pick('.community-card, .folio-powerbi-community-card'),
  cards: rects('.folio-powerbi-release-row, .news-release-row, .news-item, .folio-powerbi-video-card, .content-card, .learning-section, .folio-powerbi-community-card, .community-card, .content-row, .folio-powerbi-cert-card, .cert-card'),
  hero: rects('.folio-powerbi-hero, .powerbi-hero')
};
'''


def collect(driver: webdriver.Chrome) -> dict:
    return driver.execute_script(SCRIPT)


def main() -> None:
    driver = webdriver.Chrome(options=options)
    try:
        results: dict[str, dict] = {}
        for name, url in URLS.items():
            driver.get(url)
            time.sleep(3.5)
            result = collect(driver)
            driver.save_screenshot(str(OUT / f'{name}.png'))
            if name == 'streamlit-news':
                driver.execute_script("const first = document.querySelector('details'); if (first) { first.open = true; }")
                time.sleep(0.5)
                result['afterOpenFirst'] = collect(driver)
                driver.save_screenshot(str(OUT / f'{name}-first-open.png'))
            results[name] = result
        (OUT / 'report.json').write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
        print(json.dumps(results, ensure_ascii=False, indent=2)[:30000])
    finally:
        driver.quit()


if __name__ == '__main__':
    main()