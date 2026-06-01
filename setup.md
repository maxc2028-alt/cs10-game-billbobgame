# Neighborhood Cleanup: South Block

**Group Members:** Ethan and Max

## What this is

Neighborhood Cleanup: South Block is a 2D Arcade game about restoring a neighborhood, helping people connect, and turning abandoned spaces into something hopeful.

## Download the game

These links are meant for everyone, even if they do not have Python installed. Once a GitHub Release is published, the links below will download the latest public build directly:

- [Download for Windows](https://github.com/maxc2028-alt/cs10-game-billbobgame/releases/latest/download/NeighborhoodCleanup-Windows.exe)
- [Download for Mac](https://github.com/maxc2028-alt/cs10-game-billbobgame/releases/latest/download/NeighborhoodCleanup-Mac.dmg)

## How to play from source

If you want to run the game from the code instead of the downloadable build:

1. Install Python 3.11 or newer.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start the game:

```bash
python game-max.py
```

## For maintainers

Release assets are built automatically with GitHub Actions when a GitHub Release is published. See [`.github/workflows/release.yml`](.github/workflows/release.yml) and [`build_release.py`](build_release.py).
