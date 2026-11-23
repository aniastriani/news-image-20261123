# news-image-20261123

[![make.fun · news-image-20261123](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![rank](https://make.fun/badge/news-image-20261123/aniastriani/news-image-20261123/rank.svg)](https://make.fun/bounty/news-image-20261123/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![reward](https://make.fun/badge/news-image-20261123/aniastriani/news-image-20261123/reward.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)

The World in One Image — Monday 23 November 2026. A newspaper front
page that sums up the day's world news in one picture: COP31 climate
talks collapse with no deal after the EU rejects any text without a
fossil fuel phase-out; oil tankers are struck in and near the Strait
of Hormuz as the war reaches Saudi Arabia and Bahrain; suspected
Ukrainian sea drones hit the Russian corvette Merkury at Benghazi and
the ship capsizes; a Russian drone hits an apartment block in Dymer,
north of Kyiv; BepiColombo enters orbit around Mercury, only the
second mission ever to do so; and rescuers recover 24 bodies from a
candy factory fire in Cikande, Indonesia.

`main.py` draws the whole page with the Python standard library only —
a hand-built 5x7 pixel font stored as rows of five bits, small vector
pictograms, and a PNG writer built by hand. No network, no clock, no
randomness: every run writes the same bytes.

## Run it

```sh
python3 main.py
```

The picture is written to `/output/entry.png`, or to
`$MAKEFUN_OUTPUT_DIR` when that variable is set.

---

<sub>Entry for the [news-image-20261123](https://make.fun/bounty/news-image-20261123) bounty on [make.fun](https://make.fun).</sub>
