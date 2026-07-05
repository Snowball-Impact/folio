from __future__ import annotations

import argparse
import os
import time
from pathlib import Path

from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://localhost:8501")
    parser.add_argument("--output", default="artifacts/home_scroll_stitched.png")
    parser.add_argument("--width", type=int, default=1440)
    parser.add_argument("--height", type=int, default=900)
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
        driver.get(args.url)
        time.sleep(3)

        scroll_info = driver.execute_script(
            """
            const candidates = Array.from(document.querySelectorAll('body, body *'))
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
              .filter((item) => item.delta > 20)
              .sort((a, b) => b.delta - a.delta);

            if (!candidates.length) {
              return { mode: 'window', total: document.documentElement.scrollHeight, viewport: window.innerHeight };
            }

            const chosen = candidates[0];
            window.__folioScrollTarget = document.querySelectorAll('body, body *')[chosen.index];
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
