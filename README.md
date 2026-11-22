# The World Today — Sunday, 22 November 2026

Entry for the make.fun competition "Sum up the world news in one image"
(news-image-20261122): the day's world news on a single 1024x1024 page.

Files:

- `entry.png` — the entry image, produced locally by `render.py`.
- `main.py` — graded entrypoint; standard library only. It copies
  `entry.png` to the folder given by `MAKEFUN_OUTPUT_DIR`.
- `render.py` — local build tool that draws `entry.png` from
  `sources.json` and the photographs in `thumbs/`.
- `sources.json` — the stories used. Each one was reported by at least
  two independent outlets that day; the outlets are named in the image
  footer.

The page carries headlines and reported figures only, no article text.
