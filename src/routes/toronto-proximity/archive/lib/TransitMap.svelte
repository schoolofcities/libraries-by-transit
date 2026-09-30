<script>

	import { onMount, createEventDispatcher } from "svelte";
	import maplibregl from "maplibre-gl";
	import "maplibre-gl/dist/maplibre-gl.css";
	import { getStyle, MAP_OPTIONS, fitToToronto, LIBRARY_LAYER_PAINT,
	         TRANSIT_LINE_PAINT, ISOCHRONE_COLOR_EXPR, addLibraryHoverPopup } from './mapConfig.js';
	import Legend from './Legend.svelte';
	import { DATA } from '../../data/index.js';

	const dispatch = createEventDispatcher();

	export let map = null;

	let mapContainer;
	let showLegend = false;

	let timeOfWeek = 'weekday';

	const dataFiles = {
    weekday:  DATA.transitWeekday,
    weekend:  DATA.transitWeekend,
	};

	const timeLabels = {
		weekday: 'Tuesday, 10:00-10:30am',
		weekend: 'Saturday, 10:00-10:30am'
	};

	$: timeLabel = timeLabels[timeOfWeek];

	function setTimeOfWeek(val) {
		timeOfWeek = val;
		if (!map || !map.getSource('isochrones-transit')) return;
		map.getSource('isochrones-transit').setData(dataFiles[val]);
	}

	onMount(async () => {

		const style = await getStyle();

		showLegend = window.innerWidth >= 1025;

		const popup = new maplibregl.Popup({ closeButton: false, closeOnClick: false });

		map = new maplibregl.Map({
			container: mapContainer,
			style,
			...MAP_OPTIONS,
		});

		map.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'top-right');
		map.addControl(new maplibregl.ScaleControl({ unit: 'metric', maxWidth: 100 }), 'bottom-right');

		map.on('load', () => {

			fitToToronto(map);

			map.addSource('isochrones-transit', {
				type: 'geojson',
				data: dataFiles[timeOfWeek]
			});

			map.addSource('libraries-transit', {
				type: 'geojson',
				data: DATA.libraries
			});

			map.addSource('transit-lines', {
				type: 'geojson',
				data: DATA.ttcLines
			});

			map.addLayer({
				id: 'iso-transit-fill',
				type: 'fill',
				source: 'isochrones-transit',
				paint: {
					'fill-color': ISOCHRONE_COLOR_EXPR,
					'fill-opacity': 0.85,
					'fill-outline-color': 'transparent',
				},
			});

			map.on('click', 'iso-transit-fill', (e) => {
				const mins = e.features[0].properties.minutes;
				const label = mins >= 60 ? '60+ min' : `${Math.round(mins)} min`;
				new maplibregl.Popup()
					.setLngLat(e.lngLat)
					.setHTML(`<b>${label}</b> to nearest library`)
					.addTo(map);
			});

			map.on('mouseenter', 'iso-transit-fill', () => {
				map.getCanvas().style.cursor = 'pointer';
			});
			map.on('mouseleave', 'iso-transit-fill', () => {
				map.getCanvas().style.cursor = '';
			});

			map.addLayer({
				id: 'transit-line',
				type: 'line',
				source: 'transit-lines',
				paint: TRANSIT_LINE_PAINT,
			});

			map.addLayer({
				id: 'library-circles-transit',
				type: 'circle',
				source: 'libraries-transit',
				paint: LIBRARY_LAYER_PAINT,
			});

			addLibraryHoverPopup(map, 'library-circles-transit', popup);

			map.on('move', () => dispatch('move', map));

		});

	});

</script>



<div class="map-wrap">

	<div class="map-title">Walking + Transit</div>

	<div class="toggle">
		<button class:active={timeOfWeek === 'weekday'}        on:click={() => setTimeOfWeek('weekday')}>Weekday</button>
		<button class:active={timeOfWeek === 'weekend'}        on:click={() => setTimeOfWeek('weekend')}>Weekend</button>
	</div>

	<div class="map" bind:this={mapContainer}></div>

	{#if showLegend}
	<div class="legend-slot">
		<Legend
			title="Minutes to Library"
			subtitle={timeLabel}
			colors={['#C4A7C9', '#9865A1', '#6D247A']}
			breakLabels={['15 min', '30 min']}
		/>
	</div>
	{/if}

	<button class="legend-toggle" on:click={() => showLegend = !showLegend}>
		{showLegend ? 'Hide legend' : 'Show legend'}
	</button>

</div>



<style>

	.map-wrap {
		position: relative;
		width: 100%;
		height: 520px;
	}

	.map {
		width: 100%;
		height: 100%;
	}

	.map-title {
		position: absolute;
		top: 12px;
		left: 12px;
		z-index: 10;
		background: white;
		padding: 5px 12px;
		border-radius: 6px;
		font-family: 'TradeGothicBold', sans-serif;
		font-size: 13px;
		box-shadow: 0 2px 6px rgba(0,0,0,0.2);
	}

	.toggle {
		position: absolute;
		top: 10px;
		left: 50%;
		transform: translateX(-50%);
		z-index: 10;
		display: flex;
		gap: 4px;
		background: white;
		padding: 4px;
		border-radius: 8px;
		box-shadow: 0 2px 6px rgba(0,0,0,0.2);
	}

	.toggle button {
		padding: 4px 10px;
		border: none;
		border-radius: 5px;
		background: transparent;
		font-family: 'OpenSans', sans-serif;
		font-size: 13px;
		cursor: pointer;
		color: #333;
		transition: background 0.15s;
	}

	.toggle button:hover  { background: #f0f0f0; }
	.toggle button.active { background: #6D247A; color: white; }

	.legend-slot {
		position: absolute;
		bottom: 70px;
		right: 12px;
		z-index: 10;
	}

	/* Desktop — always show legend, hide toggle button */
	.legend-toggle { display: none; }

	@media (min-width: 1025px) {
		.legend-slot {
			bottom: 36px;
			display: block !important;
		}
	}

	/* Tablet and below — show toggle button, legend controlled by state */
	@media (max-width: 1024px) {
		.map-wrap { height: 400px; }

		.toggle {
			top: 38px;
			left: 12px;
			transform: none;
		}

		.legend-toggle {
			display: block;
			position: absolute;
			bottom: 36px;
			right: 12px;
			z-index: 11;
			background: white;
			border: 1px solid #ccc;
			border-radius: 5px;
			padding: 5px 12px;
			font-family: 'OpenSans', sans-serif;
			font-size: 11px;
			cursor: pointer;
			box-shadow: 1px 1px 3px rgba(0,0,0,0.15);
		}
	}

	@media (max-width: 600px) {
		.map-wrap { height: 320px; }
		.map-title { font-size: 11px; padding: 4px 8px; }
		.toggle button { font-size: 11px; padding: 3px 8px; }
	}

</style>
