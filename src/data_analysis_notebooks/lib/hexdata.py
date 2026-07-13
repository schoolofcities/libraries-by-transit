"""
Helpers for loading the hex demographic grid together with travel-time
isochrones. Used in the DA analysis file, where the same
walk/weekday/weekend/transit-averaged travel times need to be joined onto the same
population-weighted hex grid.
"""
import json
import geopandas as gpd

# Demographic groups, including the total population baseline.
# Used for the citywide-average comparisons
DEMOG_GROUPS = {
    'Total Population':      'pop_total',
    'Visible Minority':      'visible_minority',
    'Low Income':            'low_income',
    'First Gen. Immigrants': 'first_gen_immigrants',
    'Seniors (65+)':         'seniors',
    'Children (0–14)':       'children',
}

# Same groups, excluding Total Population — used wherever hexes are split
# into quintiles/percent-share by group
DEMOG_PCT_VARS = {
    'visible_minority':     'Visible Minority',
    'low_income':           'Low Income',
    'first_gen_immigrants': 'First Gen. Immigrants',
    'seniors':              'Seniors (65+)',
    'children':             'Children (0–14)',
}


def _load_minutes(path):
    with open(path) as f:
        gj = json.load(f)
    return [feat['properties']['minutes'] for feat in gj['features']]


def load_hex_with_times(
    hex_path='hex_with_demographic_counts_fixed.geojson',
    walk_path='isochrones_walk.geojson',
    weekday_path='isochrones_transit_weekday_window.geojson',
    weekend_path='isochrones_transit_weekend_window.geojson',
    pop_only=True,
):
    """
    Load the hex demographic grid and attach travel times from the isochrone files.

    Adds columns: walk, weekday, weekend, transit (mean of weekday/weekend).

    Isochrone features are matched to hexes by position, which assumes both
    were exported in the same hex-grid order (see Section 1). If pop_only is
    True (default), hexes with zero population are dropped, matching every
    downstream stats section.
    """
    hex_demog = gpd.read_file(hex_path)

    walk_mins    = _load_minutes(walk_path)
    weekday_mins = _load_minutes(weekday_path)
    weekend_mins = _load_minutes(weekend_path)

    n = min(len(hex_demog), len(walk_mins), len(weekday_mins), len(weekend_mins))
    if n < len(hex_demog):
        print(f"  WARNING: hex grid ({len(hex_demog)}) and isochrones ({n}) "
              f"don't match in length — truncating to {n}, check export order.")

    hex_demog = hex_demog.iloc[:n].copy()
    hex_demog['walk']    = walk_mins[:n]
    hex_demog['weekday'] = weekday_mins[:n]
    hex_demog['weekend'] = weekend_mins[:n]
    hex_demog['transit'] = (hex_demog['weekday'] + hex_demog['weekend']) / 2

    if pop_only:
        hex_demog = hex_demog[hex_demog['pop_total'] > 0].copy()

    return hex_demog
