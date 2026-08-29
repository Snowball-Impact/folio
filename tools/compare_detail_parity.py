from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageStat

ROOT = Path(__file__).resolve().parents[1]
STREAM = ROOT / 'artifacts' / 'ui-parity' / 'streamlit'
SVELTE = ROOT / 'artifacts' / 'uiux-svelte-current-20260825-190153'
STAMP = datetime.now().strftime('%Y%m%d-%H%M%S')
OUT = ROOT / 'artifacts' / 'ui-parity' / f'detail-comparison-{STAMP}'
OUT.mkdir(parents=True, exist_ok=True)

PAIRS = [
    ('desktop-known', STREAM / 'desktop-detail-known.png', SVELTE / 'desktop-project-detail-known.png', 1424, 1000),
    ('desktop-owner', STREAM / 'desktop-detail-known.png', SVELTE / 'desktop-project-detail-owner.png', 1424, 1000),
    ('mobile-known', STREAM / 'mobile-detail-known.png', SVELTE / 'mobile-project-detail-known.png', 500, 844),
    ('mobile-owner', STREAM / 'mobile-detail-known.png', SVELTE / 'mobile-project-detail-owner.png', 500, 844),
]

try:
    FONT = ImageFont.truetype('arial.ttf', 22)
    SMALL = ImageFont.truetype('arial.ttf', 15)
except Exception:
    FONT = ImageFont.load_default()
    SMALL = ImageFont.load_default()


def open_rgb(path: Path) -> Image.Image:
    return Image.open(path).convert('RGB')


def avg_color(image: Image.Image) -> tuple[int, int, int]:
    return tuple(round(v) for v in ImageStat.Stat(image.resize((1, 1))).mean)


def lightness_metrics(image: Image.Image, viewport_height: int) -> dict[str, float]:
    crop = image.crop((0, 0, image.width, min(image.height, viewport_height))).resize((120, 120))
    pixels = list(crop.getdata())
    very_light = sum(1 for r, g, b in pixels if r > 245 and g > 245 and b > 245) / len(pixels)
    blue_navy = sum(1 for r, g, b in pixels if b > r and b > g and r < 80 and g < 110) / len(pixels)
    return {'very_light': round(very_light, 3), 'blue_navy': round(blue_navy, 3)}


def resize_to_width(image: Image.Image, width: int, max_height: int | None = None) -> Image.Image:
    ratio = width / image.width
    resized = image.resize((width, max(1, int(image.height * ratio))))
    if max_height and resized.height > max_height:
        resized = resized.crop((0, 0, width, max_height))
    return resized


def label(text: str, width: int, height: int = 38) -> Image.Image:
    im = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(im)
    draw.text((10, 10), text, fill=(11, 31, 63), font=SMALL)
    return im


def make_pair_sheet(name: str, left: Image.Image, right: Image.Image, *, viewport_height: int, full: bool) -> Path:
    col_w = 520 if left.width > 600 else 300
    max_h = 5200 if full else None
    if not full:
        left = left.crop((0, 0, left.width, min(left.height, viewport_height)))
        right = right.crop((0, 0, right.width, min(right.height, viewport_height)))
    l = resize_to_width(left, col_w, max_h)
    r = resize_to_width(right, col_w, max_h)
    gutter = 24
    head_h = 52
    h = max(l.height, r.height) + head_h
    sheet = Image.new('RGB', (col_w * 2 + gutter, h), (244, 247, 253))
    sheet.paste(label('Streamlit original', col_w), (0, 0))
    sheet.paste(label('Svelte current', col_w), (col_w + gutter, 0))
    sheet.paste(l, (0, head_h))
    sheet.paste(r, (col_w + gutter, head_h))
    path = OUT / f'{name}-{"full" if full else "first-viewport"}.png'
    sheet.save(path)
    return path


rows = []
for name, stream_path, svelte_path, width, viewport_height in PAIRS:
    if not stream_path.exists() or not svelte_path.exists():
        continue
    stream = open_rgb(stream_path)
    svelte = open_rgb(svelte_path)
    first_sheet = make_pair_sheet(name, stream, svelte, viewport_height=viewport_height, full=False)
    full_sheet = make_pair_sheet(name, stream, svelte, viewport_height=viewport_height, full=True)
    rows.append({
        'pair': name,
        'streamlit_path': str(stream_path.relative_to(ROOT)),
        'svelte_path': str(svelte_path.relative_to(ROOT)),
        'streamlit_size': stream.size,
        'svelte_size': svelte.size,
        'height_ratio_svelte_to_streamlit': round(svelte.height / stream.height, 2),
        'streamlit_avg_rgb': avg_color(stream),
        'svelte_avg_rgb': avg_color(svelte),
        'streamlit_first_viewport': lightness_metrics(stream, viewport_height),
        'svelte_first_viewport': lightness_metrics(svelte, viewport_height),
        'first_viewport_sheet': str(first_sheet.relative_to(ROOT)),
        'full_sheet': str(full_sheet.relative_to(ROOT)),
    })

report = {'source_svelte_capture': str(SVELTE.relative_to(ROOT)), 'pairs': rows}
(OUT / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')

lines = ['# Detail Parity Comparison', '', f'- Svelte capture: `{SVELTE.relative_to(ROOT).as_posix()}`', '']
lines.append('| pair | Streamlit size | Svelte size | height ratio | Streamlit first light/navy | Svelte first light/navy | first viewport | full sheet |')
lines.append('| --- | --- | --- | ---: | --- | --- | --- | --- |')
for row in rows:
    sl = row['streamlit_first_viewport']
    sv = row['svelte_first_viewport']
    lines.append(
        f"| {row['pair']} | {tuple(row['streamlit_size'])} | {tuple(row['svelte_size'])} | {row['height_ratio_svelte_to_streamlit']} | "
        f"{sl['very_light']}/{sl['blue_navy']} | {sv['very_light']}/{sv['blue_navy']} | "
        f"`{row['first_viewport_sheet']}` | `{row['full_sheet']}` |"
    )
(OUT / 'metrics.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(OUT.resolve())