// Shared MapLibre setup used by WalkMap, TransitMap, and SwipeMap.

export const MAP_STYLE_URL = 'https://tiles.stadiamaps.com/styles/alidade_smooth.json';

export async function getStyle() {
	const res = await fetch(MAP_STYLE_URL);
	const style = await res.json();
	style.layers = style.layers.filter(l => l.type !== 'symbol');
	return style;
}

// Base options shared by every map instance.
// Usage: new maplibregl.Map({ container, style, ...MAP_OPTIONS })
export const MAP_OPTIONS = {
	center: [-79.386783, 43.670203],
	zoom: 9,
	dragRotate: false,
	touchPitch: false,
	minZoom: 9,
	maxZoom: 17,
	projection: 'mercator',
	attributionControl: false,
};

export const BEARING = -17;

// Toronto bounds + padding, tuned per breakpoint (phone / tablet / desktop).
// Tablet gets a tighter crop (originally added for iPad) and phone gets more
// padding around the edges.
export function getMapView(width) {
	const isPhone = width <= 600;
	const isTablet = width > 600 && width <= 1024;
	const bounds = isTablet
		? [[-79.60, 43.59], [-79.12, 43.85]]
		: [[-79.62, 43.582], [-79.085, 43.858]];
	const padding = isPhone ? 24 : (isTablet ? 3 : 0);
	return { bounds, padding };
}

// Fits a map to the Toronto view for the current window width.
// Call once inside map.on('load', ...).
export function fitToToronto(map) {
	const { bounds, padding } = getMapView(window.innerWidth);
	map.fitBounds(bounds, { padding, bearing: BEARING, duration: 0 });
}

// Shared paint for the library-branch circle layer (used by WalkMap,
// TransitMap, and both SwipeMap panels).
export const LIBRARY_LAYER_PAINT = {
	'circle-color': '#015FC1',
	'circle-radius': 4,
	'circle-stroke-color': '#ffffff',
	'circle-stroke-width': 1.5,
};

// Shared paint for the TTC rapid-transit line layer.
export const TRANSIT_LINE_PAINT = {
	'line-color': '#000000',
	'line-opacity': 0.7,
	'line-width': 2,
};

// under_15 / 15_to_30 / over_30 -> fill color. Used by WalkMap and
// TransitMap's isochrone fill layers.
export const ISOCHRONE_COLOR_EXPR = [
	'match', ['get', 'time_bucket'],
	'under_15', '#C4A7C9',
	'15_to_30', '#9865A1',
	'over_30', '#6D247A',
	'#6D247A',
];

// Call inside map.on('load', ...) once the library layer has been added.
export function addLibraryHoverPopup(map, layerId, popup) {
	map.on('mouseenter', layerId, (e) => {
		map.getCanvas().style.cursor = 'pointer';
		const coords = e.features[0].geometry.coordinates.slice();
		const name = e.features[0].properties.BranchName ?? 'Library';
		popup.setLngLat(coords).setHTML(`<b>${name}</b>`).addTo(map);
	});
	map.on('mouseleave', layerId, () => {
		map.getCanvas().style.cursor = '';
		popup.remove();
	});
}
