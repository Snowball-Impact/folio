from __future__ import annotations

import json
import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

OUT = Path('artifacts/ui-parity/live-powerbi-uiux')
OUT.mkdir(parents=True, exist_ok=True)

options = Options()
options.add_argument('--headless=new')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--window-size=1424,900')
chrome = Path(r'C:\Program Files\Google\Chrome\Application\chrome.exe')
if chrome.exists():
    options.binary_location = str(chrome)

SCRIPT = r'''
const pick = (s) => Array.from(document.querySelectorAll(s)).map((el) => ({
  tag: el.tagName,
  text: (el.innerText || el.textContent || '').trim().slice(0, 260),
  open: !!el.open,
  href: el.href || '',
  cls: typeof el.className === 'string' ? el.className : ''
}));
const rects = (s) => Array.from(document.querySelectorAll(s)).slice(0, 12).map((el) => {
  const r = el.getBoundingClientRect();
  return {
    tag: el.tagName,
    cls: typeof el.className === 'string' ? el.className : '',
    text: (el.innerText || el.textContent || '').trim().slice(0, 180),
    x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width), h: Math.round(r.height)
  };
});
return {
  body: document.body.innerText.slice(0, 2200),
  height: Math.max(document.body.scrollHeight, document.documentElement.scrollHeight),
  details: pick('details'),
  summary: pick('summary'),
  videos: pick('.news-video-card, a[href*=youtube], a[href*=youtu]'),
  cards: rects('.news-release-row, .news-item, .news-video-card'),
  englishSummary: document.body.innerText.includes('원문 요약:'),
  koreanSignals: ['시각화', '모델링', '업데이트', '수정되었습니다', '공식 업데이트 영상'].filter((t) => document.body.innerText.includes(t))
};
'''

driver = webdriver.Chrome(options=options)
try:
    driver.get('http://127.0.0.1:5173/powerbi')
    time.sleep(2.5)
    result = driver.execute_script(SCRIPT)
    driver.execute_script("const first = document.querySelector('details'); if (first) { first.open = true; }")
    time.sleep(0.4)
    result['afterOpenFirst'] = driver.execute_script(SCRIPT)
    driver.save_screenshot(str(OUT / 'svelte-news-after-fix.png'))
    (OUT / 'svelte-news-after-fix.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2)[:20000])
finally:
    driver.quit()