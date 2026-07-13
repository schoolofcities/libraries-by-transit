# Is your local library close enough?

Comparing equity gaps in accessibility to Toronto Public Libraries across the city's equity-seeking groups.

By [Jeff Allen](https://jamaps.github.io/about.html) & [Polina Gorn](https://www.linkedin.com/in/polina-gorn-b2a1b8284/) — July 2026

We measure multi-modal spatial access to Toronto Public Library branches using network-based travel time routing, then link the results to 2021 Census demographics to see whether access is equitable across the city's equity-seeking groups.

## Data sources

To reproduce the analysis from scratch, download:

| Data | Source |
|---|---|
| TPL branch locations | [Toronto Open Data catalogue](https://open.toronto.ca/dataset/library-branch-general-information/)| 
| 2021 Census DA/CT attribute data | [CHASS Canadian Census Analyser](https://datacentre.chass.utoronto.ca/census/) (UofT access required) |
| 2021 Census DA/CT boundary files | [StatCan 2021 Census Boundary Files](https://www12.statcan.gc.ca/census-recensement/2021/geo/sip-pis/boundary-limites/index2021-eng.cfm) |
| Toronto municipal boundary | [Toronto Open Data catalogue](https://open.toronto.ca/catalogue/) — search "regional municipal boundary" | 
| OpenStreetMap street/active-transport network | [OSM extracts for Toronto](https://download.bbbike.org/osm/bbbike/Toronto/) |
| TTC GTFS feed | [Merged GTFS - TTC Routes and Schedules](https://open.toronto.ca/dataset/merged-gtfs-ttc-routes-and-schedules/) | 
