# Analysis

Notebooks behind the library proximity map and study. Run them in order:

1. **`isochrone_code.ipynb`**: builds a 200 m hex grid and uses r5py to compute travel times to the nearest library by walking, and by walking + transit (weekday and weekend). Also exports the library points and TTC rapid transit lines for the web map.
2. **`DA_data_analysis.ipynb`**: aggregates 2021 Census DA demographics to census tracts and onto the hex grid, then calculates population-weighted travel times and equity gaps by group. Exports the static choropleth maps, summary tables and the dumbbell chart data.

`lib/` has shared helpers for the second notebook: loading census data (`census.py`), joining travel times to the hex grid (`hexdata.py`) and population-weighted statistics (`stats.py`).

## Data sources

To reproduce the analysis from scratch, download:

| Data | Source |
|---|---|
| TPL branch locations | [Toronto Open Data catalogue](https://open.toronto.ca/dataset/library-branch-general-information/) |
| 2021 Census DA/CT attribute data | [CHASS Canadian Census Analyser](https://datacentre.chass.utoronto.ca/census/) (UofT access required) |
| 2021 Census DA/CT boundary files | [StatCan 2021 Census Boundary Files](https://www12.statcan.gc.ca/census-recensement/2021/geo/sip-pis/boundary-limites/index2021-eng.cfm) |
| Toronto municipal boundary | [Toronto Open Data catalogue](https://open.toronto.ca/catalogue/) — search "regional municipal boundary" |
| OpenStreetMap street/active-transport network | [OSM extracts for Toronto](https://download.bbbike.org/osm/bbbike/Toronto/) |
| TTC GTFS feed | [Merged GTFS - TTC Routes and Schedules](https://open.toronto.ca/dataset/merged-gtfs-ttc-routes-and-schedules/) |
