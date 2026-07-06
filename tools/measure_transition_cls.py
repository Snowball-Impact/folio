from __future__ import annotations

import argparse
import json
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


def make_driver(width: int, height: int) -> webdriver.Chrome:
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument(f"--window-size={width},{height}")
    return webdriver.Chrome(options=options)


_FIND_SCROLLER_JS = """
const candidates = Array.from(document.querySelectorAll('body, body *'))
  .map((el) => {
    const style = window.getComputedStyle(el);
    return { el, delta: el.scrollHeight - el.clientHeight, overflowY: style.overflowY };
  })
  .filter((item) => item.delta > 20 && (item.overflowY === 'auto' || item.overflowY === 'scroll' || item.overflowY === 'overlay'))
  .sort((a, b) => b.delta - a.delta);
window.__folioScroller = candidates.length ? candidates[0].el : document.scrollingElement;
"""

# Records one sample per animation frame (in-browser, no Selenium round-trip
# latency per sample) so we can catch sub-100ms layout jumps that a
# Python-side polling loop (network round trip per sample) would miss.
_ARM_RECORDER_JS = """
window.__folioSamples = [];
function rect(sel) {
    const el = document.querySelector(sel);
    if (!el) return null;
    const r = el.getBoundingClientRect();
    return [Math.round(r.top * 100) / 100, Math.round(r.height * 100) / 100];
}
const startT = performance.now();
function tick() {
    const scroller = window.__folioScroller || document.scrollingElement;
    window.__folioSamples.push({
        t: Math.round((performance.now() - startT) * 10) / 10,
        scrollTop: scroller ? scroller.scrollTop : null,
        header: rect('.st-key-folio_header'),
        blockContainer: rect('.block-container'),
        stMain: rect('section.stMain'),
        appViewContainer: rect('[data-testid="stAppViewContainer"]'),
    });
    if (performance.now() - startT < arguments[0]) {
        requestAnimationFrame(tick);
    }
}
requestAnimationFrame(tick);
"""


def arm_recorder(driver, duration_ms: int) -> None:
    driver.execute_script(_ARM_RECORDER_JS, duration_ms)


def collect_samples(driver) -> list[dict]:
    return driver.execute_script("return window.__folioSamples;")


def click_button_by_text(driver, text: str):
    buttons = driver.find_elements(By.TAG_NAME, "button")
    for btn in buttons:
        if btn.text.strip() == text:
            btn.click()
            return True
    return False


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://localhost:8501")
    parser.add_argument("--width", type=int, default=1440)
    parser.add_argument("--height", type=int, default=900)
    parser.add_argument("--duration-ms", type=int, default=2000)
    parser.add_argument("--output", default="artifacts/cls_measure.json")
    args = parser.parse_args()

    driver = make_driver(args.width, args.height)
    results = {}
    try:
        driver.get(args.url)
        time.sleep(3)
        driver.execute_script(_FIND_SCROLLER_JS)

        # Scenario: same-page rerun via a tag pill click on Home (no navigation)
        pill_btn = None
        for btn in driver.find_elements(By.TAG_NAME, "button"):
            if btn.text.strip() == "powerbi":
                pill_btn = btn
                break
        if pill_btn is not None:
            arm_recorder(driver, args.duration_ms)
            pill_btn.click()
            time.sleep(args.duration_ms / 1000 + 0.3)
            results["same_page_rerun_tag_pill"] = {"clicked": True, "samples": collect_samples(driver)}
        else:
            results["same_page_rerun_tag_pill"] = {"clicked": False}

        time.sleep(1)
        driver.execute_script(_FIND_SCROLLER_JS)

        # Scenario: Home -> Login (cross-page nav)
        arm_recorder(driver, args.duration_ms)
        clicked = click_button_by_text(driver, "로그인")
        time.sleep(args.duration_ms / 1000 + 0.3)
        results["home_to_login"] = {"clicked": clicked, "samples": collect_samples(driver)}

        time.sleep(1)
        driver.execute_script(_FIND_SCROLLER_JS)

        # Scenario: Login -> Home via logo button
        arm_recorder(driver, args.duration_ms)
        clicked2 = click_button_by_text(driver, "홈으로 이동")
        time.sleep(args.duration_ms / 1000 + 0.3)
        results["login_to_home"] = {"clicked": clicked2, "samples": collect_samples(driver)}

    finally:
        driver.quit()

    with open(args.output, "w", encoding="utf-8") as fh:
        json.dump(results, fh, ensure_ascii=False, indent=2)
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
