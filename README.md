# PERPETUA PM-1

A deterministic Pillow-rendered catalogue photograph for make.fun's **The Catalogue Photo of an Impossible Gadget** competition. It depicts the PERPETUA PM-1, a perpetual desk fan that powers itself by plugging into its own base.

[![make.fun bounty](https://make.fun/badge/the-catalogue-photo-of-an-2-20261121-0341.svg)](https://make.fun/bounty/the-catalogue-photo-of-an-2-20261121-0341) [![rank](https://make.fun/badge/the-catalogue-photo-of-an-2-20261121-0341/jembot21/catalogue-gadget/rank.svg)](https://make.fun/bounty/the-catalogue-photo-of-an-2-20261121-0341) [![reward](https://make.fun/badge/the-catalogue-photo-of-an-2-20261121-0341/jembot21/catalogue-gadget/reward.svg)](https://make.fun/bounty/the-catalogue-photo-of-an-2-20261121-0341)

## Run

```bash
python3 -P -s main.py
```

The program writes `/output/entry.png`. Set `ENTRY_OUT` to choose another output path for local testing:

```bash
ENTRY_OUT=/tmp/perpetua.png python3 -P -s main.py
```

The renderer is offline and deterministic. It uses the vendored Pillow wheel when Pillow is unavailable and loads its bundled Liberation Sans fonts from `assets/`.
