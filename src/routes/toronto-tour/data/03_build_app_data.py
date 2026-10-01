"""
Build the data file for the tour page from the routed itineraries.

Adds what the step cards need on top of the routed segments: boarding and
alighting stop names (nearest GTFS stop served by that line), line names and
colours, TTC and TPL links, and groups segments into scroll steps. Walks under
WALK_FOLD_MIN that lead to a ride (to the first stop, or a transfer) are folded
into that ride's step.

Inputs:  transit_routes_edited.geojson (02b_manual_fixes.R), tour_stops.csv, tpl_branch_info.csv
         (TPL Branch General Information, Toronto Open Data), r5/ttc_gtfs.zip
Output:  tour_app.json

Usage: python3 03_build_app_data.py
"""

import json
import re
import zipfile
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

HERE = Path(__file__).parent
OUT = HERE / "tour_app.json"

# Walks shorter than this that lead to a ride (from a library to the first stop,
# or a transfer) are folded into that ride's step instead of getting their own.
WALK_FOLD_MIN = 3
STOP_SNAP_M = 80
COORD_DECIMALS = 5
CRS_M = 32617

# Brand red for buses and streetcars; subway and LRT lines use the TTC's official
# line colours (from ttc.ca's stylesheet; the GTFS route_color values differ),
# except Line 6, darkened from #969594 so it reads on the light basemap.
BUS_COLOR = "#DC4633"
LINE_COLORS = {"1": "#F8C300", "2": "#00923F", "4": "#A21A68", "5": "#EB8738", "6": "#6E6E6E"}

# One colour per tour on the overview map (School of Cities brand palette).
TOUR_COLORS = ["#1E3765", "#007FA3", "#6D247A", "#AB1368", "#0D534D",
               "#00A189", "#DC4633", "#EBA00F", "#6FC7EA", "#8DBF2E"]


def clean_branch_name(name):
    return re.sub(r"\s*\(formerly?.*?\)\s*|\s*\(formely.*?\)\s*", "", str(name)).strip()


def clean_stop_name(name):
    return re.sub(r"\s*-?\s*(\w+bound|LRT) Platform\b.*$", "", name).strip()


def load_gtfs():
    z = zipfile.ZipFile(HERE / "r5" / "ttc_gtfs.zip")
    routes = pd.read_csv(z.open("routes.txt"), dtype=str)
    stops = pd.read_csv(z.open("stops.txt"), dtype=str)
    trips = pd.read_csv(z.open("trips.txt"), usecols=["route_id", "trip_id"], dtype=str)
    stop_times = pd.read_csv(z.open("stop_times.txt"), usecols=["trip_id", "stop_id"], dtype=str)

    route_stops = (stop_times.drop_duplicates().merge(trips, on="trip_id")
                   [["route_id", "stop_id"]].drop_duplicates()
                   .merge(routes[["route_id", "route_short_name"]], on="route_id"))
    stops = gpd.GeoDataFrame(
        stops, geometry=gpd.points_from_xy(stops.stop_lon.astype(float), stops.stop_lat.astype(float)),
        crs=4326).to_crs(CRS_M)
    route_stops = stops[["stop_id", "stop_name", "geometry"]].merge(route_stops, on="stop_id")
    line_names = dict(zip(routes.route_short_name, routes.route_long_name))
    return route_stops, line_names


def nearest_stop_name(route_stops, line, point_m):
    cand = route_stops[route_stops.route_short_name == line]
    if cand.empty:
        return None
    d = cand.distance(point_m)
    if d.min() > STOP_SNAP_M:
        return None
    return clean_stop_name(cand.loc[d.idxmin(), "stop_name"])


def line_label(line, line_names):
    name = line_names.get(line, "")
    return name if name.startswith("Line ") else f"{line} {name}".strip()


def bbox(coords):
    xs = [c[0] for c in coords]
    ys = [c[1] for c in coords]
    return [round(min(xs), COORD_DECIMALS), round(min(ys), COORD_DECIMALS),
            round(max(xs), COORD_DECIMALS), round(max(ys), COORD_DECIMALS)]


