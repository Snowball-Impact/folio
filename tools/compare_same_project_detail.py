from __future__ import annotations

import json
import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageStat

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / 'artifacts' / 'ui-parity' / 'same-project-detail-20260825'

try:
    SMALL = ImageFont.truetype('arial.ttf', 15)
except Exception:
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
        return resized.crop((0, 0, width, max_height))
    return resized


def label(text: str, width: int) -> Image.Image:
    image = Image.new('RGB', (width, 38), 'white')
    ImageDraw.Draw(image).text((10, 10), text, fill=(11, 31, 63), font=SMALL)
    return image


def make_pair_sheet(name: str, left: Image.Image, right: Image.Image, *, viewport_height: int, full: bool) -> Path:
    col_w = 520 if left.width > 600 else 300
    if not full:
        left = left.crop((0, 0, left.width, min(left.height, viewport_height)))
        right = right.crop((0, 0, right.width, min(right.height, viewport_height)))
    left = resize_to_width(left, col_w, 5200 if full else None)
    right = resize_to_width(right, col_w, 5200 if full else None)
    gutter = 24
    head_h = 52
    sheet = Image.new('RGB', (col_w * 2 + gutter, max(left.height, right.height) + head_h), (244, 247, 253))
    sheet.paste(label('Streamlit same project', col_w), (0, 0))
    sheet.paste(label('Svelte same project', col_w), (col_w + gutter, 0))
    sheet.paste(left, (0, head_h))
    sheet.paste(right, (col_w + gutter, head_h))
    path = OUT / f'{name}-same-project-{"full" if full else "first-viewport"}.png'
    sheet.save(path)
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description='Compare Streamlit and Svelte detail captures for one fixture.')
    parser.add_argument('--project-id', required=True)
    parser.add_argument('--streamlit-desktop', type=Path, required=True)
    parser.add_argument('--streamlit-mobile', type=Path, required=True)
    parser.add_argument('--svelte-desktop', type=Path, required=True)
    parser.add_argument('--svelte-mobile', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=DEFAULT_OUT)
    parser.add_argument('--auth-state', default='unknown')
    args = parser.parse_args()

    global OUT
    OUT = args.output if args.output.is_absolute() else ROOT / args.output
    OUT.mkdir(parents=True, exist_ok=True)
    streamlit_desktop = args.streamlit_desktop if args.streamlit_desktop.is_absolute() else ROOT / args.streamlit_desktop
    streamlit_mobile = args.streamlit_mobile if args.streamlit_mobile.is_absolute() else ROOT / args.streamlit_mobile
    svelte_desktop = args.svelte_desktop if args.svelte_desktop.is_absolute() else ROOT / args.svelte_desktop
    svelte_mobile = args.svelte_mobile if args.svelte_mobile.is_absolute() else ROOT / args.svelte_mobile
    pairs = [
        ('desktop', streamlit_desktop, svelte_desktop, 1440, 1000),
        ('mobile', streamlit_mobile, svelte_mobile, 390, 844),
    ]
    rows = []
    for name, stream_path, svelte_path, _width, viewport_height in pairs:
        stream_path = stream_path if stream_path.is_absolute() else ROOT / stream_path
        svelte_path = svelte_path if svelte_path.is_absolute() else ROOT / svelte_path
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

    report = {
        'project_id': args.project_id,
        'auth_state': args.auth_state,
        'source_streamlit_capture': str(streamlit_desktop.parent.relative_to(ROOT)),
        'source_svelte_capture': str(svelte_desktop.parent.relative_to(ROOT)),
        'pairs': rows,
    }
    (OUT / 'same-project-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')

    lines = [
        '# Same Project Detail Comparison',
        '',
        f'- Project: `{args.project_id}`',
        f'- Auth state: `{args.auth_state}`',
        f'- Streamlit capture: `{streamlit_desktop.parent.relative_to(ROOT).as_posix()}`',
        f'- Svelte capture: `{svelte_desktop.parent.relative_to(ROOT).as_posix()}`',
        '',
        '| pair | Streamlit size | Svelte size | height ratio | Streamlit first light/navy | Svelte first light/navy | first viewport | full sheet |',
        '| --- | --- | --- | ---: | --- | --- | --- | --- |',
    ]
    for row in rows:
        sl = row['streamlit_first_viewport']
        sv = row['svelte_first_viewport']
        lines.append(
            f"| {row['pair']} | {tuple(row['streamlit_size'])} | {tuple(row['svelte_size'])} | {row['height_ratio_svelte_to_streamlit']} | "
            f"{sl['very_light']}/{sl['blue_navy']} | {sv['very_light']}/{sv['blue_navy']} | "
            f"`{row['first_viewport_sheet']}` | `{row['full_sheet']}` |"
        )
    (OUT / 'same-project-metrics.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(OUT.resolve())


if __name__ == '__main__':
    main()
