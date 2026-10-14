"""Render the static portfolio. Python standard library only."""
from html import escape
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / "content/portfolio.json").read_text())
assets = json.loads((ROOT / "content/assets.json").read_text())
used_assets = set()

def e(value):
    return escape(str(value), quote=True)

def img(key, alt, sizes="(max-width: 700px) 88vw, 520px", eager=False):
    used_assets.add(key)
    a = assets[key]
    variants = {v["width"]: v["src"] for v in a["sources"]}
    srcset = ", ".join(f"./{path} {width}w" for width, path in sorted(variants.items()))
    priority = 'fetchpriority="high"' if eager else ''
    return f'<img src="./{a["sources"][1]["src"]}" srcset="{srcset}" sizes="{sizes}" width="{a["width"]}" height="{a["height"]}" alt="{e(alt)}" loading="{"eager" if eager else "lazy"}" decoding="async" {priority}>'

def figure(item, eager=False, sizes=None):
    key, alt, caption = item
    large = './' + assets[key]["sources"][-1]["src"]
    return f'<figure><button class="media-trigger image-trigger" type="button" data-image="{large}" data-alt="{e(alt)}" data-title="{e(caption)}" aria-label="Enlarge: {e(caption)}">{img(key, alt, sizes or "(max-width: 700px) 86vw, 520px", eager)}<span class="enlarge-label" aria-hidden="true">↗</span></button><figcaption>{e(caption)}</figcaption></figure>'

def video(item, sizes="(max-width: 700px) 86vw, 520px"):
    key = item["image"]
    attr = f'data-video="./assets/video/{e(item["video"])}"' if item.get("video") else f'data-youtube="{e(item["youtube"])}"'
    fallback = f'./assets/video/{item["video"]}' if item.get("video") else f'https://www.youtube.com/watch?v={item["youtube"]}'
    return f'<figure class="video-figure"><button class="media-trigger video-trigger" type="button" {attr} data-title="{e(item["title"])}" aria-label="Play: {e(item["title"])}">{img(key, item["title"] + " video still", sizes)}<span class="play-label"><span aria-hidden="true">▶</span> Play video</span></button><figcaption><span>{e(item["title"])}</span><span class="caption-detail">{e(item["caption"])}</span></figcaption><noscript><a href="{e(fallback)}">Watch video ↗</a></noscript></figure>'

def gallery(id, label, items, kind="", videos=None):
    count = len(items) + len(videos or [])
    figures = ''.join(video(x) for x in videos or []) + ''.join(figure(x) for x in items)
    return f'<div class="gallery {kind}"><div class="gallery-bar"><h4 id="{id}-label">{e(label)}</h4><div class="rail-controls" hidden><span class="rail-count" aria-hidden="true">1 / {count}</span><button type="button" data-direction="-1" aria-label="Previous items: {e(label)}" aria-controls="{id}">←</button><button type="button" data-direction="1" aria-label="Next items: {e(label)}" aria-controls="{id}">→</button></div></div><div class="rail" id="{id}" tabindex="0" role="region" aria-labelledby="{id}-label">{figures}</div><p class="swipe-note">Scroll sideways to see more <span aria-hidden="true">→</span></p></div>'

def chapter(number, id, title, description):
    return f'<section class="chapter" id="{id}" aria-labelledby="{id}-title"><div class="chapter-heading"><div><span class="section-number">{number}</span><h2 id="{id}-title">{title}</h2></div><p>{description}</p></div>'

def awards():
    return '''<aside class="awards" aria-labelledby="awards-title"><div class="award-heading"><span class="award-star" aria-hidden="true">✳</span><h4 id="awards-title">2026 Reed Awards</h4><span>Nicola’s Fudge</span></div><div class="award-categories"><p><span>Winner</span>Best International Campaign (National)</p><p><span>Winner</span>Best International Online Video (National)</p><p class="award-finalist"><span>Finalist</span>Best Public Affairs Campaign</p></div><a class="text-link award-source" href="https://www.taxpayers.org.nz/nicolas_fudge" target="_blank" rel="noopener noreferrer">Campaign recognition ↗</a></aside>'''

parts = []
parts.append('''<!doctype html>
<html lang="en-NZ">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Matthew Larsen is a Wellington graphic designer working across campaigns, publications, packaging, video and photography, with seven years of commercial print experience.">
  <meta name="robots" content="noindex,follow">
  <meta name="theme-color" content="#f5f3ed">
  <meta property="og:type" content="website">
  <meta property="og:title" content="Matthew Larsen — Graphic Designer">
  <meta property="og:description" content="Selected design work across print, digital and motion.">
  <meta property="og:image" content="https://mlarsen084.github.io/matthew-larsen-portfolio/assets/share.jpg">
  <meta property="og:url" content="https://mlarsen084.github.io/matthew-larsen-portfolio/">
  <title>Matthew Larsen — Graphic Designer</title>
  <link rel="icon" href="./assets/favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="./styles.css">
  <script src="./script.js" defer></script>
</head>
<body>
<a class="skip-link" href="#work">Skip to selected work</a>
<div class="page">
<header class="masthead"><a href="#top" aria-label="Matthew Larsen, back to top">ML.</a><span>Graphic design / Selected work</span><a href="mailto:mlarsen084@gmail.com">Get in touch ↗</a></header>
<main>
<section class="intro" id="top" aria-labelledby="name">
  <div class="intro-main"><p class="eyebrow">Wellington, New Zealand</p><h1 id="name">Matthew Larsen<span class="name-period">.</span></h1><p class="role">Graphic designer.</p>''')
