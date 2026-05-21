# Spatial Access to Public Libraries in Toronto: A Multimodal Assessment of Coverage and Equity

## Abstract

We measure multi-modal spatial access to public libraries in Toronto using network-based travel time routing and link results to census demographics. Couple sentences of key findings ___....


## 1. Questions

Spatial access to public libraries matters: proximity predicts visits and borrowing (Bhatt, 2010; Park, 2012), but access can vary across travel modes and population groups (Allen, 2019; Donnelly, 2014; Cheng et al., 2021).

We analyze data in City of Toronto, specifically asking two questions:

1. **Coverage:** How does minimum travel time to the nearest library branch vary across Toronto by mode (walk, bike, weekday transit, Saturday transit)?

2. **Equity:** How do those travel times vary across different population groups that often have specific needs for library services and programs?

## 2. Methods

**Data.** TPL branch points (n = ##, retrieved from Toronto Open Data, March 2026). ### metre hexagon grid. 2021 Census Dissemination Area (DA) level attributes from Statistics Canada: population density, immigrants arriving 2016–2021, residents aged 0–14, residents aged 65+, and low-income prevalence, ADD MORE??. OpenStreetMap data (extracted #### 2026) for the street and active-transport network. TTC GTFS feed dated 2026-##-## for transit schedules.

**Network Analysis.** Travel times computed in R with the `r5r` package from the centroid of each cell in a ### metre hex grid covering the City of Toronto boundary. Four scenarios:

- *Walk:* ## km/h, maximum 60 minutes.
- *Bike:* ## km/h, LTS ≤ # only, maximum 60 minutes.
- *Weekday transit:* departure window Tuesday 2026-##-##, ##:00–##:00, maximum walk access/egress ## minutes, maximum 60 minutes.
- *Saturday transit:* departure window Saturday 2026-##-##, ##:00–##:00, maximum walk access/egress ## minutes, maximum 60 minutes.

For each scenario and hexagon, we take the minimum travel time across all branches. These are visualized as isochrone maps. Hexagon values are then assigned to DAs by area-weighted overlay (DAs are typically bigger than hexagons). For each demographic indicator we compute population weighted means, medians, and percentiles.

**Replication.** Inputs are all open; the input data, analysis script, and maps are available at [GitHub URL on acceptance].



## 3. Findings

**Isochrone maps (Figure 1).** Describe key trends

**Demographic maps (Figure 2).** Describe key trends

**Quintile statistics (Table 1/Figure 3).** Describe key trends

**Limitations.** Four caveats apply. First, MAUP: travel times are computed from hex centroids, and results may be sensitive to the choice of grid size and placement — a standard concern with raster-based accessibility analysis (Openshaw, 1984). Second, census vintage: demographic linkages use 2021 Census DAs, the most recent available at the time of writing; population composition in rapidly growing areas may have shifted since. Third, edge effects: by restricting destinations to TPL branches, we ignore libraries in adjacent municipalities (Mississauga, Vaughan, Markham, Pickering) that may be the nearest branch for residents near the city boundary, biasing measured access downward in those areas (Sahar et al., 2017). Fourth, opening hours: travel-time isochrones measure network access, not service access. Departure windows were chosen to fall within typical TPL operating hours on both a weekday and a Saturday, mitigating but not eliminating this concern — but individual branch hours vary and are not accounted for (Allen, 2019).

---

**Figure 1.** Maps showing minimum travel time to nearest library branch: (a) walk, (b) bike, (c) weekday transit, (d) Saturday transit. 

**Figure 2.** Maps showing public library locations relative to (a) population density, (b) 2016–2021 immigrant share, (c) LIM-AT prevalence, (d) share aged 0–14, (e) share aged 65+. (f) etc etc etc.

**Table 1.** Population-weighted mean minimum travel time to nearest TPL branch by mode and demographic quintile, presented as a dumbbell chart (lowest vs. highest quintile; whiskers = within-quintile 25th–75th percentile).




--- 

## References


Allen, J. (2019). Mapping differences in access to public libraries by travel mode and time of day. Library & Information Science Research, 41(1), 11–18. https://doi.org/10.1016/j.lisr.2019.02.001. 

Bhatt, R. (2010). The impact of public library use on reading, television, and academic outcomes. Journal of Urban Economics, 68(2), 148–166. https://doi.org/10.1016/j.jue.2010.03.008

Cheng, W., Wu, J., & Hong, L. (2021). Assessing the spatial accessibility and spatial equity of public libraries' physical locations. Library & Information Science Research, 43(2), 101097. https://doi.org/10.1016/j.lisr.2021.101097

Donnelly, F. P. (2014). The geographic distribution of United States public libraries: An analysis of locations and service areas. Journal of Librarianship and Information Science, 46(2), 110–129. https://doi.org/10.1177/0961000612473099

Openshaw, S. (1984). The Modifiable Areal Unit Problem. Geo Books. 

Park, S. J. (2012). Measuring public library accessibility: A case study using GIS. Library & Information Science Research, 34(1), 13–21. https://doi.org/10.1016/j.lisr.2011.07.007

Sahar, L., Foster, S. L., Cohen-Mansfield, J., & Tannous, M. (2017). Does the edge effect impact on the measure of spatial accessibility to healthcare providers? International Journal of Health Geographics, 16(1), 46. https://doi.org/10.1186/s12942-017-0119-3
