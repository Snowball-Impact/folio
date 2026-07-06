from __future__ import annotations

import os
import time
from pathlib import Path
from urllib.parse import quote

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options


BASE = "http://127.0.0.1:8501"
OUT = Path("artifacts/ui-audit")


def make_driver(width: int, height: int) -> webdriver.Chrome:
    options = Options()
    chrome = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
    if chrome.exists():
        options.binary_location = str(chrome)
    options.add_argument("--headless=new")
    options.add_argument(f"--window-size={width},{height}")
    return webdriver.Chrome(options=options)


def capture(driver: webdriver.Chrome, name: str, url: str, width: int) -> None:
    driver.get(url)
    time.sleep(4)
    height = driver.execute_script(
        "return Math.min(5000, Math.max(900, document.querySelector('section.stMain')?.scrollHeight || document.body.scrollHeight));"
    )
    driver.set_window_size(width, int(height) + 151)
    time.sleep(1)
    driver.save_screenshot(str(OUT / f"{name}.png"))


def login(driver: webdriver.Chrome) -> None:
    driver.get(f"{BASE}/?page=Login")
    time.sleep(3)
    inputs = driver.find_elements(By.CSS_SELECTOR, "input")
    inputs[0].send_keys(os.environ["test_id"])
    inputs[1].send_keys(os.environ["test_pw"])
    inputs[1].send_keys(Keys.ENTER)
    time.sleep(5)


def main() -> None:
    load_dotenv()
    OUT.mkdir(parents=True, exist_ok=True)

    public = make_driver(1440, 1000)
    try:
        capture(public, "desktop-login", f"{BASE}/?page=Login", 1440)
        capture(public, "desktop-signup", f"{BASE}/?page=Sign%20Up", 1440)
    finally:
        public.quit()

    desktop = make_driver(1440, 1000)
    try:
        login(desktop)
        capture(desktop, "desktop-home", f"{BASE}/?page=Home", 1440)
        capture(desktop, "desktop-submit", f"{BASE}/?page=Submit", 1440)
        capture(desktop, "desktop-my-page", f"{BASE}/?page={quote('My Page')}", 1440)
        project_links = desktop.find_elements(By.CSS_SELECTOR, 'a[href*="project_id="]')
        detail_url = project_links[0].get_attribute("href") if project_links else None
        if detail_url:
            capture(desktop, "desktop-detail", detail_url, 1440)
    finally:
        desktop.quit()

    mobile = make_driver(390, 844)
    try:
        login(mobile)
        capture(mobile, "mobile-home", f"{BASE}/?page=Home", 390)
        capture(mobile, "mobile-submit", f"{BASE}/?page=Submit", 390)
        capture(mobile, "mobile-my-page", f"{BASE}/?page={quote('My Page')}", 390)
    finally:
        mobile.quit()

    print(OUT.resolve())


if __name__ == "__main__":
    main()
