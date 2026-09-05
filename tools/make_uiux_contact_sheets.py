from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path('artifacts/ui-parity')
OUT = ROOT / 'design-audit'
OUT.mkdir(parents=True, exist_ok=True)
STREAM = ROOT / 'streamlit'
CUR = ROOT / 'svelte-current'

pairs = {
    'core-desktop': [
        ('desktop-home', 'desktop-home'),
        ('desktop-detail-known', 'desktop-detail-known'),
        ('desktop-submit', 'desktop-submit'),
        ('desktop-my-page', 'desktop-my-page'),
        ('desktop-notifications', 'desktop-notifications'),
    ],
    'content-desktop': [
        ('desktop-reference-powerbi-latest', 'desktop-reference-powerbi-latest'),
        ('desktop-powerbi-news', 'desktop-powerbi-news'),
        ('desktop-powerbi-learning', 'desktop-powerbi-learning'),
        ('desktop-powerbi-community', 'desktop-powerbi-community'),
        ('desktop-powerbi-cert', 'desktop-powerbi-cert'),
    ],
    'static-auth-desktop': [
        ('desktop-about', 'desktop-about'),
        ('desktop-login', 'desktop-login'),
        ('desktop-signup', 'desktop-signup'),
        ('desktop-policy-privacy', 'desktop-policy-privacy'),
        ('desktop-policy-terms', 'desktop-policy-terms'),
    ],
    'core-mobile': [
        ('mobile-home', 'mobile-home'),
        ('mobile-detail-known', 'mobile-detail-known'),
        ('mobile-submit', 'mobile-submit'),
        ('mobile-my-page', 'mobile-my-page'),
        ('mobile-notifications', 'mobile-notifications'),
    ],
    'content-mobile': [
        ('mobile-reference-powerbi-latest', 'mobile-reference-powerbi-latest'),
        ('mobile-powerbi-news', 'mobile-powerbi-news'),
        ('mobile-powerbi-learning', 'mobile-powerbi-learning'),
        ('mobile-powerbi-community', 'mobile-powerbi-community'),
        ('mobile-powerbi-cert', 'mobile-powerbi-cert'),
        ('mobile-about', 'mobile-about'),
    ],
}

try:
    font = ImageFont.truetype('arial.ttf', 22)
    small = ImageFont.truetype('arial.ttf', 16)
except Exception:
    font = ImageFont.load_default()
    small = ImageFont.load_default()


def fit(img: Image.Image, width: int, max_height: int = 4200) -> Image.Image:
    ratio = width / img.width
    resized = img.resize((width, max(1, int(img.height * ratio))))
    if resized.height > max_height:
        resized = resized.crop((0, 0, width, max_height))
    return resized


def label_block(text: str, width: int, height: int = 34) -> Image.Image:
    im = Image.new('RGB', (width, height), 'white')
    d = ImageDraw.Draw(im)
    d.text((10, 8), text, fill=(11, 31, 63), font=small)
    return im

for name, group in pairs.items():
    col_w = 520 if 'mobile' not in name else 300
    gutter = 24
    row_gap = 36
    rows = []
    for stream_name, cur_name in group:
        sp = STREAM / f'{stream_name}.png'
        cp = CUR / f'{cur_name}.png'
        if not sp.exists() or not cp.exists():
            print(f'skip missing {sp} {cp}')
            continue
        s = fit(Image.open(sp).convert('RGB'), col_w)
        c = fit(Image.open(cp).convert('RGB'), col_w)
        h = max(s.height, c.height)
        row = Image.new('RGB', (col_w * 2 + gutter, h + 68), (244, 247, 253))
        row.paste(label_block(f'Streamlit original: {stream_name}', col_w), (0, 0))
        row.paste(label_block(f'Svelte current: {cur_name}', col_w), (col_w + gutter, 0))
        row.paste(s, (0, 44))
        row.paste(c, (col_w + gutter, 44))
        rows.append(row)
    total_h = sum(r.height for r in rows) + row_gap * max(0, len(rows) - 1) + 56
    sheet = Image.new('RGB', (col_w * 2 + gutter, total_h), (244, 247, 253))
    d = ImageDraw.Draw(sheet)
    d.text((0, 12), f'FOLIO UI/UX Visual Audit - {name}', fill=(11, 31, 63), font=font)
    y = 56
    for row in rows:
        sheet.paste(row, (0, y))
        y += row.height + row_gap
    out = OUT / f'{name}.png'
    sheet.save(out)
    print(out)