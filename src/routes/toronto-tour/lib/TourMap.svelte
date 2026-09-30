<script>
	// Map for the library tour page. On the overview it shows all tours. For one
	// tour it's driven by scroll `progress` (step index + fraction through that
	// step): a dot travels along the route, the travelled part is drawn at full
	// strength over a faded version of the whole tour, and the camera follows
	// the dot, easing its zoom into the next step near the end of each one.

	import { onMount } from 'svelte';
	import maplibregl from 'maplibre-gl';
	import 'maplibre-gl/dist/maplibre-gl.css';
	import mapStyle from './map-style.json';
	import { WALK_COLOR, BOOK_ICON, MODE_ICONS, modeIcon, allToursBbox, buildStepPaths, along, lerp } from './tour.js';

	let {
		tours,
		tour = null, // selected tour, or null for the overview
		steps = [], // steps of the selected tour, including the intro
		progress = 0, // step index + fraction through that step
		hoveredTour = null,
		onselect = () => {}
	} = $props();

	let container;
	let map = $state(null);
	let markers = [];
	let paths = [];
	let cameras = [];
	let doneBefore = []; // per step: line features for everything travelled before it
	let lastIndex = -1;

	const EMPTY = { type: 'FeatureCollection', features: [] };

	// Camera settings. The zoom for a step fits its whole path, clamped; the last
	// BLEND of each step eases toward the next step's camera.
	const LIBRARY_ZOOM = 15.5;
	const MIN_ZOOM = 11;
	const MAX_ZOOM = 16.5;
	const BLEND = 0.3;

	// Rotate so Toronto's street grid runs up-down (same as the project's other maps).
	const BEARING = -17;

	const collection = (features) => ({ type: 'FeatureCollection', features });

	// Camera that fits a set of [lon, lat] points in the rotated view. MapLibre's
	// own fitBounds fits the corners of a north-up box, which leaves a lot of
	// empty space once the map is rotated.
	function fitRotated(points, padding) {
		const rad = (BEARING * Math.PI) / 180;
		const cos = Math.cos(rad);
		const sin = Math.sin(rad);
		const merc = points.map((p) => maplibregl.MercatorCoordinate.fromLngLat(p));
		// Rotate into screen orientation (x right, y down).
		const rot = merc.map((m) => [m.x * cos + m.y * sin, -m.x * sin + m.y * cos]);
		const xs = rot.map((r) => r[0]);
		const ys = rot.map((r) => r[1]);
		const [x1, x2, y1, y2] = [Math.min(...xs), Math.max(...xs), Math.min(...ys), Math.max(...ys)];
		const cx = (x1 + x2) / 2;
		const cy = (y1 + y2) / 2;
		const centre = new maplibregl.MercatorCoordinate(cx * cos - cy * sin, cx * sin + cy * cos).toLngLat();
		const { clientWidth: w, clientHeight: h } = container;
		const scale = Math.min((w - 2 * padding) / (x2 - x1 || 1e-9), (h - 2 * padding) / (y2 - y1 || 1e-9));
		return { center: [centre.lng, centre.lat], zoom: Math.log2(scale / 512) };
	}

	// Icons (Maki, 15x15 viewBox) rasterized at 2x so they stay crisp, in white
	// and black ('-dark'): the book for the overview's library dots, and a mode
	// icon for the moving dot.
	function addIconImages(m) {
		const book = BOOK_ICON.match(/<path[^>]*\/?>(<\/path>)?/)[0];
		const icons = { book, ...MODE_ICONS };
		const size = 28;
		const variants = Object.entries(icons).flatMap(([name, inner]) => [
			[name, inner, '#ffffff'],
			[`${name}-dark`, inner, '#000000']
		]);
		for (const [name, inner, fill] of variants) {
			const svg =
				`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 15 15" width="${size}" height="${size}" fill="${fill}">` +
				inner.replace(/fill="currentColor"/g, '') +
				'</svg>';
			const img = new Image(size, size);
			img.onload = () => {
				const canvas = document.createElement('canvas');
				canvas.width = canvas.height = size;
				const ctx = canvas.getContext('2d');
				ctx.drawImage(img, 0, 0, size, size);
				if (!m.hasImage(name)) m.addImage(name, ctx.getImageData(0, 0, size, size), { pixelRatio: 2 });
			};
			img.src = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svg);
		}
	}

	// White icons unless white falls below WCAG's 3:1 contrast for graphics on
	// this colour (e.g. Line 1 yellow, Line 5 orange); then use black.
	function isLight(hex) {
		const lin = (c) => (c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4);
		const [r, g, b] = [1, 3, 5].map((k) => lin(parseInt(hex.slice(k, k + 2), 16) / 255));
		const L = 0.2126 * r + 0.7152 * g + 0.0722 * b;
		return 1.05 / (L + 0.05) < 3;
	}

	const allTourPoints = () => tours.flatMap((t) => t.segments.flatMap((s) => s.coords));

	function line(seg, coords) {
		return {
			type: 'Feature',
			properties: { id: seg.id, walk: seg.mode === 'WALK', color: seg.color ?? WALK_COLOR },
			geometry: { type: 'LineString', coordinates: coords }
		};
	}

	function overviewData() {
		return {
			routes: collection(
				tours.map((t) => ({
					type: 'Feature',
					properties: { tour: t.id, color: t.color },
					geometry: { type: 'MultiLineString', coordinates: t.segments.map((s) => s.coords) }
				}))
			),
			libraries: collection(
				tours.flatMap((t) =>
					t.libraries.map((l) => ({
						type: 'Feature',
						properties: { tour: t.id, color: t.color },
						geometry: { type: 'Point', coordinates: [l.lon, l.lat] }
					}))
				)
			)
		};
	}

	function stopsData(t) {
		return collection(
			t.segments
				.filter((s) => s.mode !== 'WALK')
				.flatMap((s) =>
					[s.coords[0], s.coords[s.coords.length - 1]].map((c) => ({
						type: 'Feature',
						properties: { id: s.id, color: s.color },
						geometry: { type: 'Point', coordinates: c }
					}))
				)
		);
	}

	// Route layers are added three times: the faded whole tour ('base'), the
	// steps already completed ('done', updated only when the step changes), and
	// the current step's travelled part ('progress', updated every scroll frame
	// and kept small so scrolling stays smooth).
	function addRouteLayers(m, source, prefix, opacity) {
		m.addLayer({
			id: `${prefix}-casing`,
			type: 'line',
			source,
			filter: ['!', ['get', 'walk']],
			layout: { 'line-join': 'round', 'line-cap': 'round' },
			paint: { 'line-color': '#ffffff', 'line-width': 9, 'line-opacity': opacity }
		});
		m.addLayer({
			id: `${prefix}-walk-line`,
			type: 'line',
			source,
			filter: ['get', 'walk'],
			layout: { 'line-join': 'round', 'line-cap': 'round' },
			paint: { 'line-color': WALK_COLOR, 'line-width': 0.5, 'line-opacity': opacity }
		});
		m.addLayer({
			id: `${prefix}-walk`,
			type: 'line',
			source,
			filter: ['get', 'walk'],
			layout: { 'line-join': 'round', 'line-cap': 'round' },
			paint: {
				'line-color': WALK_COLOR,
				'line-width': 4,
				'line-dasharray': [0.1, 2],
				'line-opacity': opacity
			}
		});
		m.addLayer({
			id: `${prefix}-ride`,
			type: 'line',
			source,
			filter: ['!', ['get', 'walk']],
			layout: { 'line-join': 'round', 'line-cap': 'round' },
			paint: { 'line-color': ['get', 'color'], 'line-width': 5, 'line-opacity': opacity }
		});
	}

	onMount(() => {
		const m = new maplibregl.Map({
			container,
			style: mapStyle,
			bounds: allToursBbox(tours),
			bearing: BEARING,
			// Zoom only with the +/- buttons; the wheel scrolls through the route
			// instead (the page forwards wheel events over the map to the panel).
			scrollZoom: false,
			doubleClickZoom: false,
			boxZoom: false,
			touchZoomRotate: false,
			dragRotate: false,
			touchPitch: false,
			minZoom: 9,
			maxZoom: 18,
			attributionControl: false
		});
		m.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'top-right');
		m.addControl(
			new maplibregl.AttributionControl({
				compact: true,
				customAttribution:
					'Data from <a href="https://open.toronto.ca/dataset/ttc-routes-and-schedules/" target="_blank" rel="noopener">TTC</a>, ' +
					'<a href="https://open.toronto.ca/dataset/library-branch-general-information/" target="_blank" rel="noopener">Toronto Public Library</a>, ' +
					'<a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> contributors'
			}),
			'bottom-right'
		);

		m.on('load', () => {
			// Start with the attribution collapsed behind its (i) button.
			container.querySelector('.maplibregl-ctrl-attrib')?.classList.remove('maplibregl-compact-show');
			if (!tour) m.jumpTo({ ...fitRotated(allTourPoints(), 30), bearing: BEARING });
			const ov = overviewData();
			m.addSource('overview-routes', { type: 'geojson', data: ov.routes });
			m.addSource('overview-libraries', { type: 'geojson', data: ov.libraries });
			m.addSource('base', { type: 'geojson', data: EMPTY });
			m.addSource('done', { type: 'geojson', data: EMPTY });
			m.addSource('progress', { type: 'geojson', data: EMPTY });
			m.addSource('stops', { type: 'geojson', data: EMPTY });
			m.addSource('dot', { type: 'geojson', data: EMPTY });

			m.addLayer({
				id: 'overview-routes-casing',
				type: 'line',
				source: 'overview-routes',
				layout: { 'line-join': 'round', 'line-cap': 'round' },
				paint: { 'line-color': '#ffffff', 'line-width': 6 }
			});
			m.addLayer({
				id: 'overview-routes',
				type: 'line',
				source: 'overview-routes',
				layout: { 'line-join': 'round', 'line-cap': 'round' },
				paint: { 'line-color': ['get', 'color'], 'line-width': 3 }
			});
			m.addLayer({
				id: 'overview-libraries',
				type: 'circle',
				source: 'overview-libraries',
				paint: {
					'circle-radius': 8,
					'circle-color': ['get', 'color'],
					'circle-stroke-color': '#ffffff',
					'circle-stroke-width': 1.5
				}
			});
			m.addLayer({
				id: 'overview-books',
				type: 'symbol',
				source: 'overview-libraries',
				layout: { 'icon-image': 'book', 'icon-size': 0.8, 'icon-allow-overlap': true },
				paint: { 'icon-opacity': 1 }
			});
			addIconImages(m);

			addRouteLayers(m, 'base', 'base', 0.3);
			addRouteLayers(m, 'done', 'done', 1);
			addRouteLayers(m, 'progress', 'progress', 1);
			m.addLayer({
				id: 'stops',
				type: 'circle',
				source: 'stops',
				paint: {
					'circle-radius': 4,
					'circle-color': '#ffffff',
					'circle-stroke-color': ['get', 'color'],
					'circle-stroke-width': 2
				}
			});
			m.addLayer({
				id: 'dot-halo',
				type: 'circle',
				source: 'dot',
				paint: { 'circle-radius': 17, 'circle-color': ['get', 'color'], 'circle-opacity': 0.2 }
			});
			m.addLayer({
				id: 'dot',
				type: 'circle',
				source: 'dot',
				paint: {
					'circle-radius': 11,
					'circle-color': ['get', 'color'],
					'circle-stroke-color': '#ffffff',
					'circle-stroke-width': 2
				}
			});
			// Icon for how the dot is travelling (walk, bus, streetcar/LRT, subway), in
			// white or black depending on the dot's colour.
			m.addLayer({
				id: 'dot-icon',
				type: 'symbol',
				source: 'dot',
				layout: {
					'icon-image': ['get', 'icon'],
					'icon-size': 0.95,
					'icon-allow-overlap': true,
					'icon-ignore-placement': true
				}
			});

			for (const id of ['overview-routes', 'overview-routes-casing']) {
				m.on('click', id, (e) => onselect(e.features[0].properties.tour));
				m.on('mouseenter', id, () => (m.getCanvas().style.cursor = 'pointer'));
				m.on('mouseleave', id, () => (m.getCanvas().style.cursor = ''));
			}

			m.on('resize', () => {
				if (tour) {
					cameras = stepCameras();
					follow(progress);
				}
			});

			map = m;
		});

		return () => m.remove();
	});

	// Camera for each step: centre and zoom at its start, plus the zoom used
	// while following the dot along it.
	function stepCameras() {
		return steps.map((s, i) => {
			const p = paths[i];
			if (s.kind === 'intro') {
				return { fixed: true, ...fitRotated(tour.segments.flatMap((g) => g.coords), 50) };
			}
			if (s.kind === 'library') return { fixed: true, center: p.point, zoom: LIBRARY_ZOOM };
			const { zoom } = fitRotated(p.parts.flatMap((part) => part.path.coords), 60);
			return { fixed: false, zoom: Math.max(MIN_ZOOM, Math.min(MAX_ZOOM, zoom)) };
		});
	}

	function cameraAt(i, frac, dotPoint) {
		const c = cameras[i];
		return { center: c.fixed ? c.center : dotPoint, zoom: c.zoom };
	}

	// Switch between overview and a single tour.
	$effect(() => {
		if (!map) return;
		const visibility = tour ? 'none' : 'visible';
		for (const id of ['overview-routes-casing', 'overview-routes', 'overview-libraries', 'overview-books']) {
			map.setLayoutProperty(id, 'visibility', visibility);
		}

		markers.forEach((mk) => mk.remove());
		markers = [];
		lastIndex = -1;

		if (!tour) {
			for (const src of ['base', 'done', 'progress', 'stops', 'dot']) map.getSource(src).setData(EMPTY);
			paths = [];
			cameras = [];
			doneBefore = [];
			map.easeTo({ ...fitRotated(allTourPoints(), 30), bearing: BEARING, duration: 800 });
			return;
		}

		map.getSource('base').setData(collection(tour.segments.map((s) => line(s, s.coords))));
		map.getSource('stops').setData(stopsData(tour));
		markers = tour.libraries.map(libraryMarker);
		paths = buildStepPaths(tour, steps);
		cameras = stepCameras();
		let acc = [];
		doneBefore = paths.map((p) => {
			const before = acc;
			acc = [...acc, ...p.parts.map((part) => line(part.seg, part.seg.coords))];
			return before;
		});
	});

	// Follow scroll progress.
	$effect(() => {
		if (!map || !tour || !paths.length) return;
		follow(progress);
	});

	function follow(prog) {
		const n = steps.length;
		const i = Math.max(0, Math.min(n - 1, Math.floor(prog)));
		const frac = i === n - 1 ? 0 : Math.max(0, Math.min(1, prog - i));
		const step = steps[i];
		const here = along(paths[i], frac);

		// Travelled so far: completed steps (only when the step changes), plus
		// this step's part. The intro shows the whole tour at full strength.
		if (i !== lastIndex) {
			const done = step.kind === 'intro' ? tour.segments.map((s) => line(s, s.coords)) : doneBefore[i];
			map.getSource('done').setData(collection(done));
		}
		map.getSource('progress').setData(collection(here.travelled.map((t) => line(t.seg, t.coords))));
		// The dot takes the colour of what it's travelling on (dark blue at libraries).
		const seg = here.travelled.at(-1)?.seg ?? paths[i].parts[0]?.seg;
		const color = step.kind === 'library' || !seg ? '#1E3765' : (seg.color ?? WALK_COLOR);
		const icon = (step.kind === 'library' ? 'book' : modeIcon(seg)) + (isLight(color) ? '-dark' : '');
		map.getSource('dot').setData(
			collection(
				step.kind === 'intro'
					? []
					: [{ type: 'Feature', properties: { icon, color }, geometry: { type: 'Point', coordinates: here.point } }]
			)
		);

		// Camera: follow this step, blending into the next step's start near the end.
		let cam = cameraAt(i, frac, here.point);
		if (frac > 1 - BLEND && i < n - 1) {
			const t = (frac - (1 - BLEND)) / BLEND;
			const e = t * t * (3 - 2 * t); // smoothstep
			const next = cameraAt(i + 1, 0, paths[i + 1].point);
			cam = {
				center: [lerp(cam.center[0], next.center[0], e), lerp(cam.center[1], next.center[1], e)],
				zoom: lerp(cam.zoom, next.zoom, e)
			};
		}
		map.jumpTo({ ...cam, bearing: BEARING });

		if (i !== lastIndex) {
			lastIndex = i;
			const current = step.kind === 'library' ? step.library : null;
			markers.forEach((mk, k) => mk.getElement().classList.toggle('current', k + 1 === current));
		}
	}

	// Dim other tours while one is hovered in the list.
	$effect(() => {
		if (!map) return;
		const op = hoveredTour == null ? 1 : ['case', ['==', ['get', 'tour'], hoveredTour], 1, 0.5];
		map.setPaintProperty('overview-routes', 'line-opacity', op);
		map.setPaintProperty('overview-routes-casing', 'line-opacity', op);
		map.setPaintProperty('overview-libraries', 'circle-stroke-opacity', op);
		map.setPaintProperty('overview-libraries', 'circle-opacity', op);
		map.setPaintProperty('overview-books', 'icon-opacity', op);
	});

	function libraryMarker(lib) {
		// MapLibre positions the outer element with a CSS transform, so all styling
		// (including the scale-up for the current library) goes on an inner one.
		const el = document.createElement('div');
		el.className = 'library-marker';
		el.setAttribute('aria-label', lib.name);
		const inner = document.createElement('div');
		inner.className = 'library-marker-inner';
		inner.innerHTML = BOOK_ICON;
		const label = document.createElement('div');
		label.className = 'library-marker-label';
		label.textContent = `${lib.n} · ${lib.name}`;
		el.append(inner, label);
		const popup = new maplibregl.Popup({ offset: 16, closeButton: false }).setHTML(
			`<div class="library-popup"><strong>${lib.name}</strong><br>${lib.address}<br>` +
				`<a href="${lib.url}" target="_blank" rel="noopener">Hours &amp; info ↗</a></div>`
		);
		return new maplibregl.Marker({ element: el }).setLngLat([lib.lon, lib.lat]).setPopup(popup).addTo(map);
	}
