from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageStat

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'artifacts' / 'ui-parity' / 'focus-compare-20260828'
OUT.mkdir(parents=True, exist_ok=True)

PAIRS = {
    'my': {
        'desktop': (ROOT / 'artifacts/ui-parity/streamlit/desktop-my-page.png', ROOT / 'artifacts/playwright/test-results/authenticated-routes-authe-1eb4f-rs-authenticated-state-auth-desktop/my-authenticated.png'),
        'mobile': (ROOT / 'artifacts/ui-parity/streamlit/mobile-my-page.png', ROOT / 'artifacts/playwright/test-results/authenticated-routes-authe-1eb4f-rs-authenticated-state-auth-mobile/my-authenticated.png'),
    },
    'notifications': {
        'desktop': (ROOT / 'artifacts/ui-parity/streamlit/desktop-notifications.png', ROOT / 'artifacts/playwright/test-results/authenticated-routes-authe-eb0dd-rs-authenticated-state-auth-desktop/notifications-authenticated.png'),
        'mobile': (ROOT / 'artifacts/ui-parity/streamlit/mobile-notifications.png', ROOT / 'artifacts/playwright/test-results/authenticated-routes-authe-eb0dd-rs-authenticated-state-auth-mobile/notifications-authenticated.png'),
    },
    'submit': {
        'desktop': (ROOT / 'artifacts/ui-parity/streamlit/desktop-submit.png', ROOT / 'artifacts/playwright/test-results/authenticated-routes-authe-32bc1-rs-authenticated-state-auth-desktop/submit-authenticated.png'),
        'mobile': (ROOT / 'artifacts/ui-parity/streamlit/mobile-submit.png', ROOT / 'artifacts/playwright/test-results/authenticated-routes-authe-32bc1-rs-authenticated-state-auth-mobile/submit-authenticated.png'),
    },
    'detail': {
        'desktop': (ROOT / 'artifacts/ui-parity/streamlit/desktop-detail-known.png', ROOT / 'artifacts/playwright/test-results/authenticated-routes-authe-56031--valid-project-fixture-auth-desktop/detail-authenticated.png'),
        'mobile': (ROOT / 'artifacts/ui-parity/streamlit/mobile-detail-known.png', ROOT / 'artifacts/playwright/test-results/authenticated-routes-authe-56031--valid-project-fixture-auth-mobile/detail-authenticated.png'),
    },
}

try:
    FONT = ImageFont.truetype('arial.ttf', 18)
    SMALL = ImageFont.truetype('arial.ttf', 13)
except Exception:
    FONT = ImageFont.load_default()
    SMALL = ImageFont.load_default()


def open_rgb(path: Path) -> Image.Image:
    return Image.open(path).convert('RGB')


def resize_width(image: Image.Image, width: int) -> Image.Image:
    ratio = width / image.width
    return image.resize((width, max(1, round(image.height * ratio))))


def first_view(image: Image.Image, height: int) -> Image.Image:
    return image.crop((0, 0, image.width, min(image.height, height)))


def difference_ratio(left: Image.Image, right: Image.Image) -> float:
    width = min(left.width, right.width)
    height = min(left.height, right.height)
    left = left.crop((0, 0, width, height))
    right = right.crop((0, 0, width, height))
    diff = ImageChops.difference(left, right)
    changed = sum(1 for pixel in diff.resize((240, 240)).getdata() if max(pixel) > 18)
    return round(changed / (240 * 240), 3)


def lightness(image: Image.Image, height: int) -> dict[str, float]:
    crop = first_view(image, height).resize((120, 120))
    pixels = list(crop.getdata())
    return {
        'very_light': round(sum(1 for r, g, b in pixels if r > 245 and g > 245 and b > 245) / len(pixels), 3),
        'navy': round(sum(1 for r, g, b in pixels if r < 80 and g < 110 and b > r and b > g) / len(pixels), 3),
    }


def header(label: str, width: int) -> Image.Image:
    image = Image.new('RGB', (width, 34), 'white')
    ImageDraw.Draw(image).text((8, 8), label, fill=(11, 31, 63), font=SMALL)
    return image


def sheet(name: str, viewport: str, original: Image.Image, current: Image.Image, full: bool) -> Path:
    target_width = original.width
    original = original if full else first_view(original, 1000 if viewport == 'desktop' else 844)
    current = current if full else first_view(current, 1000 if viewport == 'desktop' else 844)
    current = resize_width(current, target_width)
    original = resize_width(original, target_width)
    column_width = min(target_width, 720)
    original = resize_width(original, column_width)
    current = resize_width(current, column_width)
    height = max(original.height, current.height)
    image = Image.new('RGB', (column_width * 2 + 20, height + 34), (244, 247, 253))
    image.paste(header('Streamlit original', column_width), (0, 0))
    image.paste(header('Svelte current', column_width), (column_width + 20, 0))
    image.paste(original, (0, 34))
    image.paste(current, (column_width + 20, 34))
    path = OUT / f'{name}-{viewport}-{"full" if full else "first-viewport"}.png'
    image.save(path)
    return path


rows: list[dict[str, object]] = []
for name, viewports in PAIRS.items():
    for viewport, (original_path, current_path) in viewports.items():
        if not original_path.exists() or not current_path.exists():
            continue
        original = open_rgb(original_path)
        current = open_rgb(current_path)
        target_height = 1000 if viewport == 'desktop' else 844
        normalized_current = resize_width(current, original.width)
        rows.append({
            'page': name,
            'viewport': viewport,
            'original': str(original_path.relative_to(ROOT)),
            'current': str(current_path.relative_to(ROOT)),
            'original_size': original.size,
            'current_size': current.size,
            'current_height_ratio': round(current.height / original.height, 3),
            'first_viewport_difference_ratio': difference_ratio(first_view(original, target_height), first_view(normalized_current, target_height)),
            'original_first_lightness': lightness(original, target_height),
            'current_first_lightness': lightness(normalized_current, target_height),
            'first_viewport_sheet': str(sheet(name, viewport, original, current, False).relative_to(ROOT)),
            'full_sheet': str(sheet(name, viewport, original, current, True).relative_to(ROOT)),
        })

(OUT / 'report.json').write_text(json.dumps({'pairs': rows}, ensure_ascii=False, indent=2), encoding='utf-8')
lines = [
    '# Focus Page Capture Comparison',
    '',
    '원본과 Svelte 캡처의 viewport/state가 완전히 같지 않으므로 수치는 차이 탐색용이다.',
    '',
    '| page | viewport | original | current | height ratio | first viewport diff | first viewport sheet | full sheet |',
    '| --- | --- | --- | --- | ---: | ---: | --- | --- |',
]
for row in rows:
    lines.append(
        f"| {row['page']} | {row['viewport']} | `{row['original_size']}` | `{row['current_size']}` | "
        f"{row['current_height_ratio']} | {row['first_viewport_difference_ratio']} | "
        f"`{row['first_viewport_sheet']}` | `{row['full_sheet']}` |"
    )
(OUT / 'metrics.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(OUT.resolve())
