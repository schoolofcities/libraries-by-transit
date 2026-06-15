<script>

	import { onMount, createEventDispatcher } from "svelte";
	import maplibregl from "maplibre-gl";
	import "maplibre-gl/dist/maplibre-gl.css";

	const dispatch = createEventDispatcher();

	export let map = null;

	let mapContainer;
	let showLegend = false;

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

	async function getStyle() {
		const res = await fetch('https://tiles.stadiamaps.com/styles/alidade_smooth.json');
		const style = await res.json();
		style.layers = style.layers.filter(l => l.type !== 'symbol');
		return style;
	}

	onMount(async () => {

		const style = await getStyle();

		showLegend = window.innerWidth >= 1025;

		const popup = new maplibregl.Popup({ closeButton: false, closeOnClick: false });

		map = new maplibregl.Map({
			container: mapContainer,
			style: style,
			center: [-79.386783, 43.670203],
			zoom: 9,
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
			
			const bounds = window.innerWidth > 1024
				? [[-79.56, 43.60], [-79.13, 43.84]]
				: [[-79.62, 43.582], [-79.085, 43.858]];

			map.fitBounds(bounds, { padding: window.innerWidth > 1024 ? 0 : 24, bearing: -17, duration: 0 });


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
					'fill-color': [
						'match', ['get', 'time_bucket'],
						'under_15', '#C4A7C9',
						'15_to_30', '#9865A1',
						'over_30',  '#6D247A',
						'#6D247A'
					],
					'fill-opacity': 0.85,
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
					'line-width': 2.5,
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

	{#if showLegend}
	<div class="legend">
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
		font-family: 'TradeGothicBold', Arial, sans-serif;
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
		font-family: 'OpenSans', Arial, sans-serif;
		font-size: 13px;
		cursor: pointer;
		color: #333;
		transition: background 0.15s;
	}

	.toggle button:hover  { background: #f0f0f0; }
	.toggle button.active { background: #6D247A; color: white; }

	.legend {
		position: absolute;
		bottom: 70px;
		right: 12px;
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

	.legend-subtitle {
		color: #666;
		font-size: 10px;
		font-family: 'OpenSans', Arial, sans-serif;
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

	/* Desktop — always show legend, hide toggle button */
	.legend-toggle { display: none; }

	@media (min-width: 1025px) {
		.legend {
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
			font-family: 'OpenSans', Arial, sans-serif;
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

.color-segment { flex: 1; }

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

</style>
