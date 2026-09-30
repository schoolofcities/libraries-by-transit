// Shared constants and text helpers for the library tour page.

export const WALK_COLOR = '#00A189'; // --brandMedGreen

// Open-book "library" icon from Maki (Mapbox, CC0-1.0, v8.2.0), inlined.
export const BOOK_ICON =
	'<svg viewBox="0 0 15 15" width="14" height="14" aria-hidden="true"><path fill="currentColor" d="M1.0819,9.9388C0.9871,9.867,1.0007,9.7479,1.0007,9.7479L1.5259,3.5c0,0,0.0082-0.0688,0.0388-0.104C1.584,3.374,1.6084,3.342,1.6544,3.3232C2.1826,3.1072,5.0537,1.5519,6.5,3c0.2397,0.2777,0.4999,0.6876,0.4999,1v5.2879c0,0,0.0062,0.1122-0.0953,0.1801c-0.0239,0.016-0.124,0.0616-0.242,0.0026c-2.2253-1.1134-4.711,0.1546-5.3381,0.4871C1.1987,10.0244,1.1006,9.9531,1.0819,9.9388zM13.6754,9.9577c-0.6271-0.3325-3.1128-1.6005-5.3381-0.4871c-0.118,0.059-0.2181,0.0134-0.242-0.0026C7.9939,9.4001,8.0001,9.2879,8.0001,9.2879V4c0-0.3124,0.2602-0.7223,0.4999-1c1.4463-1.4481,4.2991,0.1071,4.8273,0.3232c0.046,0.0188,0.0704,0.0508,0.0897,0.0728C13.4476,3.4312,13.4558,3.5,13.4558,3.5l0.5435,6.2479c0,0,0.0136,0.1191-0.0812,0.1909C13.8994,9.9531,13.8013,10.0244,13.6754,9.9577zM8.8647,12.6863c0.0352-0.0085,0.0964-0.0443,0.1179-0.0775c0.0236-0.0364,0.0378-0.0617,0.0423-0.1088c0.0495-0.9379,1.6245-1.8119,4.6477-0.0298c0.0775,0.0441,0.1666,0.0396,0.2425-0.0155C14.0014,12.392,14,12.2859,14,12.2859v-0.5542c0,0,0.0003-0.0764-0.0272-0.1184c-0.0205-0.0312-0.0476-0.0643-0.0926-0.0858c-2.0254-1.3145-4.5858-1.8972-5.8854-0.1592c-0.0181,0.0423-0.0353,0.0613-0.0728,0.0905C7.8654,11.5028,7.7964,11.5,7.7964,11.5H7.2109c0,0-0.069,0.0028-0.1256-0.0412c-0.0375-0.0292-0.0547-0.0482-0.0728-0.0905c-1.2996-1.738-3.86-1.1828-5.8854,0.1317c-0.045,0.0215-0.0721,0.0546-0.0926,0.0858c-0.0275,0.042-0.0272,0.1184-0.0272,0.1184v0.5542c0,0-0.0014,0.1061,0.0849,0.1688c0.0759,0.0551,0.165,0.0596,0.2425,0.0155c3.0232-1.7821,4.5982-0.8806,4.6477,0.0573c0.0045,0.0471,0.0187,0.0724,0.0423,0.1088c0.0215,0.0332,0.0827,0.069,0.1179,0.0775C6.8645,12.8656,7.9112,12.9363,8.8647,12.6863z"/></svg>';

