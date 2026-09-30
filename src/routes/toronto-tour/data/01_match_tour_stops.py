"""
Match the 10 tours x 10 libraries in the spreadsheet to points in libraries.geojson.

Matching is by address (street number + first word of street name), since branch
names in the spreadsheet don't always match the geojson (closure notes, etc.). Two
branches have since moved and been renamed (Ethennonnhawahstihnen, formerly Bayview;
Junction Triangle, formerly Perth/Dupont), so those fall back to a name match and
use the geojson's current location.

Output: tour_stops.csv (route, stop, branch_name, address, lon, lat)

Usage: python3 01_match_tour_stops.py
"""

import json
import re
from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent
XLSX = HERE / "Your Library Tour Address.xlsx"
LIBRARIES = HERE / "libraries.geojson"
OUT = HERE / "tour_stops.csv"

# Spreadsheet layout: 5 blocks of 3 columns (stop #, name, address) side by side.
# Rows 0-9 hold the odd routes (1,3,5,7,9), rows 12-21 the even routes (2,4,...,10).
BLOCK_ROWS = {0: range(0, 10), 1: range(12, 22)}


def clean(s):
    return re.sub(r"\s+", " ", str(s)).strip()


def address_key(address):
    """Street number + first word of the street name from the first address component
    that starts with a number, e.g. '1515 Albion Road, Toronto' -> '1515 albion'."""
    for part in clean(address).split(","):
        part = part.strip().lower()
        m = re.match(r"^(?:[a-z]?\d+-)?(\d+[a-z]?(?: 1/2)?)\s+(.*)$", part)
        if m:
            num, street = m.groups()
            return f"{num} {street.split()[0].rstrip('.')}"
    return None


def read_tours():
    raw = pd.read_excel(XLSX, header=None)
    rows = []
    for block in range(5):
        c = block * 3
        for half, row_range in BLOCK_ROWS.items():
            route = block * 2 + 1 + half
            for r in row_range:
                stop, name, address = raw.iat[r + 1, c], raw.iat[r + 1, c + 1], raw.iat[r + 1, c + 2]
                rows.append({
                    "route": route,
                    "stop": int(stop),
                    "sheet_name": clean(name),
                    "sheet_address": clean(address),
                })
    return pd.DataFrame(rows).sort_values(["route", "stop"])


def main():
    tours = read_tours()

    libs = json.load(open(LIBRARIES))["features"]
    lib_by_key = {}
    for f in libs:
        key = address_key(f["properties"]["Address"])
        lib_by_key.setdefault(key, []).append(f)

    out, unmatched = [], []
    for t in tours.itertuples():
        key = address_key(t.sheet_address)
        hits = lib_by_key.get(key, [])
        if not hits:
            base = t.sheet_name.split(" - ")[0].lower()
            hits = [f for f in libs if base in f["properties"]["BranchName"].lower()]
        if len(hits) != 1:
            unmatched.append((t.route, t.stop, t.sheet_name, t.sheet_address, key, len(hits)))
            continue
        f = hits[0]
        lon, lat = f["geometry"]["coordinates"]
        out.append({
            "route": t.route,
            "stop": t.stop,
            "branch_name": clean(f["properties"]["BranchName"]),
            "address": clean(f["properties"]["Address"]),
            "sheet_name": t.sheet_name.split(" - ")[0],
            "lon": lon,
            "lat": lat,
        })

    if unmatched:
        for u in unmatched:
            print("UNMATCHED route %s stop %s: %s | %s | key=%s | hits=%s" % u)
        raise SystemExit(1)

    df = pd.DataFrame(out)
    assert len(df) == 100 and df["branch_name"].is_unique, "expected 100 unique libraries"
    df.to_csv(OUT, index=False)
    print(f"Wrote {len(df)} stops to {OUT.name}")


if __name__ == "__main__":
    main()
