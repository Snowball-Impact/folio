from __future__ import annotations

import argparse
import time
from pathlib import Path
from urllib.parse import quote

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

DEFAULT_PROJECT_ID = "eaa667f4-23d2-4720-b2bc-ea4bc1ac3da2"


def build_driver(width: int, height: int) -> webdriver.Chrome:
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument(f"--window-size={width},{height}")
    return webdriver.Chrome(options=options)


def capture(driver: webdriver.Chrome, base: str, name: str, path: str, out_dir: Path, width: int, height: int) -> None:
    driver.set_window_size(width, height)
    driver.get(f"{base}{path}")
    time.sleep(1.2)
    target = out_dir / f"{name}.png"
    driver.save_screenshot(str(target))
    print(f"captured {target}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Capture Svelte cutover parity screens.")
    parser.add_argument("--base", default="http://127.0.0.1:8788")
    parser.add_argument("--project-id", default=DEFAULT_PROJECT_ID)
    parser.add_argument("--out", default="artifacts/ui-parity/svelte-cutover")
    args = parser.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    project_id = quote(args.project_id)
    routes = [
        ("about", "/about"),
        ("policy-privacy", "/policy/privacy"),
        ("policy-terms", "/policy/terms"),
        ("powerbi-cert", "/powerbi?topic=cert"),
        ("project-detail", f"/projects/{project_id}"),
        ("legacy-about", "/?page=About"),
        ("legacy-policy", "/?page=Policy&type=privacy"),
        ("legacy-project", f"/?page=Home&project_id={project_id}"),
        ("legacy-edit", f"/?page=My%20Page&edit_project={project_id}"),
    ]

    viewports = [("desktop", 1440, 1200), ("mobile", 390, 1100)]
    driver = build_driver(1440, 1200)
    try:
        for viewport_name, width, height in viewports:
            for route_name, path in routes:
                capture(driver, args.base, f"{viewport_name}-{route_name}", path, out_dir, width, height)
    finally:
        driver.quit()


if __name__ == "__main__":
    main()