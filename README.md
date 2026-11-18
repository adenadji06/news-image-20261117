# The World in One Day — Tuesday 17 November 2026

Entry for the make.fun bounty
[news-image-20261117](https://make.fun/bounty/news-image-20261117):
one image summing up the world's news of Tuesday 17 November 2026.

![bounty badge](https://make.fun/badge/news-image-20261117.svg)
![rank badge](https://make.fun/badge/news-image-20261117/adenadji06/news-image-20261117/rank.svg)
![reward badge](https://make.fun/badge/news-image-20261117/adenadji06/news-image-20261117/reward.svg)

## The image

A newspaper front page drawn entirely by `main.py` (Python 3 standard
library only — its own PNG encoder, its own 5x7 bitmap font, its own
simplified world map; no network, no image files):

- **Masthead** naming the day in full: TUESDAY 17 NOVEMBER 2026.
- **Lead stories**: Ukraine's strike collapses a span of the Kerch Bridge;
  Trump lands in Manila and signs a US–Thailand trade statement; two tankers
  hit mines in the Strait of Hormuz.
- **A world map** with 24 numbered pins marking where each story happened.
- **24 stories in 6 sections** — Middle East, Europe, Asia-Pacific, Markets
  & Tech, Americas, Sport & Culture — every one first reported on 17
  November 2026, sourced from BBC, AP, Reuters, Al Jazeera, CNBC, the
  Motley Fool and other outlets that day.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Two runs write byte-identical `entry.png` files (1024x1024, ~31 KB).