// Mode icons for the moving dot, from Maki (Mapbox, CC0-1.0, v8.2.0). Inner SVG
// markup for a 0 0 15 15 viewBox.
export const MODE_ICONS = {
	'bus': '<path d="M2 3C2 1.9 2.9 1 4 1H11C12.1 1 13 1.9 13 3V11C13 12 12 12 12 12V13C12 13.55 11.55 14 11 14C10.45 14 10 13.55 10 13V12H5V13C5 13.55 4.55 14 4 14C3.45 14 3 13.55 3 13V12C2 12 2 11 2 11V3ZM3.5 4C3.22 4 3 4.22 3 4.5V7.5C3 7.78 3.22 8 3.5 8H11.5C11.78 8 12 7.78 12 7.5V4.5C12 4.22 11.78 4 11.5 4H3.5ZM4 9C3.45 9 3 9.45 3 10C3 10.55 3.45 11 4 11C4.55 11 5 10.55 5 10C5 9.45 4.55 9 4 9ZM11 9C10.45 9 10 9.45 10 10C10 10.55 10.45 11 11 11C11.55 11 12 10.55 12 10C12 9.45 11.55 9 11 9ZM4 2.5C4 2.78 4.22 3 4.5 3H10.5C10.78 3 11 2.78 11 2.5C11 2.22 10.78 2 10.5 2H4.5C4.22 2 4 2.22 4 2.5Z"/>',
	'rail-light': '<path d="M5.5,0C5,0,5,0.5,5,0.5v1C5,1.777,5.223,2,5.5,2S6,1.777,6,1.5V1h1v2H6c0,0-2,0-2,2v3c0,3,3,3,3,3h1c0,0,3,0,3-3V5c0-2-2-2-2-2H8V1h1v0.5C9,1.777,9.223,2,9.5,2S10,1.777,10,1.5v-1C10,0,9.5,0,9.5,0H5.5z M7.5,4l2.0449,0.7734L10,6.5C10.1316,7,9.5,7,9.5,7h-4c0,0-0.6316,0-0.5-0.5l0.4551-1.7266L7.5,4z M7.5,8C7.7761,8,8,8.2239,8,8.5S7.7761,9,7.5,9S7,8.7761,7,8.5S7.2239,8,7.5,8z M4.125,12L3,15h1.5l0.375-1h5.25l0.375,1H12l-1.125-3h-1.5l0.375,1h-4.5l0.375-1H4.125z"/>',
	'rail-metro': '<path d="M5.5,0c0,0-0.75,0-1,1L3,6.5V10c0,1,1,1,1,1h7c0,0,1,0,1-1V6.5L10.5,1c-0.2727-1-1-1-1-1H5.5z M6.5,1.5h2c0,0,0.5357,0,0.75,1L10,6c0.2146,1.0017-1,1-1,1H6c0,0-1.2146,0.0017-1-1l0.75-3.5C5.9643,1.5,6.5,1.5,6.5,1.5z M5,8c0.5523,0,1,0.4477,1,1s-0.4477,1-1,1S4,9.5523,4,9S4.4477,8,5,8z M6.75,8h1.5C8.3885,8,8.5,8.1115,8.5,8.25S8.3885,8.5,8.25,8.5h-1.5C6.6115,8.5,6.5,8.3885,6.5,8.25S6.6115,8,6.75,8z M10,8c0.5523,0,1,0.4477,1,1s-0.4477,1-1,1S9,9.5523,9,9S9.4477,8,10,8z M4.125,12L3,15h1.5l0.375-1h5.25l0.375,1H12l-1.125-3h-1.5l0.375,1h-4.5l0.375-1H4.125z"/>',
	'shoe': '<path d="M9.5,7a9.97,9.97,0,0,1-1.315-.948L6.01,3.221a.558.558,0,0,0-1,.279H5V5H3.209a.5.5,0,0,1-.357-.148S2.5,4,2,4H1.5a.5.5,0,0,0-.5.5V9H6.5c1.5,0,2,1,3.5,1h4V9.5C14,8,10.547,7.594,9.5,7Zm0,4a3.131,3.131,0,0,1-1.526-.447A4.1,4.1,0,0,0,6,10H1v1.5a.5.5,0,0,0,.5.5h4a.5.5,0,0,0,.5-.5V11a3.134,3.134,0,0,1,1.526.447A4.1,4.1,0,0,0,9.5,12h4a.5.5,0,0,0,.5-.5V11Z"/>',
};

// Which icon the dot shows while on a segment.
export function modeIcon(seg) {
	if (!seg || seg.mode === 'WALK') return 'shoe';
	if (seg.mode === 'SUBWAY') return 'rail-metro';
	if (seg.mode === 'TRAM') return 'rail-light';
	return 'bus';
}

