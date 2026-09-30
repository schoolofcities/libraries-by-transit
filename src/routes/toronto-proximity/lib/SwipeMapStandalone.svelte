<script>

	import { onMount } from "svelte";
	import maplibregl from "maplibre-gl";
	import "maplibre-gl/dist/maplibre-gl.css";
	import { getStyle, MAP_OPTIONS, fitToToronto, LIBRARY_LAYER_PAINT,
	         TRANSIT_LINE_PAINT, ISOCHRONE_COLOR_EXPR, addLibraryHoverPopup } from './mapConfigStandalone.js';
	import { lighten } from './utils.js';
	import { DEMOGRAPHICS, CITY_AVG } from './demographics.js';
	import Legend from './LegendStandalone.svelte';
	import { DATA } from '../data/index.js';

	let leftContainer;
	let rightContainer;
	let leftMap;
	let rightMap;
	export let zoomOffset = 0;

	const demographics = DEMOGRAPHICS;
	const maxBarVal = 35;

	$: barColor      = activeDemog.colors[activeDemog.colors.length - 1];
	$: barColorLight = lighten(barColor);
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

	// Transit toggle 
	let timeOfWeek = 'weekday';

	const transitFiles = {
		weekday: DATA.transitWeekday,
		weekend: DATA.transitWeekend,
	};

	const timeLabels = {
		weekday: 'Tuesday, 10:00-10:30am',
		weekend: 'Saturday, 10:00-10:30am',
	};

	$: timeLabel = timeLabels[timeOfWeek];

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

		const style = await getStyle();

		const leftPopup  = new maplibregl.Popup({ closeButton: false, closeOnClick: false });
		const rightPopup = new maplibregl.Popup({ closeButton: false, closeOnClick: false });

		leftMap = new maplibregl.Map({ container: leftContainer, style, ...MAP_OPTIONS });
		leftMap.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'top-left');

		leftMap.on('load', () => {

			fitToToronto(leftMap); leftMap.setZoom(leftMap.getZoom() + zoomOffset);

			leftMap.addSource('census-tracts', {
				type: 'geojson',
				data: DATA.censusTracts,
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
		});

		// Right map
		rightMap = new maplibregl.Map({ container: rightContainer, style, ...MAP_OPTIONS });
		rightMap.addControl(new maplibregl.ScaleControl({ unit: 'metric', maxWidth: 100 }), 'bottom-right');

		rightMap.on('load', () => {

			fitToToronto(rightMap); rightMap.setZoom(rightMap.getZoom() + zoomOffset);

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
		});

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

	<!-- Left label — demographic heading + bar chart (hidden on small screens) -->
	<div class="map-label left-label">
		<div class="label-text">
			{activeDemog.label}
			<span class="label-sub">% of population per census tract</span>
		</div>
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
	</div>

	<!-- Right label — transit heading + weekday/weekend toggle -->
	<div class="map-label right-label">
		Walking + Transit
		<div class="toggle">
			<button class:active={timeOfWeek === 'weekday'} on:click={() => setTimeOfWeek('weekday')}>Weekday</button>
			<button class:active={timeOfWeek === 'weekend'} on:click={() => setTimeOfWeek('weekend')}>Weekend</button>
		</div>
	</div>

	<!-- Variable dropdown — centred at top -->
	<div class="dropdown-wrap">
		<label for="demog-select">Variable:</label>
		<select id="demog-select" on:change={(e) => setDemographic(demographics.find(d => d.id === e.target.value))}>
			{#each demographics as d}
				<option value={d.id}>{d.label}</option>
			{/each}
		</select>
	</div>

	<!-- Legends — hidden on small screens -->
	<div class="legend-slot left-legend">
		<Legend
			title={activeDemog.label}
			colors={activeDemog.colors}
			breakLabels={activeDemog.breaks.map(b => `${b}%`)}
		/>
	</div>

	<div class="legend-slot right-legend">
		<Legend
			title="Minutes to Library"
			subtitle={timeLabel}
			colors={['#516082', '#5FA5C1', '#A2D7F2']}
			breakLabels={['15 min', '30 min']}
		/>
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

	/* ── Divider ──────────────────────────────────────────────────────────── */
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

	/* ── Labels ───────────────────────────────────────────────────────────── */
	.map-label {
		position: absolute;
		top: 12px;
		z-index: 10;
		background: white;
		padding: 8px 12px;
		border-radius: 6px;
		font-family: 'OpenSans', sans-serif;
		font-size: 13px;
		box-shadow: 0 2px 6px rgba(0,0,0,0.2);
		pointer-events: none;
		max-width: 280px;
	}

	.left-label  { left: 52px; }

	.right-label {
		right: 44px;
		display: flex;
		flex-direction: column;
		align-items: flex-end;
		gap: 4px;
		pointer-events: all;
		font-family: 'TradeGothicBold', sans-serif;
	}

	.label-text {
		font-size: 13px;
		font-family: 'TradeGothicBold', sans-serif;
		margin-bottom: 6px;
	}

	.label-sub {
		font-size: 10px;
		font-weight: normal;
		color: #666;
		display: block;
	}

	/* ── Toggle ───────────────────────────────────────────────────────────── */
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
		font-size: 11px;
		cursor: pointer;
		color: #333;
		transition: background 0.15s;
	}

	.toggle button:hover  { background: #e0e0e0; }
	.toggle button.active { background: #516082; color: white; }

	/* ── Dropdown ─────────────────────────────────────────────────────────── */
	.dropdown-wrap {
		position: absolute;
		top: 12px;
		left: 50%;
		transform: translateX(-50%);
		z-index: 10;
		background: white;
		padding: 2px 5px;
		border-radius: 6px;
		font-family: 'OpenSans', sans-serif;
		font-size: 12px;
		box-shadow: 0 2px 6px rgba(0,0,0,0.2);
		display: flex;
		align-items: center;
		gap: 5px;
	}

	.dropdown-wrap select {
		border: 1px solid #ccc;
		border-radius: 4px;
		padding: 2px 4px;
		font-size: 12px;
		cursor: pointer;
	}

	/* ── Bar chart ────────────────────────────────────────────────────────── */
	.bar-row {
		display: flex;
		align-items: center;
		gap: 2px;
		margin-bottom: 3px;
	}

	.bar-label {
		font-size: 11px;
		font-weight: normal;
		color: #444;
		width: 80px;
		flex-shrink: 0;
	}

	.bar-track {
		width: 100px;
		flex-shrink: 0;
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
		font-size: 11px;
		font-weight: normal;
		color: #333;
		width: 46px;
		flex-shrink: 0;
	}

	.chart-note {
		font-size: 9px;
		color: #999;
		font-weight: normal;
		margin-top: 4px;
	}

	/* ── Legends ──────────────────────────────────────────────────────────── */
	.legend-slot {
		position: absolute;
		z-index: 10;
	}

	.left-legend  { bottom: 36px; left: 12px; }
	.right-legend { bottom: 36px; right: 12px; }

	/* ── Tablet (≤1024px) — hide bar chart, legends; stack dropdown below headings ── */
	@media (max-width: 1024px) {
		.swipe-wrap { height: 440px; }

		/* Left label — smaller, tighter */
		.left-label { 
			left: 45px; 
			max-width: 170px; 
			font-size: 10px; 
			padding: 4px 7px;
		}
		.label-text { font-size: 10px; margin-bottom: 3px; }
		.label-sub  { font-size: 8px; }

		/* Bar chart — smaller */
		.bar-label  { font-size: 9px; width: 65px; }
		.bar-track  { width: 70px; height: 9px; }
		.bar-val    { font-size: 9px; width: 36px; }
		.chart-note { font-size: 8px; margin-top: 2px; }
		.bar-row    { margin-bottom: 2px; gap: 2px; }

		/* Right label */
		.right-label { right: 6px; font-size: 10px; padding: 4px 7px; font-family: 'TradeGothicBold', sans-serif;}
		.toggle button { padding: 2px 6px; font-size: 9px; }

		/* Dropdown below toggle */
		.dropdown-wrap {
			bottom: auto;
			top: 12px;
			right: auto;
			left: 230px;
			transform: none;
			font-size: 10px;
			padding: 3px 7px;
		}
		.dropdown-wrap select { font-size: 10px; }

		/* Left legend — smaller position offset (internal sizing handled by Legend.svelte) */
		.left-legend { 
			bottom: 8px; 
			left: 6px; 
		}

		/* Hide right legend */
		.right-legend { display: none; }

		.divider-handle { width: 24px; height: 24px; font-size: 14px; }
	}

	/* ── Mobile (≤600px) ──────────────────────────────────────────────────── */
	@media (max-width: 600px) {
    .swipe-wrap { height: 380px; }

    /* Hide left label entirely */
    .left-label { display: none; }

    /* Move dropdown to top left */
    .dropdown-wrap {
        top: 12px;
        left: 12px;
        right: auto;
        bottom: auto;
        transform: none;
        background: white;
        box-shadow: 0 2px 6px rgba(0,0,0,0.2);
        padding: 4px 8px;
        font-size: 10px;
    }
    .dropdown-wrap label { display: none; }
    .dropdown-wrap select {
        font-size: 10px;
        border: 1px solid #ccc;
        border-radius: 4px;
        padding: 2px 4px;
        max-width: 130px;
    }

    /* Keep left legend bottom left */
    .left-legend { display: block; }

    /* Hide right legend */
    .right-legend { display: none; }

    /* Hide zoom buttons — these classes are injected by MapLibre at runtime,
       so :global() tells Svelte not to scope-check them against this file's markup */
    :global(.maplibregl-ctrl-top-left),
    :global(.maplibregl-ctrl-top-right) { display: none; }
}

</style>
