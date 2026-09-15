# Zac Veen

## Background

Zac Veen is a Colorado Rockies outfielder and former first-round pick who won the 2025 spring training MVP award, 
but his big-league debut was rough — 12 games, a .424 OPS, and a 37.8% strikeout rate in 2025. Over the 2025–26 offseason 
he reworked his body, his mentality and his swing: a wider, more athletic stance, more tilt in the swing path, and a noticeably steeper attack 
angle. I ask  whether those mechanical changes are showing up in the numbers, and whether they're enough to 
outweigh a strikeout problem that's still getting worse.

> **Full Article -** https://blakestreetbanter.com/2026/09/10/the-case-for-zac-veen/


## What the data shows

The swing changes are real and measurable. Attack angle jumped from 4.7° to 12.4° year-over-year on fastballs 
specifically, it flipped from negative to +3.7°, a meaningful shift toward an uppercut geared for power. Point 
of contact moved from 24.3 inches to 35.1 inches in front of his center of mass, a longer, more extended swing 
that's associated with higher home run rates. The results followed: OPS nearly doubled, from .424 to .847, with 
two home runs in his first two games back.

But plate discipline didn't improve alongside it. Ff anything, it got worse. Strikeout rate rose to 38.6%, and 
his swing rate against breaking balls jumped from 44.0% to 63.6%, including a sharp increase in chasing breaking 
balls out of the zone (26.7% → 52.4%). Whiff rate stayed roughly flat overall but climbed specifically on fastballs 
and off-speed pitches. As the article puts it, a 38.6% strikeout rate "could end careers" the swing is doing what 
it's supposed to, but the pitch recognition hasn't caught up yet.

## Data

| Source | Method | File |
|---|---|---|
| Statcast pitch-by-pitch | [pybaseball](https://github.com/jldbc/pybaseball) | `sample_data/zac_veen_2025_2026.csv` |
| Bat tracking | Baseball Savant [Search](https://baseballsavant.mlb.com/statcast_search) export | `sample_data/zac_veen_bat_tracking.csv` |

## Structure

```
sample_data/     raw CSVs pulled from Statcast / Baseball Savant
notebooks/       exploratory analysis notebook
src/             reusable data collection and analysis scripts
```

- `src/veen_statcast_data_collect.py` — pulls Statcast data via pybaseball and saves it to `sample_data/`
- `src/bat_tracking_analysis.py` — swing metrics by year and pitch category (attack angle, contact point, top-decile swings), plus point-of-contact and attack-angle visualizations
- `src/statcast_analysis.py` — swing%, whiff%, and zone-based plate discipline breakdowns by year and pitch category
- `notebooks/zac_veen_notebook.ipynb` — full walkthrough, mirroring the two scripts above with inline commentary

## Running this locally

```bash
pip install pandas numpy matplotlib pybaseball jupyter
```

Pull fresh data:
```bash
python src/veen_statcast_data_collect.py
```

Run the analysis:
```bash
python src/bat_tracking_analysis.py
python src/statcast_analysis.py
```

Or open `notebooks/zac_veen_notebook.ipynb` for the full interactive walkthrough.