parts.append(f'<p class="intro-copy">{e(data["intro"])}</p></div>')
parts.append(f'''<div class="intro-aside"><p class="availability"><span aria-hidden="true"></span>Open to roles & projects</p><p>Print, digital & motion. <br>Willing to relocate.</p><div class="intro-links"><a href="mailto:{e(data['email'])}">Email me ↗</a><a href="./assets/docs/matthew-larsen-cv.pdf" target="_blank" rel="noopener">Download CV ↓</a><a href="{e(data['linkedin'])}" target="_blank" rel="noopener noreferrer">LinkedIn ↗</a></div><p class="quiet-note">A selection of things I’ve made,<br>and how I made them.</p></div></section>
<nav class="contents" aria-label="Portfolio contents"><span class="contents-label">Contents</span><ol>''')
for num, id, label in [('01','work','Campaigns'),('02','publications','Publications'),('03','digital','Video & digital'),('04','photography','Photography'),('05','print','Print & production'),('06','about','About & contact')]:
    parts.append(f'<li><a href="#{id}"><span>{num}</span>{e(label)}</a></li>')
parts.append('</ol></nav>')
parts.append(chapter('01', 'work', 'Campaigns', 'Visual identities carried through packaging, print, signage and moving images.'))
for idx, project in enumerate(data['campaigns']):
    p = project
    parts.append(f'<article class="project" id="{p["id"]}" aria-labelledby="{p["id"]}-title"><div class="project-heading"><div><p class="project-meta">{e(p["year"])} · New Zealand Taxpayers’ Union</p><h3 id="{p["id"]}-title">{e(p["title"])}</h3><p class="disciplines">{e(p["type"])}</p></div><div class="project-copy">')
    parts.extend(f'<p>{e(text)}</p>' for text in p['description'])
    if p.get('link'):
        parts.append(f'<a class="text-link" href="{e(p["link"])}" target="_blank" rel="noopener noreferrer">{e(p["link_label"])} ↗</a>')
    parts.append('</div></div>')
    if p['id'] == 'nicolas-fudge': parts.append(awards())
    if p.get('leads'):
        parts.append('<div class="image-pair">' + ''.join(figure(item, eager=(idx == 0 and i == 0)) for i, item in enumerate(p['leads'])) + '</div>')
        parts.append(gallery(p['id']+'-details', 'A closer look', p['gallery'], videos=[p['film']]))
    else:
        parts.append(gallery('wcal-videos', 'The video series', [], 'landscape-gallery', p['videos']))
        parts.append(gallery('wcal-thumbnails', 'The thumbnail system', p['gallery'], 'thumbnail-gallery'))
    parts.append('</article>')
parts.append('</section>')
parts.append(chapter('02', 'publications', 'Publications', 'Page layout, typography and print-ready artwork. Plus a little motion.'))
for p in data['publications']:
    parts.append(f'<article class="project publication" aria-labelledby="{p["id"]}-title"><div class="publication-intro"><div class="publication-cover">{video({"image":p["cover"],"title":p["title"]+" — Blender animation","caption":"3D motion from the finished artwork", "video":p["id"]+".mp4"})}</div><div class="publication-copy"><p class="project-meta">InDesign / Blender · {p["pages"]} pages</p><h3 id="{p["id"]}-title">{e(p["title"])}</h3><p>{e(p["description"])}</p><a class="text-link" href="./assets/docs/{p["id"]}.pdf" target="_blank" rel="noopener">Open the full publication ↗</a></div></div>')
    parts.append(gallery(p['id']+'-pages', 'Inside the publication', p['gallery'], 'page-gallery'))
    parts.append('</article>')
