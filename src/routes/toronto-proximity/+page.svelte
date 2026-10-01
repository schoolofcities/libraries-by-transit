<script>
	import '../../assets/global-styles.css';
	import PasswordGate from '$lib/PasswordGate.svelte';
	import SwipeMap from './lib/SwipeMapStandalone.svelte';

	let showInfo = true;

	const w = typeof window !== 'undefined' ? window.innerWidth : 1440;
	const h = typeof window !== 'undefined' ? window.innerHeight : 900;
	const isTabletOrPhone = w <= 1024 || (w <= 1100 && h > w);
	const isPortrait = h > w;
	const isShortLandscape = !isPortrait && h <= 500;   // phones held sideways

	// Portrait screens are width-limited, so any extra zoom crops the east/west ends
	// of the city; landscape screens have room to spare at the sides.
	const zoomOffset = isPortrait || isShortLandscape ? 0 : (isTabletOrPhone ? 0.3 : 0.45);
	// Shift the city down so it isn't hidden behind the legends along the top
	const panOffset = isShortLandscape ? 30 : 60;
</script>

<PasswordGate />

<svelte:head>
	<title>Library access swipe map | School of Cities</title>
</svelte:head>

<svelte:window on:keydown={(e) => { if (e.key === 'Escape') showInfo = false; }} />

