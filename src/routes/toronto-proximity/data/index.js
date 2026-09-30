// URLs for the proximity map's data files. Vite's `?url` import copies each file
// into the build and returns its path (including the site's base path), so the
// components don't hardcode `/public-libraries/data/...`.

import transitWeekday from './isochrones_transit_weekday_window.geojson?url';
import transitWeekend from './isochrones_transit_weekend_window.geojson?url';
import walk from './isochrones_walk.geojson?url';
import censusTracts from './census_tracts_demographics.geojson?url';
import libraries from './libraries.geojson?url';
import ttcLines from './ttc_main_lines.geojson?url';

export const DATA = { transitWeekday, transitWeekend, walk, censusTracts, libraries, ttcLines };
