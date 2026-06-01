<script>

	import '../../assets/global-styles.css';
	import TransitMap from '../../lib/TransitMap.svelte';
	import WalkMap from '../../lib/WalkMap.svelte';

	let transitMap;
	let walkMap;

	let syncing = false;

	function syncMaps(source, target) {
		if (!target || syncing) return;
		syncing = true;
		target.jumpTo({
			center: source.getCenter(),
			zoom:   source.getZoom(),
			bearing: source.getBearing(),
			pitch:  source.getPitch()
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
			<!-- intro text -->
		</p>
	</div>

	<div class="map-grid">
		<TransitMap bind:map={transitMap} on:move={onTransitMove}/>
		<WalkMap    bind:map={walkMap}    on:move={onWalkMove}/>
	</div>

	<div class="text">
		<p>
			<!-- analysis text -->
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
		.map-grid { grid-template-columns: 1fr; }
	}

</style>
