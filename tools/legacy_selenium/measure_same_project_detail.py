from __future__ import annotations

import json
import time
from dataclasses import dataclass

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

PROJECT_ID = 'dd1ed00c-1458-4f8e-92cb-4f31e319625d'

JS = r'''
return {
  title: document.title,
  bodyStart: document.body.innerText.slice(0, 3000),
  docH: document.documentElement.scrollHeight,
  bodyH: document.body.scrollHeight,
  mainH: (document.querySelector('section.stMain') || document.querySelector('main') || {}).scrollHeight || 0,
  iframes: Array.from(document.querySelectorAll('iframe')).map((f) => ({
    title: f.title || '',
    cls: String(f.className || ''),
    w: Math.round(f.getBoundingClientRect().width),
    h: Math.round(f.getBoundingClientRect().height),
    y: Math.round(f.getBoundingClientRect().top + scrollY),
    src: f.src.slice(0, 140)
  })),
  headings: Array.from(document.querySelectorAll('h1,h2,h3')).map((h) => h.innerText).slice(0, 24),
  svelteSections: Array.from(document.querySelectorAll('.detail-hero,.detail-footer-row,.detail-flow-nav,.visual-panel,.report,.comments-panel,.site-footer')).map((el) => ({
    cls: String(el.className || ''),
    y: Math.round(el.getBoundingClientRect().top + scrollY),
    h: Math.round(el.getBoundingClientRect().height),
    text: el.innerText.slice(0, 120)
  })),
  streamlitBlocks: Array.from(document.querySelectorAll('.st-key-project_detail_visual,.st-key-project_comments_section,.folio-page-hero,.folio-hero-footer-row,[data-testid="stVerticalBlockBorderWrapper"]')).slice(0, 40).map((el) => ({
    cls: String(el.className || ''),
    testid: el.getAttribute('data-testid') || '',
    y: Math.round(el.getBoundingClientRect().top + scrollY),
    h: Math.round(el.getBoundingClientRect().height),
    text: el.innerText.slice(0, 120)
  }))
};
'''

@dataclass
class Target:
    name: str
    url: str
    width: int
    height: int


def measure(target: Target) -> dict:
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument(f'--window-size={target.width},{target.height}')
    driver = webdriver.Chrome(options=options)
    try:
        driver.get(target.url)
        time.sleep(3)
        data = driver.execute_script(JS)
        data['name'] = target.name
        data['url'] = target.url
        data['viewport'] = [target.width, target.height]
        return data
    finally:
        driver.quit()


def main() -> None:
    targets = [
        Target('streamlit-mobile-known', f'http://127.0.0.1:8501/?project_id={PROJECT_ID}', 500, 844),
        Target('svelte-mobile-known', f'http://127.0.0.1:8788/projects/{PROJECT_ID}', 500, 844),
        Target('streamlit-desktop-known', f'http://127.0.0.1:8501/?project_id={PROJECT_ID}', 1424, 1000),
        Target('svelte-desktop-known', f'http://127.0.0.1:8788/projects/{PROJECT_ID}', 1424, 1000),
    ]
    results = [measure(target) for target in targets]
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()