<main class="swipe-page">
	<SwipeMap {zoomOffset} {panOffset}/>

	<button class="info-btn" aria-label="About this map" on:click={() => (showInfo = true)}>i</button>

	{#if showInfo}
		<!-- svelte-ignore a11y_click_events_have_key_events a11y_no_static_element_interactions -->
		<div class="backdrop" on:click|self={() => (showInfo = false)}>
			<div class="info-card" role="dialog" aria-modal="true" aria-labelledby="info-title">
				<button class="close-btn" aria-label="Close" on:click={() => (showInfo = false)}>&times;</button>
				<h2 id="info-title">About this map</h2>
				<p>This map is part of a School of Cities research project on mapping public transit and pedestrian accessibility to public libraries in Toronto. This interactive map allows to explore the overlay of census-tract aggregated demographic data with the walking+transit isochrones.</p>
				<p class="subhead">How to use the map:</p>
				<ul>
					<li><b>Drag the slider</b> to compare the demographic data on the left with travel time to the nearest library on the right.</li>
					<li>Use the <b>Variable</b> menu at the top to switch between population groups, and the <b>Weekday/Weekend</b> buttons to change the transit schedule, or <b>Walking</b> to see travel times on foot only.</li>
				</ul>
				<p class="phone-note">If you are viewing this webpage from your phone, it is highly advised to explore the data in landscape, or on larger screens (tablets/laptops).</p>
				<p>If you are interested to learn more about the research and findings, <a href="https://schoolofcities.github.io/posts/spatial-access-to-public-libraries-toronto/" target="_blank" rel="noopener">read the study</a>.</p>
				<button class="ok-btn" on:click={() => (showInfo = false)}>Explore the map</button>
			</div>
		</div>
	{/if}
</main>

<style>
	/* Pinned to the visible screen so the page itself can never scroll: both legend
	   corners stay in view even as mobile browser toolbars show/hide */
	.swipe-page {
		position: fixed;
		inset: 0;
		overflow: hidden;
		overscroll-behavior: none;
	}

	.swipe-page :global(.swipe-wrap) {
		height: 100%;
	}

	.swipe-page :global(.bar-val) {
		width: auto;
		white-space: nowrap;
	}

	.info-btn, .backdrop {
		font-family: 'OpenSans', sans-serif;
	}

	.info-btn, .info-card h2, .info-card .subhead, .info-card b, .info-card a {
		font-family: 'OpenSansBold', sans-serif;
		font-weight: normal;
	}

	.info-btn {
		position: absolute;
		top: 12px;
		right: 8px;
		z-index: 20;
		width: 28px;
		height: 28px;
		border-radius: 50%;
		border: none;
		background: #516082;
		color: white;
		font-size: 15px;
		cursor: pointer;
		box-shadow: 0 2px 6px rgba(0,0,0,0.3);
	}
	.info-btn:hover { background: #3f4c6b; }

	.backdrop {
		position: fixed;
		inset: 0;
		z-index: 100;
		background: rgba(0,0,0,0.35);
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 16px;
	}

	.info-card {
		position: relative;
		box-sizing: border-box;   /* so max-height includes the padding and the card never exceeds the screen */
		background: white;
		max-width: 480px;
		max-height: 100%;         /* of the backdrop's padded area, i.e. the visible screen minus 16px each side */
		overflow-y: auto;
		padding: 24px 28px 20px;
		border-radius: 8px;
		box-shadow: 0 4px 20px rgba(0,0,0,0.3);
		font-size: 14px;
		line-height: 1.55;
		color: #1a1a1a;
	}

	.info-card h2 {
		margin: 0 0 10px;
		font-size: 19px;
	}

	.info-card p, .info-card li {
		font-family: 'OpenSans', sans-serif;
		font-size: 14px;
		line-height: 1.55;
		color: #1a1a1a;
		padding: 0;
	}

	.info-card p {
		margin: 0 0 16px;
	}

	.info-card .subhead {
		margin-bottom: 4px;
	}

	.info-card ul {
		margin: 0 0 16px;
		padding-left: 20px;
	}

	.info-card li { margin-bottom: 6px; }

	.info-card a { color: #516082; }

	.close-btn {
		position: absolute;
		top: 8px;
		right: 10px;
		border: none;
		background: none;
		font-size: 22px;
		line-height: 1;
		cursor: pointer;
		color: #666;
	}

	.ok-btn {
		border: none;
		border-radius: 4px;
		padding: 7px 14px;
		background: #516082;
		color: white;
		font-family: 'OpenSans', sans-serif;
		font-size: 13px;
		cursor: pointer;
	}
	.ok-btn:hover { background: #3f4c6b; }
	/* ── Bigger controls on tablets and phones*/

	/* Tablets, small laptops and phones held sideways (601–1024px), plus large upright tablets up to 1100px (iPad Pro, Surface Pro) */
	@media (max-width: 1024px), (max-width: 1100px) and (orientation: portrait) {
		/* Variable menu (inside the demographic legend) */
		main.swipe-page :global(.dropdown-wrap) { font-size: 14px; }
		main.swipe-page :global(.dropdown-wrap select) {
			font-size: 15px;
			padding: 4px 6px;
		}
		main.swipe-page :global(.bar-label)  { font-size: 13px; width: 98px; }
		main.swipe-page :global(.bar-track)  { width: 110px; height: 12px; }
		main.swipe-page :global(.bar-val)    { font-size: 13px; }
		main.swipe-page :global(.chart-note) { font-size: 11px; margin-top: 4px; }
		main.swipe-page :global(.bar-row)    { margin-bottom: 4px; gap: 4px; }

		/* Travel-mode heading and Weekday/Weekend/Walking toggle (inside the travel-time legend) */
		main.swipe-page :global(.mode-title) { font-size: 16px; }
		main.swipe-page :global(.mode-control) { gap: 6px; }
		main.swipe-page :global(.toggle button) {
			font-size: 14px;
			padding: 7px 14px;
		}

		/* Legends */
		main.swipe-page :global(.legend)          { padding: 10px 12px; }
		main.swipe-page :global(.legend-name)     { font-size: 14px; margin-bottom: 4px; }
		main.swipe-page :global(.right-legend .legend-name) { font-size: 15px; }
		main.swipe-page :global(.legend-subtitle) { font-size: 13px; }
		main.swipe-page :global(.color-bar)       { width: 170px; height: 13px; }
		main.swipe-page :global(.break-labels)    { width: 170px; font-size: 12px; }
		main.swipe-page :global(.legend-item)     { font-size: 13px; }
		main.swipe-page :global(.swatch)          { width: 12px; height: 12px; }
		main.swipe-page :global(.swatch.line)     { height: 3px; }
		/* Demographic legend across the top; travel-time legend at the bottom right */
		main.swipe-page :global(.left-legend)     { top: 12px; left: 52px; max-width: calc(100% - 52px - 52px); }
		main.swipe-page :global(.right-legend)    { top: auto; bottom: 40px; right: 12px; }

		/* Bigger slider handle, easier to grab with a finger */
		main.swipe-page :global(.divider-handle) { width: 40px; height: 40px; font-size: 20px; }

		/* "i" button: bigger, top right beside the demographic legend */
		.info-btn {
			width: 36px;
			height: 36px;
			font-size: 18px;
		}
	}

	/* Large upright tablets (iPad Pro, Surface Pro): scale the map's
	   controls up so they take the same share of the screen as on an
	   iPad mini. "zoom" enlarges an element and everything inside it. */
	@media (min-width: 900px) and (max-width: 1100px) and (orientation: portrait) {
		main.swipe-page :global(.legend-slot),
		main.swipe-page :global(.divider-handle),
		.info-btn {
			zoom: 1.3;
		}
	}

	/* Large monitors (1800px+ wide): legends scale up so they stay readable */
	@media (min-width: 1800px) and (min-height: 1000px) {
		main.swipe-page :global(.legend-slot),
		.info-btn {
			zoom: 1.25;
		}
	}

	/* Touch-only devices (tablets of any size, e.g. iPad Pro in landscape, which is wider
	   than the tablet breakpoint): demographic legend across the top, travel-time legend
	   at the bottom — same layout as smaller tablets and phones */
	@media (hover: none) and (pointer: coarse) {
		main.swipe-page :global(.left-legend)  { max-width: calc(100% - 52px - 52px); }
		main.swipe-page :global(.right-legend) { top: auto; bottom: 40px; right: 12px; }
	}

	/* Phones held sideways (short landscape): too little height for the
	   tablet-sized legends, so shrink them back down. The demographic legend
	   fits on one row along the top; the travel-time legend moves to the
	   bottom, over the lake, just left of the scale bar. */
	@media (orientation: landscape) and (max-height: 500px) {
		main.swipe-page :global(.legend)          { padding: 6px 8px; }
		main.swipe-page :global(.legend-name)     { font-size: 11px; margin-bottom: 2px; }
		main.swipe-page :global(.right-legend .legend-name) { font-size: 12px; }
		main.swipe-page :global(.legend-subtitle) { font-size: 10px; margin: 1px 0 4px; }
		main.swipe-page :global(.color-bar)       { width: 110px; height: 9px; }
		main.swipe-page :global(.break-labels)    { width: 110px; font-size: 9px; }
		main.swipe-page :global(.legend-item)     { font-size: 11px; }
		main.swipe-page :global(.swatch)          { width: 9px; height: 9px; }

		main.swipe-page :global(.dropdown-wrap)        { font-size: 12px; margin-bottom: 4px; }
		main.swipe-page :global(.dropdown-wrap select) { font-size: 12px; padding: 2px 4px; }
		main.swipe-page :global(.bar-label)  { font-size: 11px; width: 78px; }
		main.swipe-page :global(.bar-track)  { width: 70px; height: 9px; }
		main.swipe-page :global(.bar-val)    { font-size: 11px; }
		main.swipe-page :global(.chart-note) { font-size: 9px; margin-top: 2px; }
		main.swipe-page :global(.bar-row)    { margin-bottom: 2px; gap: 2px; }

		main.swipe-page :global(.mode-title)    { font-size: 12px; }
		main.swipe-page :global(.mode-control)  { gap: 3px; }
		main.swipe-page :global(.toggle button) { font-size: 11px; padding: 4px 8px; }

		main.swipe-page :global(.left-legend)  { top: 8px; left: 50px; max-width: calc(100% - 50px - 48px); }
		main.swipe-page :global(.right-legend) { top: auto; bottom: 8px; right: 115px; }

		main.swipe-page :global(.divider-handle) { width: 32px; height: 32px; font-size: 16px; }

		.info-btn { top: 8px; width: 30px; height: 30px; font-size: 15px; }
	}

	/* Phones held upright (≤600px): compact, uncluttered */
	@media (max-width: 600px) {
		main.swipe-page :global(.dropdown-wrap select) {
			font-size: 13px;
			padding: 3px 4px;
			max-width: 140px;
		}
		main.swipe-page :global(.mode-title) { font-size: 12px; }
		main.swipe-page :global(.mode-control) { gap: 4px; }
		main.swipe-page :global(.toggle button) {
			font-size: 12px;
			padding: 5px 8px;
		}

		/* Bar chart inside the demographic legend */
		main.swipe-page :global(.bar-label)  { font-size: 11px; width: 76px; }
		main.swipe-page :global(.bar-track)  { width: 60px; height: 8px; }
		main.swipe-page :global(.bar-val)    { font-size: 11px; }
		main.swipe-page :global(.chart-note) { font-size: 9px; margin-top: 2px; }
		main.swipe-page :global(.bar-row)    { margin-bottom: 2px; gap: 3px; }

		/* Legends: smaller; the Library / Transit key appears once, in the demographic legend */
		main.swipe-page :global(.legend)          { padding: 6px 8px; }
		main.swipe-page :global(.legend-name)     { font-size: 12px; margin-bottom: 2px; }
		main.swipe-page :global(.right-legend .legend-name) { font-size: 13px; }
		main.swipe-page :global(.legend-subtitle) { font-size: 11px; margin: 1px 0 4px; }
		main.swipe-page :global(.color-bar)       { width: 110px; height: 9px; }
		main.swipe-page :global(.break-labels)    { width: 110px; font-size: 10px; margin-bottom: 4px; }
		main.swipe-page :global(.legend-item)     { font-size: 11px; }
		main.swipe-page :global(.swatch)          { width: 9px; height: 9px; }
		main.swipe-page :global(.legend-extras) {
			flex-direction: column;
			align-items: flex-start;
			gap: 2px;
		}
		/* Demographic legend top left; travel-time legend moves to the bottom right */
		main.swipe-page :global(.left-legend)  { top: 8px; left: 8px; max-width: calc(100% - 16px - 38px); }
		main.swipe-page :global(.right-legend) { top: auto; bottom: 52px; right: 8px; max-width: calc(100% - 16px); }

		main.swipe-page :global(.divider-handle) { width: 32px; height: 32px; font-size: 16px; }

		.info-btn {
			top: 8px;
			right: 8px;
			width: 30px;
			height: 30px;
			font-size: 15px;
		}
	}

	/* The phone tip in the About box only shows on upright phones */
	.info-card .phone-note { display: none; }
	@media (max-width: 600px) {
		.info-card .phone-note {
			display: block;
			background: #eef1f6;
			border-left: 3px solid #516082;
			padding: 8px 10px;
			border-radius: 4px;
		}
	}

	/* Short screens (phones held sideways): wider card, tighter text, so the whole
	   About box fits on screen without scrolling */
	@media (max-height: 500px) {
		.backdrop { padding: 10px; }
		.info-card {
			max-width: 720px;
			padding: 14px 22px 14px;
			font-size: 13px;
			line-height: 1.4;
		}
		.info-card h2 { font-size: 16px; margin-bottom: 6px; }
		.info-card p, .info-card li { font-size: 13px; line-height: 1.4; }
		.info-card p { margin-bottom: 8px; }
		.info-card ul { margin-bottom: 8px; }
		.info-card li { margin-bottom: 2px; }
		.ok-btn { padding: 5px 12px; font-size: 12px; }
	}
</style>
