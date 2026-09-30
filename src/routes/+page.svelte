<script>

	import '../assets/global-styles.css';

	import { onMount } from "svelte";

	import maplibregl from "maplibre-gl";
	import "maplibre-gl/dist/maplibre-gl.css";

	import mapStyle from "../assets/map-style.json";

	let map;

	onMount(async () => {

		map = new maplibregl.Map({
			container: "map",
			style: mapStyle,
			center: [-79.386783, 43.670203],
			zoom: 13,
			bearing: 0,
			pitch: 0,
			scrollZoom: true,
			dragRotate: false,
			touchPitch: false,
			dragPan: true,
			touchZoomRotate: true,
			boxZoom: true,
			keyboard: true,
			doubleClickZoom: true,
			minZoom: 10,
			maxZoom: 17,
			projection: "mercator",
			attributionControl: false,
		});

		map.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'top-right');
		map.addControl(new maplibregl.ScaleControl({ unit: 'metric', maxWidth: 120 }), 'bottom-right');

	});

</script>



<svelte:head>

	<title>Toronto libraries proximity | School of Cities</title>

	<meta
		name="viewport"
		content="width=device-width, initial-scale=1, minimum-scale=1"
	/>

	<meta name="description" content="">
	<meta name="author" content="Jeff Allen">

</svelte:head>



<main>

	<div id="map"></div>

</main>



<style>

	#map {
		height: 100dvh;
		width: 100dvw;
		z-index: 0;
	}

</style>
