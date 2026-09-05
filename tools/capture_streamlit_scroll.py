from __future__ import annotations

import argparse
import os
import time
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

from dotenv import load_dotenv
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://localhost:8501")
    parser.add_argument("--output", default="artifacts/home_scroll_stitched.png")
    parser.add_argument("--width", type=int, default=1440)
    parser.add_argument("--height", type=int, default=900)
    parser.add_argument("--wait-for-text", default="", help="Wait until this text appears in the rendered body.")
    parser.add_argument("--wait-seconds", type=int, default=20)
    parser.add_argument("--settle-seconds", type=float, default=0, help="Wait after the ready condition before measuring and capturing.")
    parser.add_argument("--diagnose-embed", action="store_true", help="Print safe iframe/component DOM metrics after the page settles.")
    parser.add_argument("--login", action="store_true", help="Log in with test_id/test_pw or FOLIO_TEST_ID/FOLIO_TEST_PW from env before opening the target URL.")
    parser.add_argument("--via-my-page", action="store_true", help="After login, open the target project through My Page's 보기 action.")
    parser.add_argument("--via-my-page-edit", action="store_true", help="After login, open the first editable project through My Page's 수정 action.")
    parser.add_argument("--keep-parts", action="store_true")
    args = parser.parse_args()

    options = Options()
    chrome_path = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
    if chrome_path.exists():
        options.binary_location = str(chrome_path)
    options.add_argument("--headless=new")
    options.add_argument(f"--window-size={args.width},{args.height}")

    driver = webdriver.Chrome(options=options)
    try:
        if args.login:
            load_dotenv(Path(__file__).resolve().parents[1] / ".env")
            email = os.environ.get("FOLIO_TEST_ID") or os.environ.get("test_id")
            password = os.environ.get("FOLIO_TEST_PW") or os.environ.get("test_pw")
            if not email or not password:
                raise RuntimeError("Login requested but test credentials were not found in env.")
            parts = urlsplit(args.url)
            login_url = urlunsplit((parts.scheme, parts.netloc, "/", "page=Login", ""))
            driver.get(login_url)
            WebDriverWait(driver, args.wait_seconds).until(
                lambda current: len(current.find_elements(By.CSS_SELECTOR, "input")) >= 2
            )
            inputs = driver.find_elements(By.CSS_SELECTOR, "input")
            email_input = next((item for item in inputs if item.get_attribute("type") == "email"), inputs[0])
            password_input = next((item for item in inputs if item.get_attribute("type") == "password"), inputs[1])
            email_input.send_keys(email)
            password_input.send_keys(password)
            password_input.send_keys(Keys.ENTER)
            WebDriverWait(driver, args.wait_seconds).until(
                lambda current: bool(current.execute_script(
                    "return Array.from(document.querySelectorAll('button')).some((button) => "
                    "button.offsetParent !== null && button.textContent.trim() === '로그아웃');"
                ))
            )
            login_diagnostic = driver.execute_script(
                "return {url: location.href, cookieNames: document.cookie.split(';').map((item) => item.trim().split('=')[0]).filter(Boolean), "
                "hasLogout: Array.from(document.querySelectorAll('button')).some((button) => button.offsetParent !== null && button.textContent.trim() === '로그아웃')};"
            )
            print(f"login={login_diagnostic}")
            # Streamlit's encrypted cookie helper commits the browser cookie from
            # its component iframe after the rerun that renders the logout menu.
            time.sleep(5)
        if args.via_my_page or args.via_my_page_edit:
            parts = urlsplit(args.url)
            my_page_url = urlunsplit((parts.scheme, parts.netloc, "/", "page=My%20Page", ""))
            title_hint = args.wait_for_text
            driver.get(my_page_url)
            if title_hint:
                WebDriverWait(driver, args.wait_seconds).until(
                    lambda current: title_hint in current.find_element(By.TAG_NAME, "body").text
                )
            action_text = "수정" if args.via_my_page_edit else "보기"
            WebDriverWait(driver, args.wait_seconds).until(
                lambda current: bool(current.execute_script(
                    "return Array.from(document.querySelectorAll('button')).some((button) => "
                    "button.textContent.trim() === arguments[0] && button.offsetParent !== null);",
                    action_text,
                ))
            )
            clicked = driver.execute_script(
                """
                const titleHint = arguments[0];
                const actionText = arguments[1];
                let match = null;
                for (const button of Array.from(document.querySelectorAll('button')).filter((item) => item.textContent.trim() === actionText && item.offsetParent !== null)) {
                    let node = button.parentElement;
                    while (node && node !== document.body) {
                        if ((!titleHint || (node.innerText || '').includes(titleHint)) && (!match || node.innerText.length < match.node.innerText.length)) {
                            match = {node, button};
                        }
                        node = node.parentElement;
                    }
                }
                if (match) { match.button.click(); return true; }
                return false;
                """,
                title_hint,
                action_text,
            )
            if not clicked:
                raise RuntimeError(f"Could not find the target project's {action_text} action on My Page.")
        else:
            driver.get(args.url)
        if args.login:
            target_diagnostic = driver.execute_script(
                "return {url: location.href, cookieNames: document.cookie.split(';').map((item) => item.trim().split('=')[0]).filter(Boolean), "
                "hasLogout: Array.from(document.querySelectorAll('button')).some((button) => button.offsetParent !== null && button.textContent.trim() === '로그아웃'), "
                "hasLogin: Array.from(document.querySelectorAll('a,button')).some((item) => item.offsetParent !== null && item.textContent.trim() === '로그인')};"
            )
            print(f"target_initial={target_diagnostic}")
        if args.wait_for_text:
            WebDriverWait(driver, args.wait_seconds).until(
                lambda current: args.wait_for_text in current.find_element(By.TAG_NAME, "body").text
            )
        else:
            time.sleep(3)
        if args.settle_seconds > 0:
            time.sleep(args.settle_seconds)

        if args.login:
            settled_diagnostic = driver.execute_script(
                "return {url: location.href, cookieNames: document.cookie.split(';').map((item) => item.trim().split('=')[0]).filter(Boolean), "
                "hasLogout: Array.from(document.querySelectorAll('button')).some((button) => button.offsetParent !== null && button.textContent.trim() === '로그아웃'), "
                "hasLogin: Array.from(document.querySelectorAll('a,button')).some((item) => item.offsetParent !== null && item.textContent.trim() === '로그인'), "
                "bodyHasEmbedToken: document.body.innerText.includes('Embed Token')};"
            )
            print(f"target_settled={settled_diagnostic}")

        if args.diagnose_embed:
            embed_diagnostic = driver.execute_script(
                """
                const visible = (element) => {
                    const style = getComputedStyle(element);
                    const rect = element.getBoundingClientRect();
                    return style.display !== 'none' && style.visibility !== 'hidden' && rect.width > 0 && rect.height > 0;
                };
                const frameMetrics = (element) => {
                    const rect = element.getBoundingClientRect();
                    return {
                        title: element.getAttribute('title') || '',
                        className: String(element.className || ''),
                        width: Math.round(rect.width),
                        height: Math.round(rect.height),
                        display: getComputedStyle(element).display,
                        visibility: getComputedStyle(element).visibility,
                        srcPresent: Boolean(element.getAttribute('src')),
                        visible: visible(element),
                    };
                };
                const topFrames = Array.from(document.querySelectorAll('iframe')).map(frameMetrics);
                const componentFrames = [];
                for (const frame of Array.from(document.querySelectorAll('iframe'))) {
                    try {
                        const doc = frame.contentDocument;
                        if (!doc) {
                            componentFrames.push({ ...frameMetrics(frame), accessible: false });
                            continue;
                        }
                        const report = doc.querySelector('#folio-powerbi-report');
                        const dashboard = doc.querySelector('.folio-dashboard-iframe');
                        const bodyText = (doc.body?.innerText || '').slice(0, 120);
                        componentFrames.push({
                            ...frameMetrics(frame),
                            accessible: true,
                            bodyText,
                            reportPresent: Boolean(report),
                            reportVisible: Boolean(report && visible(report)),
                            dashboardPresent: Boolean(dashboard),
                            dashboardVisible: Boolean(dashboard && visible(dashboard)),
                            nestedIframes: doc.querySelectorAll('iframe').length,
                        });
                    } catch (error) {
                        componentFrames.push({ ...frameMetrics(frame), accessible: false });
                    }
                }
                return {
                    url: location.href,
                    pageTextHasEmbedToken: (document.body?.innerText || '').includes('Power BI Embed Token'),
                    topLevelIframes: topFrames.length,
                    topFrames,
                    componentFrames,
                };
                """
            )
            print(f"embed_diagnostic={embed_diagnostic}")

        scroll_info = driver.execute_script(
            """
            const preferred = Array.from(document.querySelectorAll(
              '[data-testid="stAppViewContainer"], section.stMain, main, body, html'
            ));
            const candidates = preferred
              .map((el, index) => {
                const style = window.getComputedStyle(el);
                return {
                  index,
                  tag: el.tagName,
                  id: el.id || '',
                  className: String(el.className || ''),
                  scrollHeight: el.scrollHeight,
                  clientHeight: el.clientHeight,
                  overflowY: style.overflowY,
                  delta: el.scrollHeight - el.clientHeight,
                };
              })
              .filter((item) => item.delta > 20 && item.clientHeight >= 300)
              .sort((a, b) => b.delta - a.delta);

            if (!candidates.length) {
              return { mode: 'window', total: document.documentElement.scrollHeight, viewport: window.innerHeight };
            }

            const chosen = candidates[0];
            window.__folioScrollTarget = preferred[chosen.index];
            return { mode: 'element', target: chosen, total: chosen.scrollHeight, viewport: chosen.clientHeight };
            """
        )

        total = int(scroll_info["total"])
        viewport = int(scroll_info["viewport"])
        step = max(1, viewport - 80)
        positions = list(range(0, max(total - viewport, 0) + 1, step))
        last = max(total - viewport, 0)
        if not positions or positions[-1] != last:
            positions.append(last)

        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        parts: list[tuple[Path, int]] = []

        for index, y in enumerate(positions):
            if scroll_info["mode"] == "element":
                driver.execute_script("window.__folioScrollTarget.scrollTop = arguments[0];", y)
            else:
                driver.execute_script("window.scrollTo(0, arguments[0]);", y)
            time.sleep(0.5)
            part = output.parent / f"{output.stem}_part_{index:02d}.png"
            driver.save_screenshot(str(part))
            parts.append((part, y))

        images = [Image.open(path).convert("RGB") for path, _ in parts]
        stitched = Image.new("RGB", (images[0].width, total), (245, 248, 252))
        for index, (image, (_, y)) in enumerate(zip(images, parts)):
            crop_top = 0 if index == 0 else 80
            crop_bottom = min(image.height, total - y)
            if crop_bottom <= crop_top:
                continue
            stitched.paste(image.crop((0, crop_top, image.width, crop_bottom)), (0, y + crop_top))

        stitched.save(output)
        if not args.keep_parts:
            for part, _ in parts:
                part.unlink(missing_ok=True)
        print(os.path.abspath(output))
        print(scroll_info)
        print(f"parts={len(parts)}")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
