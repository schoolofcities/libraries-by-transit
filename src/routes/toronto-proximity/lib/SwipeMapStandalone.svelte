<script>

	import { onMount } from "svelte";
	import maplibregl from "maplibre-gl";
	import "maplibre-gl/dist/maplibre-gl.css";
	import { getStyle, MAP_OPTIONS, fitToToronto, LIBRARY_LAYER_PAINT,
	         TRANSIT_LINE_PAINT, ISOCHRONE_COLOR_EXPR, addLibraryHoverPopup } from './mapConfigStandalone.js';
	import { DEMOGRAPHICS, CITY_AVG } from './demographics.js';
	import Legend from './LegendStandalone.svelte';
	import { DATA } from '../data/index.js';

	let leftContainer;
	let rightContainer;
	let leftMap;
	let rightMap;
	export let zoomOffset = 0;
	// px to shift the map content down after fitting, to clear the legends at the top
	// (wide screens only — compact layouts position the city and legends together, see arrangeView)
	export let panOffset = 0;

	function fitView(map) {
		fitToToronto(map);
		map.setZoom(map.getZoom() + zoomOffset);
	}

	// ── Initial layout ─────────────────────────────────────────────────────────
	// Phones and tablets: the legends stay in their corners (demographic top left,
	// travel-time bottom right); the city is fitted into the space between
	// them so neither legend covers it. 
	const COMPACT_MQ = '(max-width: 1024px), (max-width: 1100px) and (orientation: portrait), (hover: none) and (pointer: coarse)';
	const SHORT_LANDSCAPE_MQ = '(orientation: landscape) and (max-height: 500px)';
	const LEGEND_GAP = 10;      // px kept between a legend and the city
	const MAX_BOUNDS_PAD = 0.15; // how far past the initial view people can pan, as a share of its size

	let leftLegendEl;
	let rightLegendEl;
	let cityCoords = [];        // every census-tract vertex, for measuring the city on screen

	function collectCoords(geojson) {
		const out = [];
		const walk = (c) => (typeof c[0] === 'number' ? out.push(c) : c.forEach(walk));
		geojson.features.forEach(f => f.geometry && walk(f.geometry.coordinates));
		return out;
	}

	// Top and bottom of the city outline in screen px (the map is rotated, so this
	// projects real vertices rather than a bounding box)
	function cityScreenExtent(map) {
		let top = Infinity, bottom = -Infinity;
		for (const c of cityCoords) {
			const y = map.project(c).y;
			if (y < top) top = y;
			if (y > bottom) bottom = y;
		}
		return { top, bottom };
	}

	function arrangeView() {
		const compact = matchMedia(COMPACT_MQ).matches && !matchMedia(SHORT_LANDSCAPE_MQ).matches;

		if (!compact || !cityCoords.length) {
			leftMap.panBy([0, -panOffset], { duration: 0 });
		} else {
			// Free band between the bottom of the top legend and the top of the bottom legend
			const wrap = swipeContainer.getBoundingClientRect();
			const bandTop    = leftLegendEl.getBoundingClientRect().bottom - wrap.top + LEGEND_GAP;
			const bandBottom = rightLegendEl.getBoundingClientRect().top - wrap.top - LEGEND_GAP;
			const band = bandBottom - bandTop;

			// Zoom out if the city is taller than the band (e.g. landscape tablets)
			let { top, bottom } = cityScreenExtent(leftMap);
			if (band > 0 && bottom - top > band) {
				leftMap.setZoom(leftMap.getZoom() - Math.log2((bottom - top) / band));
				({ top, bottom } = cityScreenExtent(leftMap));
			}

			// Centre the city in the band (panBy syncs the right map too)
			leftMap.panBy([0, (top + bottom) / 2 - (bandTop + bandBottom) / 2], { duration: 0 });
		}

		// Keep panning/zooming near Toronto: allow a little past the starting view, no further
		const b = leftMap.getBounds();
		const padX = (b.getEast() - b.getWest()) * MAX_BOUNDS_PAD;
		const padY = (b.getNorth() - b.getSouth()) * MAX_BOUNDS_PAD;
		const maxBounds = [[b.getWest() - padX, b.getSouth() - padY], [b.getEast() + padX, b.getNorth() + padY]];
		leftMap.setMaxBounds(maxBounds);
		rightMap.setMaxBounds(maxBounds);
	}

	const demographics = DEMOGRAPHICS;
	const maxBarVal = 35;

	const barColor      = '#F1C500';
	const barColorLight = '#F9E899';
	$: transitBarW   = (activeDemog.transit / maxBarVal) * 100;
	$: walkBarW      = (activeDemog.walk    / maxBarVal) * 100;

	let activeDemog = demographics[0];

	function colorExpr(demog) {
		const { id, colors, breaks } = demog;
		return [
			'step', ['get', id],
			colors[0],
			breaks[0], colors[1],
			breaks[1], colors[2],
			breaks[2], colors[3]
		];
	}

	function setDemographic(demog) {
		activeDemog = demog;
		if (leftMap && leftMap.getLayer('ct-fill')) {
			leftMap.setPaintProperty('ct-fill', 'fill-color', colorExpr(demog));
		}
	}

	// Travel-mode toggle: walking + transit (weekday / weekend schedule) or walking only
	let timeOfWeek = 'weekday';

	const transitFiles = {
		weekday: DATA.transitWeekday,
		weekend: DATA.transitWeekend,
		walk:    DATA.walk,
	};

	const timeLabels = {
		weekday: 'Tuesday, 10:00-10:30am',
		weekend: 'Saturday, 10:00-10:30am',
		walk:    'No transit, any time',
	};

	$: timeLabel = timeLabels[timeOfWeek];
	$: modeTitle = timeOfWeek === 'walk' ? 'Walking only' : 'Walking + Transit';

	function setTimeOfWeek(val) {
		timeOfWeek = val;
		if (rightMap && rightMap.getSource('isochrones-transit')) {
			rightMap.getSource('isochrones-transit').setData(transitFiles[val]);
		}
	}

	// Swipe divider 
	let swipeContainer;
	let dividerPct = 85;
	let dragging = false;

	function onDividerMousedown(e) {
		dragging = true;
		e.preventDefault();
	}

	function onMousemove(e) {
		if (!dragging || !swipeContainer) return;
		const rect = swipeContainer.getBoundingClientRect();
		const x = (e.clientX ?? e.touches?.[0]?.clientX) - rect.left;
		dividerPct = Math.min(95, Math.max(5, (x / rect.width) * 100));
		updateClip();
	}

	function onMouseup() { dragging = false; }

	function onDividerKeydown(e) {
		const STEP = 2;
		if (e.key === 'ArrowLeft')  { dividerPct = Math.max(5, dividerPct - STEP); updateClip(); }
		if (e.key === 'ArrowRight') { dividerPct = Math.min(95, dividerPct + STEP); updateClip(); }
	}

	function updateClip() {
		if (!leftContainer) return;
		leftContainer.style.clipPath = `inset(0 ${100 - dividerPct}% 0 0)`;
	}

	// Map sync 
	let syncing = false;

	function syncTo(source, target) {
		if (!target || syncing) return;
		syncing = true;
		target.jumpTo({
			center:  source.getCenter(),
			zoom:    source.getZoom(),
			bearing: source.getBearing(),
			pitch:   source.getPitch(),
		});
		syncing = false;
	}

	onMount(async () => {

		// Census tracts are fetched here (not by URL in addSource) so the city outline can be measured for the initial layout
		const [style, censusTracts] = await Promise.all([
			getStyle(),
			fetch(DATA.censusTracts).then(r => r.json()),
		]);
		cityCoords = collectCoords(censusTracts);

		let resolveLeft, resolveRight;
		const mapsLoaded = Promise.all([
			new Promise(r => (resolveLeft = r)),
			new Promise(r => (resolveRight = r)),
		]);

		const leftPopup  = new maplibregl.Popup({ closeButton: false, closeOnClick: false });
		const rightPopup = new maplibregl.Popup({ closeButton: false, closeOnClick: false });

		leftMap = new maplibregl.Map({ container: leftContainer, style, ...MAP_OPTIONS });
		leftMap.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'top-left');

		leftMap.on('load', () => {

			fitView(leftMap);

			leftMap.addSource('census-tracts', {
				type: 'geojson',
				data: censusTracts,
			});
			leftMap.addSource('libraries-left', {
				type: 'geojson',
				data: DATA.libraries,
			});
			leftMap.addSource('transit-lines-left', {
				type: 'geojson',
				data: DATA.ttcLines
			});

			leftMap.addLayer({
				id: 'ct-fill',
				type: 'fill',
				source: 'census-tracts',
				paint: {
					'fill-color': colorExpr(activeDemog),
					'fill-opacity': 0.85,
					'fill-outline-color': 'gray',
				},
			});

			leftMap.addLayer({
				id: 'transit-line-left',
				type: 'line',
				source: 'transit-lines-left',
				paint: TRANSIT_LINE_PAINT,
			});

			leftMap.addLayer({
				id: 'library-dots-left',
				type: 'circle',
				source: 'libraries-left',
				paint: LIBRARY_LAYER_PAINT,
			});

			leftMap.on('mousemove', 'ct-fill', (e) => {
				leftMap.getCanvas().style.cursor = 'pointer';
				const p = e.features[0].properties;
				const val = p[activeDemog.id] != null ? Math.round(p[activeDemog.id]) + '%' : 'No data';
				leftPopup.setLngLat(e.lngLat).setHTML(`<b>${activeDemog.label}:</b> ${val}`).addTo(leftMap);
			});
			leftMap.on('mouseleave', 'ct-fill', () => {
				leftMap.getCanvas().style.cursor = '';
				leftPopup.remove();
			});

			leftMap.on('move', () => syncTo(leftMap, rightMap));
			resolveLeft();
		});

		// Right map
		rightMap = new maplibregl.Map({ container: rightContainer, style, ...MAP_OPTIONS });
		rightMap.addControl(new maplibregl.ScaleControl({ unit: 'metric', maxWidth: 100 }), 'bottom-right');

		rightMap.on('load', () => {

			fitView(rightMap);

			rightMap.addSource('isochrones-transit', {
				type: 'geojson',
				data: transitFiles[timeOfWeek],
			});
			rightMap.addSource('libraries-right', {
				type: 'geojson',
				data: DATA.libraries,
			});
			rightMap.addSource('ttc-lines', {
				type: 'geojson',
				data: DATA.ttcLines,
			});

			rightMap.addLayer({
				id: 'iso-fill',
				type: 'fill',
				source: 'isochrones-transit',
				paint: {
					'fill-color': ISOCHRONE_COLOR_EXPR,
					'fill-opacity': [
						'match', ['get', 'time_bucket'],
						'over_30',  0.85,
						'15_to_30', 0.85,
						'under_15', 0.85,
						0.2,
					],
					'fill-outline-color': 'transparent',
				},
			});

			rightMap.addLayer({
				id: 'ttc-line',
				type: 'line',
				source: 'ttc-lines',
				paint: TRANSIT_LINE_PAINT,
			});

			rightMap.addLayer({
				id: 'library-dots-right',
				type: 'circle',
				source: 'libraries-right',
				paint: LIBRARY_LAYER_PAINT,
			});

			addLibraryHoverPopup(rightMap, 'library-dots-right', rightPopup);

			rightMap.on('move', () => syncTo(rightMap, leftMap));
			resolveRight();
		});

		// Both maps fitted and legend fonts loaded (they set the legend heights) → lay out
		Promise.all([mapsLoaded, document.fonts.ready]).then(arrangeView);

		updateClip();

		window.addEventListener('mousemove', onMousemove);
		window.addEventListener('mouseup', onMouseup);
		window.addEventListener('touchmove', onMousemove);
		window.addEventListener('touchend', onMouseup);

		return () => {
			window.removeEventListener('mousemove', onMousemove);
			window.removeEventListener('mouseup', onMouseup);
			window.removeEventListener('touchmove', onMousemove);
			window.removeEventListener('touchend', onMouseup);
		};

	});

