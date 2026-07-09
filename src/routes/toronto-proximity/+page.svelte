<script>

	import '../../assets/global-styles.css';
	import TransitMap from '../../lib/TransitMap.svelte';
	import WalkMap from '../../lib/WalkMap.svelte';
	import SwipeMap from '../../lib/SwipeMap.svelte';
	import StaticMaps from '../../lib/StaticMaps.svelte';
	import DotPlot from '../../lib/DotPlot.svelte';

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
			<h1>Is your local library close enough?</h1>
			<h3>Comparing equity gaps in accessibility to Toronto Public Libraries across the city's equity-seeking groups</h3>
			<p><a href="https://jamaps.github.io/about.html">Jeff Allen</a> & <a href="https://www.linkedin.com/in/polina-gorn-b2a1b8284/">Polina Gorn</a> /// July 2026</p>
		</div>
		
	</div>

	<div class="text">
		<p>Spatial access to public libraries matters: proximity predicts visits and borrowing, but access can vary across travel modes and population groups. 
		In the 21st century, the role of libraries has shifted significantly: nowadays, in the Canadian context, the libraries have significantly expanded their programming to serve vulnerable populations, including individuals experiencing homelessness, recent immigrants, seniors, etc. 
		Therefore, library access among equity-seeking population groups is crucial. </p>
		<p>
		We analyze data in the City of Toronto, specifically asking two questions:

		<p> <b>1. Coverage:</b> How does minimum travel time to the nearest library branch vary across Toronto by mode (walk, weekday transit, Saturday transit)? </p>
		<p> <b> 2. Equity: </b> How do those travel times vary across different population groups that often have specific needs for library services and programs? </p>
	</div>

	<div class="text">
		<h3>Methods</h3>
		<p><b>Data.</b> 
		<li> TPL branch points (n = 101, retrieved from Toronto Open Data, March 2026).</li>

		<li> 200 metre hexagon grid.</li>

		<li> 2021 Census Dissemination Area (DA) level attributes from Statistics Canada (population density, first generation immigrants, residents aged 0–14, residents aged 65+, low-income households (after–tax income under $30,000), visible minorities) </li>
		
		<li> OpenStreetMap data (extracted April 2026) for the street and active-transport network</li>
		
		<li> TTC GTFS feed dated 2026-05-23 for transit schedules. </li>
		</p>

		<p><b>Network Analysis.</b> 
		Travel times computed in Python with the <b>r5py</b> package from the centroid of each cell in a 200 metre hex grid covering the City of Toronto boundary.</p>
		<p>Three scenarios:</p>
		<li>Walk: 3.6 km/h, maximum 60 minutes</li>
		<li>Weekday transit: departure window Tuesday 2026-06-8 10:00–10:30, maximum 60 minutes</li>
		<li>Saturday transit: departure window Saturday 2026-06-13 10:00–10:30, maximum 60 minutes</li>
		<p>The isochrones show the significant improvement of library accessibility with the TTC network. On foot, 35% of residents can access the nearest library within 15 minutes, with 21% of the population requiring more than 30 minutes to reach the closest library. When transit is included, the share of residents unable to access a library within 30 minutes falls to 5%, and roughly 95% of the population can reach a library branch in under half an hour. Mean walk-plus-transit time drops to 16.8 minutes, saving about 4 minutes or 19% of travel time relative to walking.</p>
		<br>
		<br>
	</div>

	<!-- Section 1: Side-by-side isochrone maps -->
	<div class="map-grid">
		<TransitMap bind:map={transitMap} on:move={onTransitMove}/>
		<WalkMap    bind:map={walkMap}    on:move={onWalkMove}/>
	</div>

	<div class="text">
		<p>
			The swiper map below allows to explore the overlay of census-tract aggregated demographic data with the walking+transit isochrones.
			Based on the choropleth maps (that can all be explored in the dropdown section below the swiper map), census tracts with the highest rates of visible minority, immigrant, and low-income populations concentrate in the inner suburbs, which are simultaneously less dense areas of the city. 
			Nevertheless, the fringes of the inner suburbs that do experience high percentage of the aforementioned populations also have lower rates of library access. 
		</p>
	</div>

	<!-- Section 2: Swiper map -->
	<div class="swipe-container">
		<SwipeMap/>
	</div>	
	<br>

	<!-- Section 3: Accordion with static choropleth maps -->
	<StaticMaps/>

	<div class="text">
		<p>
		Library access is broadly equitable across demographic groups. Population-weighted mean walk-plus-transit times range only from 16.9 to 17.3 minutes across all groups, and walking-only means from 20.9 to 21.8 minutes — deviating from the citywide averages of 16.9 and 20.9 minutes by at most half a minute by transit and one minute on foot. Every equity-seeking group sits marginally above the citywide average, with visible minorities and seniors showing the largest gaps. Across all groups, transit reduces travel time by approximately four minutes relative to walking, underscoring public transit's role in equalizing library access across the city.
		</p>
	</div>

	<div class="text">
    	<DotPlot/>
	</div>

	<div class="text">
	<p> Future directions for developing this project may involve factoring in the programming and services provided in each library branch. Currently, the study looks into generalized library access, without accounting for the types of services each branch provides, and therefore the population groups it may attract. Filtering through the libraries that have programming catered to the needs of a specific population group can create a more nuanced picture of access to library services. </p>
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