parts.append('</section>')
parts.append(chapter('03','digital','Video & digital','Short-form edits, explainers and graphics made for everyday communication.'))
parts.append('<div class="section-copy"><p>At the Taxpayers’ Union I work across daily campaign and social content, often producing 15–35 graphics and videos a day. Reusable layouts help keep the work consistent when the turnaround is short.</p></div>')
parts.append(gallery('motion-work', 'Selected motion & edits', [], 'motion-gallery', data['motion']))
parts.append(gallery('social-work', 'Social graphics & posters', data['social'], 'social-gallery'))
parts.append('</section>')
parts.append(chapter('04','photography','Photography','Events, people and places. Photographed and edited by me.'))
parts.append(gallery('photo-work','Selected photographs', data['photography'], 'photo-gallery'))
parts.append('</section>')
parts.append(chapter('05','print','Print & production','Seven years in a print shop taught me to think beyond the screen.'))
for p in data['print']:
    parts.append(f'<article class="project print-project" aria-labelledby="{p["id"]}-title"><div class="project-heading"><div><p class="project-meta">McDowall Print / Selected work</p><h3 id="{p["id"]}-title">{e(p["title"])}</h3><p class="disciplines">{e(p["type"])}</p></div><div class="project-copy"><p>{e(p["description"])}</p></div></div>')
    parts.append(gallery(p['id']+'-gallery','Selected applications',p['gallery'],'print-gallery'))
    parts.append('</article>')
parts.append('''<article class="production project" aria-labelledby="production-title"><div class="project-heading"><div><p class="project-meta">2018–2024 · McDowall Print</p><h3 id="production-title">From artwork<br>to finished print.</h3><p class="disciplines">Design / Digital print / Pre-press / Finishing</p></div><div class="project-copy"><p>I spent seven years working across design, digital printing, pre-press and finishing. That included checking files, preparing dielines, managing colour, proofing and working with clients to get jobs ready for production.</p><p>I built a variable-data workflow that generated and printed more than 100,000 unique cards, using Code 128 barcodes and QR codes for a repeat client.</p></div></div><div class="production-notes"><div><h4>Artwork & pre-press</h4><p>Print-ready files, bleed, dielines, image preparation, CMYK and spot colour, proofing and production handover.</p></div><div><h4>Print & finishing</h4><p>Digital print, labels and wide format. Experience with Xerox, Fujifilm, Epson SurePress, Fiery RIP, binding, laminating and guillotines.</p></div></div>''')
parts.append(gallery('print-shop','On the print-shop floor',data['production'],'shop-gallery'))
parts.append('</article></section>')
parts.append(chapter('06','about','A little about me.','A designer with experience from the first brief through to the finished piece.'))
parts.append('''<div class="about-layout"><div class="about-copy"><p>I’m based in Wellington and work across graphic design, video, photography and print. My background combines hands-on production with the pace of a national communications team.</p><p>I’m looking for a role where I can put that range to work, keep learning and make good things with other people.</p><a class="text-link" href="./assets/docs/matthew-larsen-cv.pdf" target="_blank" rel="noopener">Download my CV ↓</a></div><div class="experience-list"><article><p class="project-meta">2025–present</p><h3>New Zealand Taxpayers’ Union</h3><p>Senior Graphic Designer</p></article><article><p class="project-meta">2018–2024</p><h3>McDowall Print</h3><p>Graphic Designer, Digital Print & Pre-Press</p></article><article><p class="project-meta">Qualifications</p><p>NZ Diploma in Digital Media and Design, Level 5<br><span class="caption-detail">Yoobee Colleges · 2023</span></p><p>NZ Certificate in Print Digital Printing, Level 4<br><span class="caption-detail">Competenz / Te Pūkenga · 2018–2022</span></p></article></div></div><div class="tools"><h3>Tools I work with</h3><p>InDesign, Illustrator, Photoshop, Premiere Pro, After Effects, Lightroom, Blender and Figma. AI tools are part of some image and video workflows, with editing and final production handled by me.</p></div>''')
parts.append(f'''<div class="contact" id="contact"><p class="eyebrow">Have a role or a project in mind?</p><h2>Let’s talk.</h2><a class="contact-email" href="mailto:{e(data['email'])}">{e(data['email'])} <span aria-hidden="true">↗</span></a><div class="contact-links"><a href="./assets/docs/matthew-larsen-cv.pdf" target="_blank" rel="noopener">Download CV ↓</a><a href="{e(data['linkedin'])}" target="_blank" rel="noopener noreferrer">LinkedIn ↗</a><span>Wellington, NZ · Willing to relocate</span></div></div></section></main><footer><p>© 2026 Matthew Larsen</p><a href="#top">Back to top ↑</a></footer></div>
<dialog class="media-dialog" aria-labelledby="dialog-title"><div class="dialog-header"><h2 id="dialog-title">Selected work</h2><button type="button" class="dialog-close" aria-label="Close media">Close <span aria-hidden="true">×</span></button></div><div class="dialog-content"></div><div class="dialog-footer"><p class="dialog-caption"></p><div class="image-controls" hidden><button type="button" class="image-prev" aria-label="Previous image">←</button><span class="image-count"></span><button type="button" class="image-next" aria-label="Next image">→</button></div></div></dialog>
</body></html>''')
(ROOT / 'index.html').write_text('\n'.join(parts)+'\n')
(ROOT / '.work/used-assets.json').write_text(json.dumps(sorted(used_assets), indent=2)+'\n') if (ROOT / '.work').exists() else None
print(f'Rendered index.html with {len(used_assets)} selected images. No JavaScript required to read the portfolio.')