</script>



<div class="swipe-wrap" bind:this={swipeContainer}>

	<div class="map right-map" bind:this={rightContainer}></div>
	<div class="map left-map"  bind:this={leftContainer}></div>

	<div
		class="divider"
		style="left: {dividerPct}%"
		on:mousedown={onDividerMousedown}
		on:touchstart={onDividerMousedown}
		on:keydown={onDividerKeydown}
		role="slider"
		tabindex="0"
		aria-label="Drag or use arrow keys to compare maps"
		aria-valuenow={Math.round(dividerPct)}
		aria-valuemin="5"
		aria-valuemax="95"
	>
		<div class="divider-handle">&#8644;</div>
	</div>

	<!-- Left legend — variable dropdown, color scale, bar chart, library/transit -->
	<div class="legend-slot left-legend" bind:this={leftLegendEl}>
		<Legend
			horizontal
			title="% of population per census tract"
			colors={activeDemog.colors}
			breakLabels={activeDemog.breaks.map(b => `${b}%`)}
		>
			<div slot="header" class="dropdown-wrap">
				<label for="demog-select">Variable:</label>
				<select id="demog-select" on:change={(e) => setDemographic(demographics.find(d => d.id === e.target.value))}>
					{#each demographics as d}
						<option value={d.id}>{d.label}</option>
					{/each}
				</select>
			</div>

			<!-- Bar chart — hidden on mobile -->
			<div class="bar-rows">
				<div class="bar-row">
					<span class="bar-label">Walk + Transit</span>
					<div class="bar-track">
						<div class="bar" style="width:{transitBarW}%; background:{barColor};"></div>
					</div>
					<span class="bar-val">{activeDemog.transit} min</span>
				</div>
				<div class="bar-row">
					<span class="bar-label">Walking only</span>
					<div class="bar-track">
						<div class="bar" style="width:{walkBarW}%; background:{barColorLight};"></div>
					</div>
					<span class="bar-val">{activeDemog.walk} min</span>
				</div>
				<div class="chart-note">City avg — Transit: {CITY_AVG.transit} min · Walk: {CITY_AVG.walk} min</div>
			</div>
		</Legend>
	</div>

	<!-- Right legend — travel-mode heading, weekday/weekend/walking toggle, minutes scale
	     (Library / Transit key is shown once, in the left legend) -->
	<div class="legend-slot right-legend" bind:this={rightLegendEl}>
		<Legend
			horizontal
			showExtras={false}
			title="Minutes to Library"
			subtitle={timeLabel}
			colors={['#516082', '#5FA5C1', '#A2D7F2']}
			breakLabels={['15 min', '30 min']}
		>
			<div slot="lead" class="mode-control">
				<div class="mode-title">{modeTitle}</div>
				<div class="toggle">
					<button class:active={timeOfWeek === 'weekday'} on:click={() => setTimeOfWeek('weekday')}>Weekday</button>
					<button class:active={timeOfWeek === 'weekend'} on:click={() => setTimeOfWeek('weekend')}>Weekend</button>
					<button class:active={timeOfWeek === 'walk'}    on:click={() => setTimeOfWeek('walk')}>Walking</button>
				</div>
			</div>
		</Legend>
	</div>

</div>



<style>

	.swipe-wrap {
		position: relative;
		width: 100%;
		height: 580px;
		overflow: hidden;
		user-select: none;
	}

	.map {
		position: absolute;
		top: 0; left: 0;
		width: 100%;
		height: 100%;
	}

	.left-map  { z-index: 2; }
	.right-map { z-index: 1; }

	.divider {
		position: absolute;
		top: 0; bottom: 0;
		z-index: 10;
		width: 4px;
		background: white;
		box-shadow: 0 0 6px rgba(0,0,0,0.4);
		cursor: col-resize;
		transform: translateX(-50%);
	}

	.divider-handle {
		position: absolute;
		top: 50%;
		left: 50%;
		transform: translate(-50%, -50%);
		background: white;
		border-radius: 50%;
		width: 32px;
		height: 32px;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 18px;
		box-shadow: 0 0 6px rgba(0,0,0,0.3);
		cursor: col-resize;
	}

	/* ── Travel-mode heading + toggle (inside right legend)  */
	.mode-control {
		display: flex;
		flex-direction: column;
		align-items: flex-start;
		gap: 4px;
		pointer-events: auto;   /* Legend box itself is pointer-events: none */
	}

	.mode-title {
		font-family: 'TradeGothicBold', sans-serif;
		font-size: 14px;
	}

	.toggle {
		display: flex;
		gap: 3px;
		background: #f0f0f0;
		padding: 3px;
		border-radius: 6px;
	}

	.toggle button {
		padding: 3px 10px;
		border: none;
		border-radius: 4px;
		background: transparent;
		font-family: 'OpenSans', sans-serif;
		font-size: 12px;
		cursor: pointer;
		color: #333;
		transition: background 0.15s;
	}

	.toggle button:hover  { background: #e0e0e0; }
	.toggle button.active { background: #516082; color: white; }

	/* ── Dropdown (inside left legend)  */
	.dropdown-wrap {
		display: flex;
		align-items: center;
		gap: 5px;
		margin-bottom: 8px;
		font-size: 13px;
		pointer-events: auto;   /* Legend box itself is pointer-events: none */
	}

	.dropdown-wrap select {
		border: 1px solid #ccc;
		border-radius: 4px;
		padding: 2px 4px;
		font-size: 13px;
		cursor: pointer;
		min-width: 0;
		flex: 1;
	}

	/* ── Bar chart (inside left legend)  */

	.bar-row {
		display: flex;
		align-items: center;
		gap: 2px;
		margin-bottom: 3px;
	}

	.bar-label {
		font-size: 12px;
		font-weight: normal;
		color: #444;
		width: 88px;
		flex-shrink: 0;
	}

	.bar-track {
		width: 100px;
		flex-shrink: 1;     /* shrinks rather than overflowing when the legend is width-capped */
		min-width: 40px;
		background: #f0f0f0;
		height: 12px;
		border-radius: 1px;
		overflow: hidden;
	}

	.bar {
		height: 100%;
		border-radius: 2px;
		transition: width 0.3s ease, background 0.3s ease;
	}

	.bar-val {
		font-size: 12px;
		font-weight: normal;
		color: #333;
		width: 50px;
		flex-shrink: 0;
		padding-left: 4px;
	}

	.chart-note {
		font-size: 10px;
		color: #999;
		font-weight: normal;
		margin-top: 4px;
	}

	/* ── Legends  */
	.legend-slot {
		position: absolute;
		z-index: 10;
	}

	.left-legend  { top: 12px; left: 52px;  max-width: calc(100% - 52px - 440px); }
	.right-legend { top: 12px; right: 44px; }

	/* "Minutes to Library" title — 1px larger than the legend's default title size */
	.right-legend :global(.legend .legend-name) { font-size: 13px; }

	/* ── Tablet (≤1024px) — compact legends ── */
	@media (max-width: 1024px) {
		.swipe-wrap { height: 440px; }

		/* Bar chart — smaller */
		.bar-label  { font-size: 10px; width: 72px; }
		.bar-track  { width: 70px; height: 9px; }
		.bar-val    { font-size: 10px; width: 40px; }
		.chart-note { font-size: 9px; margin-top: 2px; }
		.bar-row    { margin-bottom: 2px; gap: 2px; }

		/* Travel-mode heading + toggle */
		.mode-title { font-size: 11px; }
		.right-legend :global(.legend .legend-name) { font-size: 11px; }
		.toggle button { padding: 2px 6px; font-size: 10px; }

		/* Dropdown */
		.dropdown-wrap { font-size: 11px; margin-bottom: 5px; }
		.dropdown-wrap select { font-size: 11px; max-width: 150px; }

		/* Legend positions (internal sizing handled by LegendStandalone.svelte) */
		/* Demographic legend across the top (between zoom buttons and the "i" button);
		   travel-time legend at the bottom right, above the scale bar */
		.left-legend  { top: 8px; left: 45px; max-width: calc(100% - 45px - 52px); }
		.right-legend { top: auto; bottom: 40px; right: 8px; }

		.divider-handle { width: 24px; height: 24px; font-size: 14px; }
	}

	/* ── Mobile (≤600px) */
	@media (max-width: 600px) {
    .swipe-wrap { height: 380px; }

    /* Dropdown — drop the label to save width */
    .dropdown-wrap label { display: none; }
    .dropdown-wrap select { max-width: 130px; }

    /* Not enough width for both legends across the top: demographic legend stays
       top left (zoom buttons are hidden, so it can sit in the corner) and the
       travel-time legend moves to the bottom right, above the scale bar */
    .left-legend  { top: 8px; left: 8px; max-width: calc(100% - 16px - 38px); }
    .right-legend { top: auto; bottom: 52px; right: 8px; max-width: calc(100% - 16px); }

    /* Hide zoom buttons */
    :global(.maplibregl-ctrl-top-left),
    :global(.maplibregl-ctrl-top-right) { display: none; }
}

</style>
