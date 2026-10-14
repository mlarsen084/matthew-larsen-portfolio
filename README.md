# Matthew Larsen — Graphic Designer

A lightweight, single-page portfolio combining campaign design, publications,
video, photography and commercial print work. Plain HTML, CSS and JavaScript;
no framework, package installation or server runtime is needed for hosting.

Preview: https://mlarsen084.github.io/matthew-larsen-portfolio/

## Editing

Edit `content/portfolio.json` for project copy and gallery selections. Image
dimensions and responsive variants are recorded in `content/assets.json`.
Then regenerate the page:

```sh
python3 scripts/build.py
```

Edit `styles.css` for layout and `script.js` for gallery/media interactions.
The generated `index.html` is committed so hosting does not need a build step.

## Local preview

```sh
python3 -m http.server 8764 --bind 127.0.0.1
```

Open http://127.0.0.1:8764/. Relative paths also work under the GitHub Pages
repository prefix and when served at the root of a custom domain.

## Hosting

GitHub Pages publishes the root of `main`; `.nojekyll` bypasses Jekyll.
Pushing an updated `index.html`, stylesheet or asset updates the preview.

For Cloudflare Pages, connect this repository, select `main`, use no build
command, and set the output directory to `.`. Connect a custom domain only
when ready to switch. The existing portfolio and its hosting are separate.

The preview currently has `noindex,follow`. Before launching on the final
domain, remove that robots meta tag from `scripts/build.py`, update the
Open Graph URLs there, and regenerate `index.html`.

## Media

- Responsive WebP images are provided at 480, 960 and 1800 pixels where the
  original size permits. Artwork is enlarged using the largest variant.
- Videos are local MP4 files, compressed with H.264 and AAC, and loaded only
  after a visitor presses play. No video embeds exist on initial page load.
- The Nicola’s Fudge film uses a click-loaded YouTube privacy-enhanced embed.
- Closing the viewer removes the media and stops playback. Escape closes
  the viewer and returns keyboard focus to the item that opened it.
- Publications and the CV are local PDFs. Full pages remain readable and
  gallery images scroll with native browser behaviour if JavaScript is off.

Original work came from the existing portfolio and Matthew’s Adobe Portfolio.
Each image’s source is recorded in `content/assets.json`. Concept work,
mockups and production tests are identified in captions.

`scripts/prepare_assets.py` is a one-time import helper. It requires Pillow
and a path to the original portfolio checkout. The finished site does not
require Pillow. Temporary review images in `.work/` are excluded from Git.
