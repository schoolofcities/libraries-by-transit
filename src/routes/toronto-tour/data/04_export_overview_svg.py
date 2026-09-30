"""
Export the overview map's routes and library icons as a standalone SVG (no
basemap), matching the page: Web Mercator, rotated -17 degrees so Toronto's grid
runs up-down, each tour in its colour with a white casing, and each library as
a tour-coloured dot with a white book icon (Maki "library", CC0).

Layers (top-level groups, each with one sub-group per tour): route casings,
routes, libraries. Library dots carry the branch name as a <title>.

Input:  tour_app.json (from 03_build_app_data.py)
Output: tour_overview.svg

Usage: python3 04_export_overview_svg.py
"""

import json
import math
import re
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE / "tour_overview.svg"
TOUR_JS = HERE.parent / "lib" / "tour.js"

WIDTH = 1400  # px; height follows from the data's extent
PAD = 30
BEARING = -17
LINE_W = 3
CASING_W = 6
DOT_R = 8
DOT_STROKE = 1.5
ICON = 11  # book icon size, px


def mercator(lon, lat):
    x = (lon + 180) / 360
    s = math.sin(math.radians(lat))
    y = 0.5 - math.log((1 + s) / (1 - s)) / (4 * math.pi)
    return x, y


def main():
    tours = json.loads((HERE / "tour_app.json").read_text())["tours"]
    book_path = re.search(r'd="([^"]+)"', TOUR_JS.read_text().split("BOOK_ICON")[1]).group(1)

    rad = math.radians(BEARING)
    cos, sin = math.cos(rad), math.sin(rad)

    def rotated(lon, lat):
        x, y = mercator(lon, lat)
        return x * cos + y * sin, -x * sin + y * cos

    pts = [rotated(*c) for t in tours for s in t["segments"] for c in s["coords"]]
    pts += [rotated(l["lon"], l["lat"]) for t in tours for l in t["libraries"]]
    x0, x1 = min(p[0] for p in pts), max(p[0] for p in pts)
    y0, y1 = min(p[1] for p in pts), max(p[1] for p in pts)
    scale = (WIDTH - 2 * PAD) / (x1 - x0)
    height = round((y1 - y0) * scale + 2 * PAD)

    def xy(lon, lat):
        x, y = rotated(lon, lat)
        return (x - x0) * scale + PAD, (y - y0) * scale + PAD

    def path_d(coords):
        return "M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in (xy(*c) for c in coords))

    casings, lines, libs = [], [], []
    for t in tours:
        d = "".join(path_d(s["coords"]) for s in t["segments"])
        casings.append(f'<g id="casing-tour-{t["id"]}"><path d="{d}"/></g>')
        lines.append(f'<g id="route-tour-{t["id"]}" stroke="{t["color"]}"><path d="{d}"/></g>')
        dots = []
        for l in t["libraries"]:
            x, y = xy(l["lon"], l["lat"])
            name = l["name"].replace("&", "&amp;").replace("<", "&lt;")
            dots.append(
                f'<g transform="translate({x:.1f},{y:.1f})"><title>{l["n"]}. {name}</title>'
                f'<circle r="{DOT_R}"/><use href="#book" x="{-ICON / 2}" y="{-ICON / 2}" '
                f'width="{ICON}" height="{ICON}"/></g>'
            )
        libs.append(f'<g id="libraries-tour-{t["id"]}" fill="{t["color"]}">{"".join(dots)}</g>')

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {height}" width="{WIDTH}" height="{height}">
<defs>
<symbol id="book" viewBox="0 0 15 15"><path fill="#ffffff" stroke="none" d="{book_path}"/></symbol>
</defs>
<g id="route-casings" fill="none" stroke="#ffffff" stroke-width="{CASING_W}" stroke-linecap="round" stroke-linejoin="round">
{chr(10).join(casings)}
</g>
<g id="routes" fill="none" stroke-width="{LINE_W}" stroke-linecap="round" stroke-linejoin="round">
{chr(10).join(lines)}
</g>
<g id="libraries" stroke="#ffffff" stroke-width="{DOT_STROKE}">
{chr(10).join(libs)}
</g>
</svg>
"""
    OUT.write_text(svg)
    print(f"Wrote {OUT.name}: {WIDTH}x{height}px, {len(tours)} tours, "
          f"{sum(len(t['libraries']) for t in tours)} libraries, {OUT.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
