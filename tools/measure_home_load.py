from __future__ import annotations

import argparse
import json
import tempfile
import time
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


MILESTONE_SCRIPT = """
const selectors = {
  header: '.st-key-folio_header, header',
  hero: '.folio-hero, [class*="hero"]',
  loadingPanel: '.folio-home-loading-panel',
  browsePanel: '.st-key-folio_browse_panel, .folio-search-container',
  galleryCard: '.folio-project-card, [class*="project-card"], [class*="folio-card"]',
};

function visible(selector) {
  const elements = Array.from(document.querySelectorAll(selector));
  return elements.some((el) => {
    const rect = el.getBoundingClientRect();
    const style = window.getComputedStyle(el);
    return rect.width > 1 && rect.height > 1 && style.visibility !== 'hidden' && style.display !== 'none';
  });
}

function textIncludes(value) {
  return (document.body ? document.body.innerText : '').includes(value);
}

const frames = Array.from(document.querySelectorAll('iframe')).map((frame) => {
  const rect = frame.getBoundingClientRect();
  return {
    src: frame.src || '',
    visible: rect.width > 1 && rect.height > 1,
    width: Math.round(rect.width),
    height: Math.round(rect.height),
  };
});

return {
  readyState: document.readyState,
  bodyTextLength: document.body ? document.body.innerText.length : 0,
  bodyTextStart: document.body ? document.body.innerText.slice(0, 240) : '',
  frames,
  header: visible(selectors.header) || textIncludes('FOLIO'),
  hero: visible(selectors.hero) || textIncludes('휴먼 인사이트') || textIncludes('Power BI'),
  loadingPanel: visible(selectors.loadingPanel) || textIncludes('불러오고 있어요'),
  browsePanel: visible(selectors.browsePanel) || textIncludes('프로젝트를 탐색해보세요'),
  galleryCard: visible(selectors.galleryCard),
};
"""


def cache_busted_url(url: str) -> str:
    parts = urlsplit(url)
    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    query["_folio_measure"] = str(int(time.time() * 1000))
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))


def make_driver(width: int, height: int, profile_dir: str) -> webdriver.Chrome:
    options = Options()
    chrome_path = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
    if chrome_path.exists():
        options.binary_location = str(chrome_path)
    options.add_argument("--headless=new")
    options.add_argument(f"--window-size={width},{height}")
    options.add_argument(f"--user-data-dir={profile_dir}")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-background-networking")
    return webdriver.Chrome(options=options)


def sample_page(driver: webdriver.Chrome) -> dict:
    outer = driver.execute_script(MILESTONE_SCRIPT)
    inner = None
    frame_count = len(driver.find_elements("tag name", "iframe"))
    for index in range(frame_count):
        try:
            driver.switch_to.default_content()
            driver.switch_to.frame(index)
            inner = driver.execute_script(MILESTONE_SCRIPT)
            if inner.get("hero") or inner.get("browsePanel") or inner.get("galleryCard"):
                break
        except Exception:
            inner = None
            continue
    driver.switch_to.default_content()
    return {"outer": outer, "inner": inner}


def milestone_target(sample: dict) -> dict:
    inner = sample.get("inner")
    if inner and any(inner.get(name) for name in ("header", "hero", "loadingPanel", "browsePanel", "galleryCard")):
        return inner
    return sample["outer"]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="https://folio-gapyear.streamlit.app/")
    parser.add_argument("--width", type=int, default=1440)
    parser.add_argument("--height", type=int, default=900)
    parser.add_argument("--duration", type=float, default=40.0)
    parser.add_argument("--interval", type=float, default=0.5)
    parser.add_argument("--runs", type=int, default=1)
    parser.add_argument("--output", default="artifacts/home_load_measure.json")
    parser.add_argument("--screenshot-dir", default="artifacts/home_load")
    args = parser.parse_args()

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    screenshot_dir = Path(args.screenshot_dir)
    screenshot_dir.mkdir(parents=True, exist_ok=True)

    all_runs = []
    for run_index in range(args.runs):
        with tempfile.TemporaryDirectory(prefix="folio-home-load-") as profile_dir:
            driver = make_driver(args.width, args.height, profile_dir)
            started = time.perf_counter()
            milestones: dict[str, float] = {}
            samples = []
            try:
                driver.get(cache_busted_url(args.url))
                while time.perf_counter() - started <= args.duration:
                    elapsed = round(time.perf_counter() - started, 3)
                    sample = sample_page(driver)
                    target = milestone_target(sample)
                    for name in ("header", "hero", "loadingPanel", "browsePanel", "galleryCard"):
                        if target.get(name) and name not in milestones:
                            milestones[name] = elapsed
                            driver.save_screenshot(str(screenshot_dir / f"run{run_index + 1}_{name}_{elapsed:.1f}s.png"))
                    samples.append({"t": elapsed, **sample})
                    if {"header", "hero", "browsePanel", "galleryCard"}.issubset(milestones):
                        break
                    time.sleep(args.interval)
            finally:
                driver.quit()
            all_runs.append({"run": run_index + 1, "milestones": milestones, "samples": samples})

    output.write_text(json.dumps(all_runs, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(all_runs, ensure_ascii=False, indent=2))
    print(f"wrote {output.resolve()}")


if __name__ == "__main__":
    main()
