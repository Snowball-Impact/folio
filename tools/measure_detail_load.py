from __future__ import annotations

import argparse
import json
import tempfile
import time
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


DETAIL_SCRIPT = """
const selectors = {
  header: '.st-key-folio_header, header',
  loadingShell: '.folio-project-detail-loading-hero, .folio-detail-loading-content',
  detailHero: '.folio-project-detail-hero:not(.folio-project-detail-loading-hero)',
  actionGroup: '.folio-detail-action-group',
  visualPanel: '.st-key-project_detail_visual, .folio-visual-heading',
  visualIframe: '.st-key-project_detail_visual iframe, iframe.folio-dashboard-iframe',
  dashboardPlaceholder: '.folio-dashboard-placeholder',
  dashboardIframe: '.folio-dashboard-iframe',
  reportContent: '.folio-detail-content-card',
  comments: '.st-key-project_comments_section, .folio-comments-shell',
  backAction: '.st-key-detail_back_action_row',
};

function visible(selector) {
  const elements = Array.from(document.querySelectorAll(selector));
  return elements.some((el) => {
    const rect = el.getBoundingClientRect();
    const style = window.getComputedStyle(el);
    return rect.width > 1 && rect.height > 1 && style.visibility !== 'hidden' && style.display !== 'none';
  });
}

function exists(selector) {
  return document.querySelector(selector) !== null;
}

function hiddenAfterExisting(selector) {
  return exists(selector) && !visible(selector);
}

function textIncludes(value) {
  return (document.body ? document.body.innerText : '').includes(value);
}

function frameInfo() {
  return Array.from(document.querySelectorAll('iframe')).map((frame, index) => {
    const rect = frame.getBoundingClientRect();
    return {
      index,
      src: frame.src || '',
      title: frame.title || '',
      testid: frame.getAttribute('data-testid') || '',
      visible: rect.width > 1 && rect.height > 1,
      width: Math.round(rect.width),
      height: Math.round(rect.height),
    };
  });
}

return {
  readyState: document.readyState,
  bodyTextLength: document.body ? document.body.innerText.length : 0,
  bodyTextStart: document.body ? document.body.innerText.slice(0, 320) : '',
  frames: frameInfo(),
  header: visible(selectors.header) || textIncludes('FOLIO'),
  loadingShell: visible(selectors.loadingShell) || textIncludes('프로젝트를 불러오고 있어요'),
  detailHero: visible(selectors.detailHero) || textIncludes('프로젝트 상세'),
  actionGroup: visible(selectors.actionGroup),
  visualPanel: visible(selectors.visualPanel) || textIncludes('대표 결과물'),
  visualIframe: visible(selectors.visualIframe),
  dashboardPlaceholder: visible(selectors.dashboardPlaceholder) || textIncludes('대시보드 불러오는 중'),
  dashboardPlaceholderGone: hiddenAfterExisting(selectors.dashboardPlaceholder),
  dashboardIframe: visible(selectors.dashboardIframe),
  documentComplete: document.readyState === 'complete',
  reportContent: visible(selectors.reportContent) || textIncludes('프로젝트 리포트'),
  comments: visible(selectors.comments) || textIncludes('댓글'),
  backAction: visible(selectors.backAction),
};
"""


APP_SIGNALS = ("header", "loadingShell", "detailHero", "visualPanel", "reportContent", "comments")
MILESTONE_NAMES = (
    "header",
    "loadingShell",
    "detailHero",
    "actionGroup",
    "visualPanel",
    "visualIframe",
    "dashboardPlaceholder",
    "dashboardPlaceholderGone",
    "dashboardIframe",
    "documentComplete",
    "reportContent",
    "comments",
    "backAction",
)


def cache_busted_url(url: str) -> str:
    parts = urlsplit(url)
    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    query["_folio_detail_measure"] = str(int(time.time() * 1000))
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


def read_document(driver: webdriver.Chrome) -> dict | None:
    try:
        return driver.execute_script(DETAIL_SCRIPT)
    except Exception:
        return None


def sample_page(driver: webdriver.Chrome) -> dict:
    driver.switch_to.default_content()
    outer = read_document(driver)
    app = None
    component_frames: list[dict] = []

    frame_count = len(driver.find_elements("tag name", "iframe"))
    for frame_index in range(frame_count):
        try:
            driver.switch_to.default_content()
            driver.switch_to.frame(frame_index)
            candidate = read_document(driver)
            if candidate and any(candidate.get(name) for name in APP_SIGNALS):
                app = candidate
                component_frames = sample_component_frames(driver)
                break
        except Exception:
            continue

    driver.switch_to.default_content()
    return {"outer": outer, "app": app, "componentFrames": component_frames}


def sample_component_frames(driver: webdriver.Chrome) -> list[dict]:
    frames = []
    app_frame_count = len(driver.find_elements("tag name", "iframe"))
    for index in range(app_frame_count):
        try:
            driver.switch_to.frame(index)
            sample = read_document(driver)
            if sample:
                frames.append({"index": index, **sample})
            driver.switch_to.parent_frame()
        except Exception:
            try:
                driver.switch_to.parent_frame()
            except Exception:
                pass
            continue
    return frames


def collect_run(
    driver: webdriver.Chrome,
    url: str,
    duration: float,
    interval: float,
    screenshot_dir: Path,
    run_index: int,
) -> dict:
    started = time.perf_counter()
    milestones: dict[str, float] = {}
    samples = []
    driver.get(cache_busted_url(url))

    while time.perf_counter() - started <= duration:
        elapsed = round(time.perf_counter() - started, 3)
        sample = sample_page(driver)
        app = sample["app"] or sample["outer"] or {}
        components = sample["componentFrames"]

        for name in MILESTONE_NAMES:
            reached = bool(app.get(name)) or any(component.get(name) for component in components)
            if reached and name not in milestones:
                milestones[name] = elapsed
                driver.save_screenshot(str(screenshot_dir / f"run{run_index}_{name}_{elapsed:.1f}s.png"))

        samples.append({"t": elapsed, **sample})
        has_dashboard = "dashboardIframe" in milestones
        dashboard_done = not has_dashboard or "dashboardPlaceholderGone" in milestones
        if {"detailHero", "visualPanel", "reportContent", "comments"}.issubset(milestones) and dashboard_done:
            break
        time.sleep(interval)

    return {"run": run_index, "milestones": milestones, "samples": samples}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--width", type=int, default=1440)
    parser.add_argument("--height", type=int, default=900)
    parser.add_argument("--duration", type=float, default=30.0)
    parser.add_argument("--interval", type=float, default=0.5)
    parser.add_argument("--runs", type=int, default=1)
    parser.add_argument("--output", default="artifacts/detail_load_measure.json")
    parser.add_argument("--screenshot-dir", default="artifacts/detail_load")
    args = parser.parse_args()

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    screenshot_dir = Path(args.screenshot_dir)
    screenshot_dir.mkdir(parents=True, exist_ok=True)

    all_runs = []
    for run_index in range(1, args.runs + 1):
        with tempfile.TemporaryDirectory(prefix="folio-detail-load-") as profile_dir:
            driver = make_driver(args.width, args.height, profile_dir)
            try:
                all_runs.append(
                    collect_run(
                        driver,
                        args.url,
                        args.duration,
                        args.interval,
                        screenshot_dir,
                        run_index,
                    )
                )
            finally:
                driver.quit()

    output.write_text(json.dumps(all_runs, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(all_runs, ensure_ascii=False, indent=2))
    print(f"wrote {output.resolve()}")


if __name__ == "__main__":
    main()
