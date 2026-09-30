// Lightens a hex color by mixing it 40% of the way toward white.
// Used for the "walking" bar (lighter) vs "transit" bar (full color)
// in ChoroplethMap and SwipeMap.
export function lighten(hex) {
	const r = parseInt(hex.slice(1, 3), 16);
	const g = parseInt(hex.slice(3, 5), 16);
	const b = parseInt(hex.slice(5, 7), 16);
	const mix = (c) => Math.round(255 + (c - 255) * 0.4);
	return `rgb(${mix(r)},${mix(g)},${mix(b)})`;
}
