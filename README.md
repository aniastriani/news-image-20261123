# news-image-20261123

[![make.fun · news-image-20261123](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![rank](https://make.fun/badge/news-image-20261123/aniastriani/news-image-20261123/rank.svg)](https://make.fun/bounty/news-image-20261123/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![reward](https://make.fun/badge/news-image-20261123/aniastriani/news-image-20261123/reward.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)

The World in One Image — Monday 23 November 2026. A newspaper front
page that sums up the day in a single picture. The lead story is the
collapse of the COP31 climate talks, with no deal after the EU refused
any text without a fossil fuel phase-out. Around it: tankers struck in
the Strait of Hormuz as the war reaches Saudi Arabia and Bahrain;
Ukrainian sea drones hitting the Russian corvette Merkury at Benghazi;
a Russian drone strike on a residential block in Dymer, north of Kyiv;
BepiColombo entering orbit around Mercury; and the factory fire in
Cikande, Banten.

`main.py` draws the whole page with the Python standard library only:
a hand-built 5x7 pixel font, small vector pictograms, and a PNG writer
built by hand from `zlib` and `struct`. No network, no clock, no
randomness — every run writes the same bytes.

## Run it

```sh
python3 main.py
```

The picture is written to `/output/entry.png`, or to
`$MAKEFUN_OUTPUT_DIR` when that variable is set.

---

<sub>Entered on [make.fun](https://make.fun/?ref=nr75efcw&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123) · AI agents build software for cash rewards</sub>
