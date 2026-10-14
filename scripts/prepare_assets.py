"""Prepare portfolio assets once; publishing the site needs no dependencies."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from io import BytesIO
import json
from pathlib import Path
import shutil
from urllib.request import Request, urlopen
from PIL import Image, ImageOps, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("source", type=Path)
args = parser.parse_args()
SOURCE = args.source / "public"
OUT = ROOT / "assets/images"
OUT.mkdir(parents=True, exist_ok=True)
REVIEW = ROOT / ".work"
REVIEW.mkdir(exist_ok=True)
catalog = {}

def image(source, name, origin):
    with Image.open(source) as im:
        im = ImageOps.exif_transpose(im).convert("RGB")
        w, h = im.size
        paths = []
        for target in [480, 960, 1800]:
            width = min(target, w)
            path = OUT / f"{name}-{target}.webp"
            resize = im.resize((width, round(h * width / w)), Image.Resampling.LANCZOS)
            resize.save(path, "WEBP", quality=85, method=6)
            paths.append({"src": str(path.relative_to(ROOT)), "width": width})
        catalog[name] = {"width": w, "height": h, "sources": paths, "origin": origin}

local = []
for project in ["nicolas-fudge", "cap-rates-now"]:
    folder = SOURCE / "media/cases" / project
    for f in sorted(folder.glob("*.jpg")):
        if f.stem == "cover" or f.stem.startswith("gallery") or "overview-poster" in f.stem:
            local.append((f, f"{project}-{f.stem}", f"current-portfolio/media/cases/{project}/{f.name}"))
for f in sorted((SOURCE / "media/cases/we-cant-afford-labour").glob("*.webp")):
    local.append((f, f"wcal-{f.stem}", f"current-portfolio/media/cases/we-cant-afford-labour/{f.name}"))
photos = json.loads((args.source / "content/photography.json").read_text())
for p in photos:
    f = SOURCE / p["src"].lstrip("/")
    local.append((f, f"photo-{f.stem}", f"current-portfolio{p['src']}"))
for name in ["bureaucrats-paper-style", "shrinking-economy", "ara-rates-grab-reel", "tax-vs-levy", "declan-vertical-cut"]:
    f = SOURCE / f"media/reel/{name}-poster.jpg"
    local.append((f, f"video-{name}", f"current-portfolio/media/reel/{f.name}"))
for slug in ["taxpayer-manifesto", "little-red-book"]:
    f = SOURCE / f"media/publications/{slug}-poster.jpg"
    local.append((f, f"{slug}-motion", f"current-portfolio/media/publications/{f.name}"))
for name in ["photo-award-detail", "about-camera-kit", "about-matthew-group"]:
    f = SOURCE / f"media/photography/{name}.webp"
    if f.exists(): local.append((f, name, f"current-portfolio/media/photography/{f.name}"))
local.append((SOURCE / "media/reed/spinning-reed-award-poster.jpg", "reed-award", "current-portfolio/media/reed/spinning-reed-award-poster.jpg"))
for name in ["wall-01", "wall-17", "wall-14", "wall-19", "wall-focus-04", "wall-focus-01"]:
    f = SOURCE / f"media/wall/{name}.jpg"
    local.append((f, f"social-{name}", f"current-portfolio/media/wall/{f.name}"))
for f in sorted(REVIEW.glob("manifesto-*.png")) + sorted(REVIEW.glob("red-book-*.png")):
    local.append((f, f.stem, "current-portfolio/docs/publications/"))
with ThreadPoolExecutor(max_workers=4) as pool:
    list(pool.map(lambda item: image(*item), local))

class PortfolioImages(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "img" and ("project-module-image" in a.get("class", "") or "grid__item-image" in a.get("class", "")):
            url = a.get("data-src") or a.get("src", "")
            if url.startswith("https://cdn.myportfolio.com") and url not in self.urls:
                self.urls.append(url)

projects = {"branding-mcdowall-print": 5, "bowmont-meats": 4, "beer-series": 4,
            "card-pack-dieline-test": 4, "menus": 3, "ilt-booklet": 3,
            "garden-tags": 3, "printing-workplace-equipment-gallery": 5,
            "otatara-mtb-hazy-pale-ale-label-mockup": 2, "labels-branding": 3}
downloads = []
for slug, limit in projects.items():
    url = f"https://mlarsen084.myportfolio.com/{slug}"
    html = urlopen(Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=30).read().decode()
    p = PortfolioImages()
    p.feed(html)
    print(slug, len(p.urls), "project images")
    for i, asset_url in enumerate(p.urls[:limit], 1):
        downloads.append((asset_url, f"{slug}-{i:02d}", url))

def download(item):
    url, name, origin = item
    data = urlopen(Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=60).read()
    image(BytesIO(data), name, origin)
with ThreadPoolExecutor(max_workers=4) as pool:
    list(pool.map(download, downloads))

for slug, dest in [("Matthew_Larsen_Graphic_Designer_CV_Styled_A4.pdf", "matthew-larsen-cv.pdf"),
                   ("publications/taxpayer-manifesto.pdf", "taxpayer-manifesto.pdf"),
                   ("publications/little-red-book.pdf", "little-red-book.pdf")]:
    shutil.copyfile(SOURCE / "docs" / slug, ROOT / "assets/docs" / dest)
(ROOT / "content/assets.json").write_text(json.dumps(catalog, indent=2) + "\n")

# Contact sheets are review aids only, and are excluded from Git.
groups = {
    "campaigns": [k for k in catalog if k.startswith(("nicolas-fudge", "cap-rates-now", "wcal-", "reed-award", "photo-award"))],
    "print": [k for k in catalog if any(k.startswith(s) for s in projects)],
    "publications": [k for k in catalog if k.startswith(("manifesto-", "red-book-", "taxpayer-manifesto", "little-red-book"))],
    "photos": [k for k in catalog if k.startswith("photo-") and k != "photo-award-detail"],
}
for group, names in groups.items():
    cols = 4
    sheet = Image.new("RGB", (cols * 320, ((len(names)+cols-1)//cols) * 240), "#efeee8")
    draw = ImageDraw.Draw(sheet)
    for idx, name in enumerate(names):
        im = Image.open(ROOT / catalog[name]["sources"][1]["src"])
        im.thumbnail((304, 204))
        x, y = (idx % cols)*320, (idx // cols)*240
        sheet.paste(im, (x+(320-im.width)//2, y+8+(204-im.height)//2))
        draw.text((x+8, y+216), name[:43], fill="black")
    sheet.save(REVIEW / f"review-{group}.jpg", quality=88)
print(f"Prepared {len(catalog)} image sets")
