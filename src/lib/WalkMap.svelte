<script>

	import { onMount, createEventDispatcher } from "svelte";
	import maplibregl from "maplibre-gl";
	import "maplibre-gl/dist/maplibre-gl.css";
	import { getStyle, MAP_OPTIONS, fitToToronto, LIBRARY_LAYER_PAINT,
	         TRANSIT_LINE_PAINT, ISOCHRONE_COLOR_EXPR, addLibraryHoverPopup } from './mapConfig.js';
	import Legend from './Legend.svelte';

	const dispatch = createEventDispatcher();

	export let map = null;

	let mapContainer;
	let showLegend = false;

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

			map.addSource('isochrones-walk', {
				type: 'geojson',
				data: '/public-libraries/data/isochrones_walk.geojson'
			});

			map.on('click', 'iso-walk-fill', (e) => {  
				const mins = e.features[0].properties.minutes;
				const label = mins >= 60 ? '60+ min' : `${Math.round(mins)} min`;
				new maplibregl.Popup()
					.setLngLat(e.lngLat)
        			.setHTML(`<b>${label}</b> to nearest library`)					
					.addTo(map);
			});

			map.on('mouseenter', 'iso-walk-fill', () => {
				map.getCanvas().style.cursor = 'pointer';
			});
			map.on('mouseleave', 'iso-walk-fill', () => {
				map.getCanvas().style.cursor = '';
			});

			map.addSource('libraries', {
				type: 'geojson',
				data: '/public-libraries/data/libraries.geojson'
			});

			map.addSource('transit-lines', {
				type: 'geojson',
				data: '/public-libraries/data/ttc_main_lines.geojson'
			});

			map.addLayer({
				id: 'iso-walk-fill',
				type: 'fill',
				source: 'isochrones-walk',
				paint: {
					'fill-color': ISOCHRONE_COLOR_EXPR,
					'fill-opacity': 0.85,
					'fill-outline-color': 'transparent',
				},
			});

			map.addLayer({
				id: 'transit-line',
				type: 'line',
				source: 'transit-lines',
				paint: TRANSIT_LINE_PAINT,
			});

			map.addLayer({
				id: 'library-circles-walk',
				type: 'circle',
				source: 'libraries',
				paint: LIBRARY_LAYER_PAINT,
			});

			addLibraryHoverPopup(map, 'library-circles-walk', popup);

			map.on('move', () => dispatch('move', map));

		});

	});

</script>



<div class="map-wrap">

	<div class="map-title">Walking</div>

	<div class="map" bind:this={mapContainer}></div>

	{#if showLegend}
	<div class="legend-slot">
		<Legend
			title="Minutes to Library"
			colors={['#C4A7C9', '#9865A1', '#6D247A']}
			breakLabels={['15 min', '30 min']}
		/>
	</div>
	{/if}

	<!-- Only shown on tablet/mobile -->
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

	.legend-slot {
		position: absolute;
		bottom: 36px;
		right: 12px;
		z-index: 10;
	}

	/* Hide toggle on desktop — legend always visible */
	.legend-toggle { display: none; }

	/* Tablet and below — show toggle button, legend controlled by state */
	@media (max-width: 1024px) {
		.map-wrap { height: 400px; }

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

		/* When legend is shown, push toggle button above it */
		.legend-slot { bottom: 70px; }
	}

	@media (max-width: 600px) {
		.map-wrap { height: 320px; }
		.map-title { font-size: 11px; padding: 4px 8px; }
	}

</style>
