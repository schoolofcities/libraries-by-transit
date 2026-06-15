<script>

	import '../../assets/global-styles.css';
	import TransitMap from '../../lib/TransitMap.svelte';
	import WalkMap from '../../lib/WalkMap.svelte';
	import SwipeMap from '../../lib/SwipeMap.svelte';
	import StaticMaps from '../../lib/StaticMaps.svelte';

	let transitMap;
	let walkMap;
	let syncing = false;

	function syncMaps(source, target) {
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

	function onTransitMove(e) { syncMaps(e.detail, walkMap); }
	function onWalkMove(e)    { syncMaps(e.detail, transitMap); }

</script>



<main>

	<div class="text">
		<div class="title">
			<h1>Proximity to Toronto Public Libraries</h1>
			<p><a href="https://jamaps.github.io/about.html">Jeff Allen</a> /// May 2026</p>
		</div>
		<p>
			Comparing equity gaps in accessibility to Toronto Public Libraries across the city's populations
		</p>
	</div>

	<!-- Section 1: Side-by-side isochrone maps -->
	<div class="map-grid">
		<TransitMap bind:map={transitMap} on:move={onTransitMove}/>
		<WalkMap    bind:map={walkMap}    on:move={onWalkMove}/>
	</div>

	<div class="text">
		<p>
			The swiper map below illustrates census-tract aggregated demographic data that can be compared with the walking+transit isochrones. The averaged travel statistics per population group can also provide insight in the contribution of public transit to the library accessibility, as well as the city-wide context.
		</p>
		<p>
			Talk about the role of public transit in increasing accessibility and the general widespread network of libraries => minimal to no equity gaps.
		</p>
	</div>

	<div class="swipe-container">
		<SwipeMap/>
	</div>

	<div class="text">
		<p>
			<!-- analysis text -->
		</p>
	</div>

	

	<!-- Section 3: Accordion with static choropleth maps -->
	<StaticMaps/>

	<div class="text">
		<p>
			<!-- closing text -->
		</p>
	</div>

</main>



<style>

	.map-grid {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 12px;
		max-width: 1400px;
		margin: 0 auto;
		padding: 0 12px;
	}

	@media (max-width: 800px) {
		.map-grid { grid-template-columns: 1fr; gap: 8px; padding: 0 8px;}
	}

	.swipe-container {
    max-width: 1100px;
    margin: 0 auto;
    padding: 0 12px;
	}

	h1 {
    font-family: 'TradeGothicBold', Arial, sans-serif;
	}

	p, .text {
		font-family: 'SourceSerifPro', Georgia, serif;
	}

	a {
		font-family: 'SourceSerifPro', Georgia, serif;
	}

</style>