const MODE_LABELS = { BUS: 'Bus', TRAM: 'Streetcar', SUBWAY: 'Subway', RAIL: 'Train' };

// Lines 5 and 6 are light rail but come through GTFS as TRAM, like streetcars.
export function modeLabel(seg) {
	if (seg.mode === 'TRAM' && (seg.line === '5' || seg.line === '6')) return 'LRT';
	return MODE_LABELS[seg.mode] ?? 'Transit';
}

export function minutes(n) {
	return `${n} min`;
}

export function distance(meters) {
	return meters < 1000 ? `${Math.round(meters / 10) * 10} m` : `${(meters / 1000).toFixed(1)} km`;
}

// Segments are keyed by id within a tour.
export function segmentsById(tour) {
	return Object.fromEntries(tour.segments.map((s) => [s.id, s]));
}

export function stepSegments(tour, step, byId = segmentsById(tour)) {
	return step.segs.map((id) => byId[id]);
}

// Bounds covering every tour, for the overview.
export function allToursBbox(tours) {
	const b = tours.map((t) => t.bbox);
	return [
		[Math.min(...b.map((x) => x[0])), Math.min(...b.map((x) => x[1]))],
		[Math.max(...b.map((x) => x[2])), Math.max(...b.map((x) => x[3]))]
	];
}

// ── Paths for the scroll-driven dot ───────────────────────────────────────────

// Approximate ground distance in metres between two [lon, lat] points.
function metres(a, b) {
	const kx = 111320 * Math.cos(((a[1] + b[1]) / 2) * (Math.PI / 180));
	return Math.hypot((b[0] - a[0]) * kx, (b[1] - a[1]) * 110540);
}

function pathOf(coords) {
	const cum = [0];
	for (let i = 1; i < coords.length; i++) cum.push(cum[i - 1] + metres(coords[i - 1], coords[i]));
	return { coords, cum, total: cum[cum.length - 1] };
}

// For each step, the segments the dot travels, each with its own path and its
// start and end distance along the step. Library and intro steps have no
// segments; the dot sits at `point`.
export function buildStepPaths(tour, steps) {
	const byId = segmentsById(tour);
	return steps.map((s) => {
		if (!s.segs.length) {
			const lib = tour.libraries[(s.library ?? 1) - 1];
			return { point: [lib.lon, lib.lat], total: 0, parts: [] };
		}
		let d = 0;
		const parts = s.segs.map((id) => {
			const path = pathOf(byId[id].coords);
			const part = { seg: byId[id], path, start: d, end: d + path.total };
			d += path.total;
			return part;
		});
		return { point: parts[0].path.coords[0], total: d, parts };
	});
}

// Point `dist` metres along a single path, plus the coordinates travelled.
function alongPath(path, dist) {
	const { coords, cum } = path;
	if (dist <= 0) return { point: coords[0], travelled: [coords[0], coords[0]] };
	for (let i = 1; i < coords.length; i++) {
		if (cum[i] >= dist) {
			const t = (dist - cum[i - 1]) / (cum[i] - cum[i - 1] || 1);
			const a = coords[i - 1];
			const b = coords[i];
			const point = [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t];
			return { point, travelled: [...coords.slice(0, i), point] };
		}
	}
	return { point: coords[coords.length - 1], travelled: coords };
}

// Where the dot is `frac` of the way through a step, and the travelled part of
// each of the step's segments so far.
export function along(stepPath, frac) {
	if (!stepPath.parts.length) return { point: stepPath.point, travelled: [] };
	const dist = frac * stepPath.total;
	let point = stepPath.point;
	const travelled = [];
	for (const part of stepPath.parts) {
		if (dist <= part.start) break;
		const r = alongPath(part.path, Math.min(dist, part.end) - part.start);
		travelled.push({ seg: part.seg, coords: r.travelled });
		point = r.point;
	}
	return { point, travelled };
}

export const lerp = (a, b, t) => a + (b - a) * t;
