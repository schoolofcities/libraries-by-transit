<script>

	import { onMount, createEventDispatcher } from "svelte";
	import maplibregl from "maplibre-gl";
	import "maplibre-gl/dist/maplibre-gl.css";
	import mapStyle from "../assets/map-style.json";

	const dispatch = createEventDispatcher();

	export let map = null;

	let mapContainer;

	let timeOfWeek = 'weekday';

	const dataFiles = {
		weekday: '/public-libraries/data/isochrones_transit_weekday.geojson',
		weekend: '/public-libraries/data/isochrones_transit_weekend.geojson',
	};

	const timeLabels = {
		weekday: 'Tuesday, 10am',
		weekend: 'Saturday, 10am'
	};

	$: timeLabel = timeLabels[timeOfWeek];

	function setTimeOfWeek(val) {
		timeOfWeek = val;
		if (!map || !map.getSource('isochrones-transit')) return;
		map.getSource('isochrones-transit').setData(dataFiles[val]);
	}

	onMount(() => {

		const popup = new maplibregl.Popup({ closeButton: false, closeOnClick: false });

		map = new maplibregl.Map({
			container: mapContainer,
			style: mapStyle,
			center: [-79.350000, 43.730000],
			zoom: 9.8,
			bearing: -17,
			dragRotate: false,
			touchPitch: false,
			minZoom: 9,
			maxZoom: 17,
			projection: "mercator",
			attributionControl: false,
		});

		map.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'top-right');
		map.addControl(new maplibregl.ScaleControl({ unit: 'metric', maxWidth: 100 }), 'bottom-right');

		map.on('load', () => {

			map.addSource('isochrones-transit', {
				type: 'geojson',
				data: dataFiles[timeOfWeek]
			});

			map.addSource('libraries-transit', {
				type: 'geojson',
				data: '/public-libraries/data/libraries.geojson'
			});

			map.addSource('transit-lines', {
				type: 'geojson',
				data: '/public-libraries/data/ttc_main_lines.geojson'
			});

			map.addLayer({
				id: 'iso-transit-fill',
				type: 'fill',
				source: 'isochrones-transit',
				paint: {
					'fill-color': '#6D247A',
					'fill-opacity': [
						'match', ['get', 'time_bucket'],
						'over_30',  0.9,
						'15_to_30', 0.4,
						'under_15', 0.2,
						0.2
					],
					'fill-outline-color': 'transparent',
				},
			});

			map.addLayer({
				id: 'transit-line',
				type: 'line',
				source: 'transit-lines',
				paint: {
					'line-color': '#000000',
					'line-opacity': 0.5,
					'line-width': 1.5,
				},
			});

			map.addLayer({
				id: 'library-circles-transit',
				type: 'circle',
				source: 'libraries-transit',
				paint: {
					'circle-color': '#015FC1',
					'circle-radius': 4,
					'circle-stroke-color': '#ffffff',
					'circle-stroke-width': 1.5,
				},
			});

			map.on('mouseenter', 'library-circles-transit', (e) => {
				map.getCanvas().style.cursor = 'pointer';
				const coords = e.features[0].geometry.coordinates.slice();
				const name = e.features[0].properties.BranchName ?? 'Library';
				popup.setLngLat(coords).setHTML(`<b>${name}</b>`).addTo(map);
			});

			map.on('mouseleave', 'library-circles-transit', () => {
				map.getCanvas().style.cursor = '';
				popup.remove();
			});

			// Dispatch move events for sync
			map.on('move', () => dispatch('move', map));

		});

	});

</script>



<div class="map-wrap">

	<div class="map-title">Walking + Transit</div>

	<div class="toggle">
		<button class:active={timeOfWeek === 'weekday'} on:click={() => setTimeOfWeek('weekday')}>
			Weekday
		</button>
		<button class:active={timeOfWeek === 'weekend'} on:click={() => setTimeOfWeek('weekend')}>
			Weekend
		</button>
	</div>

	<div class="map" bind:this={mapContainer}></div>

	<div class="legend">
		<b>Minutes to Library</b>
		<div class="legend-subtitle">{timeLabel}</div>
		<div class="legend-row"><div class="swatch" style="background:#6D247A; opacity:0.2;"></div> &lt;15 min</div>
		<div class="legend-row"><div class="swatch" style="background:#6D247A; opacity:0.4;"></div> 15–30 min</div>
		<div class="legend-row"><div class="swatch" style="background:#6D247A; opacity:0.9;"></div> 30+ min</div>
		<div class="legend-row"><div class="swatch circle" style="background:#015FC1;"></div> Library</div>
		<div class="legend-row"><div class="swatch line"></div> TTC rapid transit</div>
	</div>

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
		font-family: Arial, sans-serif;
		font-size: 13px;
		font-weight: bold;
		box-shadow: 0 2px 6px rgba(0,0,0,0.2);
	}

	.toggle {
		position: absolute;
		top: 12px;
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
		padding: 5px 14px;
		border: none;
		border-radius: 5px;
		background: transparent;
		font-family: Arial, sans-serif;
		font-size: 13px;
		cursor: pointer;
		color: #333;
		transition: background 0.15s;
	}

	.toggle button:hover  { background: #f0f0f0; }
	.toggle button.active { background: #6D247A; color: white; }

	.legend {
		position: absolute;
		bottom: 36px;
		right: 12px;
		z-index: 10;
		background: white;
		padding: 10px 12px;
		border: 1px solid #ccc;
		border-radius: 6px;
		font-family: Arial, sans-serif;
		font-size: 12px;
		box-shadow: 1px 1px 3px rgba(0,0,0,0.15);
		pointer-events: none;
	}

	.legend-subtitle {
		color: #666;
		font-size: 10px;
		margin: 2px 0 6px;
	}

	.legend-row {
		display: flex;
		align-items: center;
		gap: 6px;
		margin-top: 4px;
	}

	.swatch {
		width: 12px;
		height: 12px;
		flex-shrink: 0;
	}

	.swatch.circle { border-radius: 50%; }

	.swatch.line {
		height: 3px;
		background: #000;
		opacity: 0.5;
	}

</style>
