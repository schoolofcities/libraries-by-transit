<script>

	import { onMount } from "svelte";
	import maplibregl from "maplibre-gl";
	import "maplibre-gl/dist/maplibre-gl.css";

	let leftContainer;
	let rightContainer;
	let leftMap;
	let rightMap;

	const demographics = [
		{ id: 'visible_minority_pct',     label: 'Visible Minority',
		colors: ['#F0E9F1','#C4A7C9','#9865A1','#6D247A'],
		breaks: [31.4, 52.1, 74.4], transit: 16.9, walk: 21.7 },
		{ id: 'low_income_pct',           label: 'Low Income',
		colors: ['#FBECEA','#F1B5AD','#E67D70','#DC4633'],
		breaks: [28.0, 34.1, 37.8], transit: 16.5, walk: 20.9 },
		{ id: 'recent_immigrants_pct',    label: 'Recent Immigrants',
		colors: ['#E5F2F5','#99CBDA','#4CA5BE','#007FA3'],
		breaks: [3.2, 5.6, 8.3], transit: 16.1, walk: 20.5 },
		{ id: 'first_gen_immigrants_pct', label: 'First Gen. Immigrants',
		colors: ['#E5F5F3','#99D9CF','#4CBDAC','#00A189'],
		breaks: [37.6, 52.9, 63.3], transit: 16.7, walk: 21.4 },
		{ id: 'seniors_pct',              label: 'Seniors (65+)',
		colors: ['#E8EBEF','#A5AFC1','#617393','#1E3765'],
		breaks: [14.1, 17.0, 20.4], transit: 16.8, walk: 21.4 },
		{ id: 'children_pct',             label: 'Children (0–14)',
		colors: ['#F3F8EA','#D1E5AB','#AFD26C','#8DBF2E'],
		breaks: [11.7, 14.1, 16.3], transit: 16.7, walk: 21.1 },
	];

	const totalTransit = 16.4;
	const totalWalk    = 20.7;
	const maxBarVal    = 26;

	function lighten(hex) {
		const r = parseInt(hex.slice(1,3), 16);
		const g = parseInt(hex.slice(3,5), 16);
		const b = parseInt(hex.slice(5,7), 16);
		const mix = (c) => Math.round(255 + (c - 255) * 0.4);
		return `rgb(${mix(r)},${mix(g)},${mix(b)})`;
	}

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

	// ── Transit toggle ─────────────────────────────────────────────────────
	let timeOfWeek = 'weekday';

	const transitFiles = {
		weekday: '/public-libraries/data/isochrones_transit_weekday.geojson',
		weekend: '/public-libraries/data/isochrones_transit_weekend.geojson',
	};

	const timeLabels = {
		weekday: 'Tuesday, 10am',
		weekend: 'Saturday, 10am',
	};

	$: timeLabel = timeLabels[timeOfWeek];

	function setTimeOfWeek(val) {
		timeOfWeek = val;
		if (rightMap && rightMap.getSource('isochrones-transit')) {
			rightMap.getSource('isochrones-transit').setData(transitFiles[val]);
		}
	}

	// ── Swipe divider ──────────────────────────────────────────────────────
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

	function updateClip() {
		if (!leftContainer) return;
		leftContainer.style.clipPath = `inset(0 ${100 - dividerPct}% 0 0)`;
	}

	// ── Map sync ───────────────────────────────────────────────────────────
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

	async function getStyle() {
		const res = await fetch('https://tiles.stadiamaps.com/styles/alidade_smooth.json');
		const style = await res.json();
		style.layers = style.layers.filter(l => l.type !== 'symbol');
		return style;
	}

	onMount(async () => {

		const style = await getStyle();

		const sharedOptions = {
			style: style,
			center: [-79.386783, 43.670203],
			zoom: 9,
			dragRotate: false,
			touchPitch: false,
			minZoom: 9,
			maxZoom: 17,
			projection: 'mercator',
			attributionControl: false,
		};

		const isPhone = window.innerWidth <= 600;
		const isTablet = window.innerWidth > 600 && window.innerWidth <= 1024;

		const bounds = isTablet 
			? [[-79.60, 43.59], [-79.12, 43.85]]  // tighter for iPad
			: [[-79.62, 43.582], [-79.085, 43.858]];  // standard

		const leftPopup  = new maplibregl.Popup({ closeButton: false, closeOnClick: false });
		const rightPopup = new maplibregl.Popup({ closeButton: false, closeOnClick: false });

		leftMap = new maplibregl.Map({ container: leftContainer, ...sharedOptions });
		leftMap.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'top-left');

		leftMap.on('load', () => {

			const bounds = window.innerWidth > 1024
    ? [[-79.56, 43.60], [-79.13, 43.84]]
    : [[-79.62, 43.582], [-79.085, 43.858]];

leftMap.fitBounds(bounds, { padding: window.innerWidth > 1024 ? 0 : 24, bearing: -17, duration: 0 });

			leftMap.fitBounds(
				bounds, { padding: isPhone ? 24 : 3, bearing: -17, duration: 0});

			leftMap.addSource('census-tracts', {
				type: 'geojson',
				data: '/public-libraries/data/census_tracts_demographics.geojson',
			});
			leftMap.addSource('libraries-left', {
				type: 'geojson',
				data: '/public-libraries/data/libraries.geojson',
			});
			leftMap.addSource('transit-lines-left', {
				type: 'geojson',
				data: '/public-libraries/data/ttc_main_lines.geojson'
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
				paint: { 'line-color': '#000', 'line-opacity': 0.7, 'line-width': 2 },
			});

			leftMap.addLayer({
				id: 'library-dots-left',
				type: 'circle',
				source: 'libraries-left',
				paint: {
					'circle-color': '#015FC1',
					'circle-radius': 4,
					'circle-stroke-color': '#fff',
					'circle-stroke-width': 1.5,
				},
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

		// ── Right map ─────────────────────────────────────────────────────
		rightMap = new maplibregl.Map({ container: rightContainer, ...sharedOptions });
		rightMap.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'top-right');
		rightMap.addControl(new maplibregl.ScaleControl({ unit: 'metric', maxWidth: 100 }), 'bottom-right');

		rightMap.on('load', () => {

			const bounds = window.innerWidth > 1024
    ? [[-79.56, 43.60], [-79.13, 43.84]]
    : [[-79.62, 43.582], [-79.085, 43.858]];

leftMap.fitBounds(bounds, { padding: window.innerWidth > 1024 ? 0 : 24, bearing: -17, duration: 0 });

			rightMap.fitBounds(
				bounds, { padding: isPhone ? 24 : 3, bearing: -17, duration: 0});

			rightMap.addSource('isochrones-transit', {
				type: 'geojson',
				data: transitFiles[timeOfWeek],
			});
			rightMap.addSource('libraries-right', {
				type: 'geojson',
				data: '/public-libraries/data/libraries.geojson',
			});
			rightMap.addSource('ttc-lines', {
				type: 'geojson',
				data: '/public-libraries/data/ttc_main_lines.geojson',
			});

			rightMap.addLayer({
				id: 'iso-fill',
				type: 'fill',
				source: 'isochrones-transit',
				paint: {
					'fill-color': '#6D247A',
					'fill-opacity': [
						'match', ['get', 'time_bucket'],
						'over_30',  0.9,
						'15_to_30', 0.4,
						'under_15', 0.2,
						0.2,
					],
					'fill-outline-color': 'transparent',
				},
			});

			rightMap.addLayer({
				id: 'ttc-line',
				type: 'line',
				source: 'ttc-lines',
				paint: { 'line-color': '#000', 'line-opacity': 0.7, 'line-width': 2 },
			});

			rightMap.addLayer({
				id: 'library-dots-right',
				type: 'circle',
				source: 'libraries-right',
				paint: {
					'circle-color': '#015FC1',
					'circle-radius': 4,
					'circle-stroke-color': '#fff',
					'circle-stroke-width': 1.5,
				},
			});

			rightMap.on('mouseenter', 'library-dots-right', (e) => {
				rightMap.getCanvas().style.cursor = 'pointer';
				const name = e.features[0].properties.BranchName ?? 'Library';
				rightPopup.setLngLat(e.features[0].geometry.coordinates.slice()).setHTML(`<b>${name}</b>`).addTo(rightMap);
			});
			rightMap.on('mouseleave', 'library-dots-right', () => {
				rightMap.getCanvas().style.cursor = '';
				rightPopup.remove();
			});

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
		role="separator"
		aria-label="Drag to compare maps"
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
			<div class="chart-note">City avg — Transit: {totalTransit} min · Walk: {totalWalk} min</div>
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
	<div class="legend left-legend">
		<div class="legend-name">{activeDemog.label}</div>
		<div class="color-bar">
			{#each activeDemog.colors as color}
				<div class="color-segment" style="background:{color};"></div>
			{/each}
		</div>
		<div class="break-labels">
			<span></span>
			{#each activeDemog.breaks as brk}
				<span>{brk}%</span>
			{/each}
			<span></span>
		</div>
		<div class="legend-extras">
			<div class="legend-item">
				<div class="swatch circle" style="background:#015FC1;"></div>
				<span>Library</span>
			</div>
			<div class="legend-item">
				<div class="swatch line"></div>
				<span>Major Transit Lines</span>
			</div>
		</div>
	</div>

<div class="legend right-legend">
    <div class="legend-name">Minutes to Library</div>
    <div class="legend-subtitle">{timeLabel}</div>
    <div class="color-bar">
        <div class="color-segment" style="background:#C4A7C9;"></div>
        <div class="color-segment" style="background:#9865A1;"></div>
        <div class="color-segment" style="background:#6D247A;"></div>
    </div>
    <div class="break-labels">
        <span></span>
        <span>15 min</span>
        <span>30 min</span>
        <span></span>
    </div>
    <div class="legend-extras">
        <div class="legend-item">
            <div class="swatch circle" style="background:#015FC1;"></div>
            <span>Library</span>
        </div>
        <div class="legend-item">
            <div class="swatch line"></div>
            <span>Major Transit Lines</span>
        </div>
    </div>
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
		font-family: 'OpenSans', Arial, sans-serif;
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
		font-family: 'TradeGothicBold', Arial, sans-serif;
	}

	.label-text {
		font-size: 13px;
		font-family: 'TradeGothicBold', Arial, sans-serif;
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
		font-family: 'OpenSans', Arial, sans-serif;
		font-size: 11px;
		cursor: pointer;
		color: #333;
		transition: background 0.15s;
	}

	.toggle button:hover  { background: #e0e0e0; }
	.toggle button.active { background: #6D247A; color: white; }

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
		font-family: 'OpenSans', Arial, sans-serif;
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
	.legend {
		position: absolute;
		z-index: 10;
		background: white;
		padding: 10px 12px;
		border: 1px solid #ccc;
		border-radius: 6px;
		font-family: 'OpenSans', Arial, sans-serif;
		font-size: 12px;
		box-shadow: 1px 1px 3px rgba(0,0,0,0.15);
		pointer-events: none;
	}

	.left-legend  { bottom: 36px; left: 12px; }
	.right-legend { bottom: 36px; right: 12px; }

	.legend-title    { font-family: 'TradeGothicBold', Arial, sans-serif; margin-bottom: 2px; font-size: 11px; }
	.legend-subtitle { color: #666; font-size: 10px; margin: 0 0 6px; }

	.legend-row {
		display: flex;
		flex-direction: row;
		align-items: center;
		gap: 10px;
		flex-wrap: wrap;
	}

.legend-name {
    font-family: 'TradeGothicBold', Arial, sans-serif;
    font-size: 11px;
    margin-bottom: 4px;
}

.color-bar {
    display: flex;
    height: 12px;
    border-radius: 2px;
    overflow: hidden;
    width: 160px;
}

.color-segment {
    flex: 1;
}

.break-labels {
    display: flex;
    justify-content: space-between;
    width: 160px;
    font-size: 9px;
    color: #444;
    margin-top: 2px;
    margin-bottom: 6px;
}

.legend-extras {
    display: flex;
    gap: 10px;
    align-items: center;
}

.legend-item {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 11px;
}

	.swatch {
		width: 12px;
		height: 12px;
		flex-shrink: 0;
		border: 1px solid rgba(0,0,0,0.1);
	}

	.swatch.circle {
		border-radius: 50%;
		border: 1.5px solid white;
		outline: 1px solid #ccc;
	}

	.swatch.line {
		height: 3px;
		background: #000;
		opacity: 0.5;
		border: none;
	}

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
		.right-label { right: 6px; font-size: 10px; padding: 4px 7px; font-family: 'TradeGothicBold', Arial, sans-serif;}
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

		/* Left legend — smaller */
		.left-legend { 
			bottom: 8px; 
			left: 6px; 
			padding: 6px 8px;
			font-size: 10px;
		}
		.color-bar   { width: 120px; height: 9px; }
		.break-labels { width: 120px; font-size: 8px; }
		.legend-name { font-size: 9px; margin-bottom: 2px; }
		.legend-item { font-size: 9px; }
		.swatch      { width: 9px; height: 9px; }

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

    /* Hide zoom buttons */
    .maplibregl-ctrl-top-left,
    .maplibregl-ctrl-top-right { display: none; }
}

</style>