def main():
    segs = gpd.read_file(HERE / "transit_routes_edited.geojson")
    segs_m = segs.to_crs(CRS_M)
    stops = pd.read_csv(HERE / "tour_stops.csv")
    tpl = pd.read_csv(HERE / "tpl_branch_info.csv")
    route_stops, line_names = load_gtfs()

    # Libraries: join TPL info by exact coordinates (libraries.geojson came from TPL data).
    tpl_key = {(round(r.Long, 5), round(r.Lat, 5)): r for r in tpl.itertuples()}
    libs = {}
    for s in stops.itertuples():
        t = tpl_key[(round(s.lon, 5), round(s.lat, 5))]
        libs[(s.route, s.stop)] = {
            "n": int(s.stop),
            "name": clean_branch_name(t.BranchName),
            "address": s.address.replace(", Toronto, ON", "").split(", M")[0],
            # The Open Data file has a typo in one branch URL (tpl.ca.ca).
            "url": t.Website.replace("tpl.ca.ca", "tpl.ca"),
            "lon": round(s.lon, COORD_DECIMALS),
            "lat": round(s.lat, COORD_DECIMALS),
        }

    tours = []
    for r, g in segs.groupby("route"):
        g = g.sort_values("segment")
        gm = segs_m.loc[g.index]

        segments = []
        for (i, row), geom_m in zip(g.iterrows(), gm.geometry):
            coords = [[round(x, COORD_DECIMALS), round(y, COORD_DECIMALS)]
                      for x, y in row.geometry.coords]
            seg = {
                "id": int(row.segment),
                "leg": int(row.leg),
                "mode": row["mode"],
                "minutes": max(1, round(row.duration_min)),
                "meters": int(row.distance_m),
                "coords": coords,
            }
            if row["mode"] != "WALK":
                line = row.route_short_name
                seg.update({
                    "line": line,
                    "line_name": line_label(line, line_names),
                    "color": LINE_COLORS.get(line, BUS_COLOR),
                    "url": f"https://www.ttc.ca/routes-and-schedules/{line}/0",
                    "from_stop": nearest_stop_name(route_stops, line, Point(geom_m.coords[0])),
                    "to_stop": nearest_stop_name(route_stops, line, Point(geom_m.coords[-1])),
                })
            segments.append(seg)

        # Steps: start library, then per leg: rides/walks, then the arrival library.
        steps = [{"kind": "library", "library": 1, "segs": [], "first": True}]
        for leg, legsegs in pd.Series(segments).groupby([s["leg"] for s in segments]):
            legsegs = list(legsegs)
            pending_walk = None
            for k, s in enumerate(legsegs):
                is_transfer = (s["mode"] == "WALK" and 0 < k < len(legsegs) - 1)
                leads_to_ride = (s["mode"] == "WALK" and k < len(legsegs) - 1)
                if leads_to_ride and s["minutes"] < WALK_FOLD_MIN:
                    pending_walk = (s, is_transfer)
                    continue
                step = {"kind": "walk" if s["mode"] == "WALK" else "ride", "segs": [s["id"]]}
                if step["kind"] == "walk":
                    nxt = legsegs[k + 1] if k + 1 < len(legsegs) else None
                    step["to"] = (nxt["from_stop"] if nxt else None) or libs[(r, leg + 1)]["name"]
                    step["to_library"] = nxt is None
                    step["transfer"] = is_transfer
                if pending_walk:
                    walk, was_transfer = pending_walk
                    step["segs"].insert(0, walk["id"])
                    step["transfer"] = was_transfer
                    pending_walk = None
                steps.append(step)
            steps.append({"kind": "library", "library": leg + 1, "segs": []})

        by_id = {s["id"]: s for s in segments}
        for st in steps:
            pts = [c for sid in st["segs"] for c in by_id[sid]["coords"]]
            if st["kind"] == "library":
                lib = libs[(r, st["library"])]
                pts = [[lib["lon"], lib["lat"]]]
            st["bbox"] = bbox(pts)

        tour_libs = [libs[(r, n)] for n in range(1, 11)]
        all_coords = [c for s in segments for c in s["coords"]]
        tours.append({
            "id": int(r),
            "title": f"{tour_libs[0]['name']} to {tour_libs[-1]['name']}",
            "color": TOUR_COLORS[int(r) - 1],
            "bbox": bbox(all_coords),
            "walk_km": round(sum(s["meters"] for s in segments if s["mode"] == "WALK") / 1000, 1),
            "travel_min": sum(s["minutes"] for s in segments),
            "rides": sum(1 for s in segments if s["mode"] != "WALK"),
            "libraries": tour_libs,
            "segments": segments,
            "steps": steps,
        })

    OUT.write_text(json.dumps({"tours": tours}, separators=(",", ":")))
    missing = sum(1 for t in tours for s in t["segments"]
                  if s["mode"] != "WALK" and not (s["from_stop"] and s["to_stop"]))
    print(f"Wrote {OUT.name}: {len(tours)} tours, "
          f"{sum(len(t['steps']) for t in tours)} steps, {OUT.stat().st_size // 1024} KB; "
          f"{missing} rides missing a stop name")


if __name__ == "__main__":
    main()
