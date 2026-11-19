[![news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/competitions/news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/skipperchen0224/makefun-news-image-20261119/rank.svg)](https://make.fun/competitions/news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/skipperchen0224/makefun-news-image-20261119/reward.svg)](https://make.fun/competitions/news-image-20261119)

# The World Today — 19 November 2026

A newspaper front page that sums up the world's news of Thursday,
19 November 2026, in one 1024×1024 image (`entry.png`).

## The day's stories

- **Lead — Shenzhen:** Trump, Xi and Putin declare peace after the first
  ever U.S.-China-Russia trilateral summit (AP, Reuters, Dawn).
- **Myanmar:** the International Court of Justice finds Myanmar guilty of
  state-backed genocide against the Rohingya, a first for the UN's top
  court (Just Security, Japan Times).
- **Gulf:** Iran widens strikes on Kuwait and Bahrain; three tankers catch
  fire after hitting mines east of the Strait of Hormuz (WSJ, NDTV).
- **Riyadh:** a Houthi missile hits the PIF Tower, the Saudi sovereign
  wealth fund's headquarters (NYT, Japan Times).
- **Ukraine:** Kyiv hits the Kerch Bridge a third time in four days; rail
  traffic halted (AP).
- **Bangladesh:** unrest spreads as the ancestral home of former leader
  Yunus is torched (AFP).
- **Culture & Tech:** GTA VI launches worldwide (NDTV). Also: Voyager 1
  reaches one light-day from Earth (Daily Mirror).

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
# writes out/entry.png (1024x1024 PNG, deterministic bytes)
```

`main.ts` (Node 22, standard library only) copies the pre-drawn
`entry.png` to the output directory. The image itself was drawn with
Pillow by `draw_image.py` (kept in the build notes, not in this repo):
newsprint layout, masthead, lead story, six stories in a 3×2 grid.
Every fact was checked against live reporting on 19 November 2026.
