from pathlib import Path
from PIL import Image, ImageStat

ROOT = Path('artifacts/ui-parity')
print('# contact sheets')
for p in sorted((ROOT / 'design-audit').glob('*.png')):
    im = Image.open(p)
    print(p.as_posix(), im.size)

names = [
    'desktop-home','desktop-detail-known','desktop-submit','desktop-my-page','desktop-notifications',
    'desktop-reference-powerbi-latest','desktop-powerbi-news','desktop-powerbi-learning','desktop-powerbi-cert',
    'desktop-about','desktop-policy-privacy','mobile-home','mobile-detail-known','mobile-submit','mobile-my-page',
    'mobile-notifications','mobile-reference-powerbi-latest','mobile-powerbi-news','mobile-about'
]
print('\n# dimensions and average color')
for folder in ['streamlit','svelte-current']:
    print('##', folder)
    for name in names:
        p = ROOT / folder / f'{name}.png'
        if not p.exists():
            continue
        im = Image.open(p).convert('RGB')
        avg = tuple(round(v) for v in ImageStat.Stat(im.resize((1, 1))).mean)
        print(name, im.size, avg)

print('\n# first viewport whitespace and dominant lightness')
for folder in ['streamlit','svelte-current']:
    print('##', folder)
    for name in names:
        p = ROOT / folder / f'{name}.png'
        if not p.exists():
            continue
        im = Image.open(p).convert('RGB')
        crop = im.crop((0, 0, im.width, min(im.height, 900)))
        pixels = list(crop.resize((100, 100)).getdata())
        very_light = sum(1 for r,g,b in pixels if r > 245 and g > 245 and b > 245) / len(pixels)
        navy_dark = sum(1 for r,g,b in pixels if b > r and b > g and r < 60 and g < 80) / len(pixels)
        print(name, 'very_light', round(very_light, 3), 'navy_dark', round(navy_dark, 3))