from __future__ import annotations

import os
import re
import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts" / "ui-parity" / "svelte-current"
BASE = "http://127.0.0.1:8788"
KNOWN_PROJECT_ID = "dd1ed00c-1458-4f8e-92cb-4f31e319625d"


def load_env() -> None:
    for path in [ROOT / ".env", ROOT / "svelte_app" / ".env"]:
        if not path.exists():
            continue
        for raw in path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def safe_name(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_.-]+", "-", value).strip("-")


def build_driver(width: int, height: int) -> webdriver.Chrome:
    options = Options()
    chrome = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
    if chrome.exists():
        options.binary_location = str(chrome)
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--hide-scrollbars")
    options.add_argument(f"--window-size={width},{height}")
    return webdriver.Chrome(options=options)


def full_page_height(driver: webdriver.Chrome) -> int:
    return int(
        driver.execute_script(
            """
            const candidates = [document.documentElement, document.body].filter(Boolean);
            const h = Math.max(...candidates.map((el) => Math.max(
              el.scrollHeight || 0,
              el.offsetHeight || 0,
              el.clientHeight || 0
            )));
            return Math.min(9000, Math.max(900, h));
            """
        )
    )


def capture(driver: webdriver.Chrome, name: str, path: str, width: int) -> str:
    driver.get(f"{BASE}{path}")
    time.sleep(2.0)
    driver.set_window_size(width, full_page_height(driver) + 120)
    time.sleep(0.8)
    target = OUT / f"{safe_name(name)}.png"
    target.parent.mkdir(parents=True, exist_ok=True)
    driver.save_screenshot(str(target))
    return str(target.relative_to(ROOT))


def login(driver: webdriver.Chrome) -> bool:
    email = os.environ.get("FOLIO_TEST_ID")
    password = os.environ.get("FOLIO_TEST_PW")
    if not email or not password:
        return False
    driver.get(f"{BASE}/login")
    time.sleep(1.5)
    inputs = driver.find_elements(By.CSS_SELECTOR, "input")
    if len(inputs) < 2:
        return False
    inputs[0].send_keys(email)
    inputs[1].send_keys(password)
    inputs[1].send_keys(Keys.ENTER)
    time.sleep(4.0)
    return True


def main() -> None:
    load_env()
    OUT.mkdir(parents=True, exist_ok=True)
    public_routes = [
        ("home", "/"),
        ("reference-powerbi-latest", "/references/powerbi?sort=latest"),
        ("reference-powerbi-likes", "/references/powerbi?sort=likes"),
        ("powerbi-news", "/powerbi"),
        ("powerbi-learning", "/powerbi?topic=learning"),
        ("powerbi-community", "/powerbi?topic=community"),
        ("powerbi-cert", "/powerbi?topic=cert"),
        ("about", "/about"),
        ("login", "/login"),
        ("signup", "/signup"),
        ("detail-known", f"/projects/{KNOWN_PROJECT_ID}"),
        ("policy-privacy", "/policy/privacy"),
        ("policy-terms", "/policy/terms"),
    ]
    auth_routes = [
        ("submit", "/submit"),
        ("my-page", "/my"),
        ("notifications", "/notifications"),
        ("edit-known", f"/projects/{KNOWN_PROJECT_ID}/edit"),
    ]
    lines = ["# Current Svelte Capture Manifest", ""]
    for width, label, height in [(1440, "desktop", 1000), (390, "mobile", 844)]:
        driver = build_driver(width, height)
        try:
            for route_name, path in public_routes:
                rel = capture(driver, f"{label}-{route_name}", path, width)
                lines.append(f"- svelte-current / {label}-{route_name} / {rel} / {BASE}{path}")
            login_ok = login(driver)
            lines.append(f"- svelte-current / {label}-auth-login / {'login_ok' if login_ok else 'login_failed'}")
            for route_name, path in auth_routes:
                rel = capture(driver, f"{label}-{route_name}", path, width)
                lines.append(f"- svelte-current / {label}-{route_name} / {rel} / {BASE}{path}")
        finally:
            driver.quit()
    (OUT / "manifest.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print((OUT / "manifest.md").resolve())


if __name__ == "__main__":
    main()