</script>

<div class="map" bind:this={container}></div>

<style>
	.map {
		width: 100%;
		height: 100%;
	}

	/* Don't set position here: MapLibre's markers rely on position: absolute. */
	.map :global(.library-marker) {
		cursor: pointer;
	}

	.map :global(.library-marker-label) {
		position: absolute;
		left: 35px;
		top: 50%;
		transform: translateY(-50%);
		white-space: nowrap;
		font-family: OpenSansBold, sans-serif;
		font-size: 12px;
		color: var(--brandDarkBlue);
		text-shadow:
			0 0 3px #fff,
			0 0 3px #fff,
			0 0 3px #fff,
			0 0 3px #fff;
		pointer-events: none;
	}

	.map :global(.library-marker-inner) {
		width: 24px;
		height: 24px;
		border-radius: 50%;
		background: var(--brandDarkBlue);
		border: 2px solid var(--brandWhite);
		color: var(--brandWhite);
		display: flex;
		align-items: center;
		justify-content: center;
		box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
		transition: transform 0.2s, box-shadow 0.2s;
	}

	.map :global(.library-marker.current) {
		z-index: 2;
	}

	.map :global(.library-marker.current .library-marker-label) {
		left: 42px;
		font-size: 13px;
	}

	/* Current library: same colours, larger, with a light blue ring. */
	.map :global(.library-marker.current .library-marker-inner) {
		transform: scale(1.35);
		box-shadow:
			0 0 0 3px var(--brandLightBlue),
			0 1px 4px rgba(0, 0, 0, 0.3);
	}

	/* The global stylesheet sets Source Serif on links; keep the attribution sans. */
	.map :global(.maplibregl-ctrl-attrib),
	.map :global(.maplibregl-ctrl-attrib a) {
		font-family: OpenSans, sans-serif;
		font-size: 10px;
	}

	.map :global(.maplibregl-ctrl-attrib a) {
		text-decoration: underline;
	}

	.map :global(.library-popup) {
		font-family: OpenSans, sans-serif;
		font-size: 13px;
		line-height: 1.5;
		color: var(--brandGray90);
	}

	.map :global(.library-popup strong) {
		font-family: OpenSansBold, sans-serif;
		font-weight: normal;
	}

	.map :global(.library-popup a) {
		font-family: OpenSans, sans-serif;
		color: var(--brandMedBlue);
	}
</style>
