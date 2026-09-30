<script>
	import '../../assets/global-styles.css';
	import SwipeMap from '../../lib/SwipeMapStandalone.svelte';

	let showInfo = true;

	const isTabletOrPhone =
		typeof window !== 'undefined' &&
		(window.innerWidth <= 1024 ||
		 (window.innerWidth <= 1100 && window.innerHeight > window.innerWidth));
	const zoomOffset = isTabletOrPhone ? 0.18 : 0.25;
</script>

<svelte:head>
	<title>Library access swipe map | School of Cities</title>
</svelte:head>

<svelte:window on:keydown={(e) => { if (e.key === 'Escape') showInfo = false; }} />

<main class="swipe-page">
	<SwipeMap {zoomOffset}/>

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
					<li>Use the <b>Variable</b> menu at the top to switch between population groups, and the <b>Weekday/Weekend</b> buttons to change the transit schedule.</li>
				</ul>
				<p class="phone-note">If you are viewing this webpage from your phone, it is highly advised to explore the data in landscape, or on larger screens (tablets/laptops).</p>
				<p>If you are interested to learn more about the research and findings, <a href="https://schoolofcities.github.io/posts/spatial-access-to-public-libraries-toronto/" target="_blank" rel="noopener">read the study</a>.</p>
				<button class="ok-btn" on:click={() => (showInfo = false)}>Explore the map</button>
			</div>
		</div>
	{/if}
</main>

<style>
	.swipe-page {
		width: 100vw;
		height: 100dvh;
		overflow: hidden;
	}

	.swipe-page :global(.swipe-wrap) {
		height: 100dvh;
	}

	/* One font for the whole pop-up and button, matching the map labels */
	/* ── Responsive tweaks for this full-screen page only ── */

	/* The shared map hides the travel-time legend below 1024px (it was built
	   for the shorter map on the story page). Full screen has room, so show it. */
	.swipe-page :global(.right-legend) {
		display: block;
	}

	/* Keep "17.3 min" on one line on smaller screens */
	.swipe-page :global(.bar-val) {
		width: auto;
		white-space: nowrap;
	}

	.info-btn, .backdrop {
		font-family: 'OpenSans', sans-serif;
	}

	/* Open Sans bold is its own font file, so bold text uses it directly */
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
		background: white;
		max-width: 480px;
		max-height: calc(100dvh - 32px);
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

	/* The site-wide stylesheet gives p and li their own font, size and
	   spacing, which beat anything inherited from .info-card. Setting them
	   directly here makes all body text in the pop-up identical. */
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
	/* ── Bigger controls on tablets and phones ──────────────────────────
	   The shared map shrinks its labels, legends and toggles below 1024px
	   (to fit the short map on the story page). This full-screen page has
	   room, so these rules size them back up. "main.swipe-page" makes each
	   rule slightly more specific than the component's own, so these win. */

	/* Tablets, small laptops and phones held sideways (601–1024px),
	   plus large upright tablets up to 1100px (iPad Pro, Surface Pro) */
	@media (max-width: 1024px), (max-width: 1100px) and (orientation: portrait) {
		/* Variable menu sits top-left, with the demographic card below it */
		main.swipe-page :global(.dropdown-wrap) {
			top: 12px;
			left: 52px;
			transform: none;
			font-size: 13px;
			padding: 5px 10px;
		}
		main.swipe-page :global(.dropdown-wrap select) {
			font-size: 14px;
			padding: 4px 6px;
		}
		main.swipe-page :global(.left-label) {
			top: 60px;
			left: 52px;
			max-width: 300px;
			padding: 8px 12px;
		}
		main.swipe-page :global(.label-text) { font-size: 14px; margin-bottom: 6px; }
		main.swipe-page :global(.label-sub)  { font-size: 11px; }
		main.swipe-page :global(.bar-label)  { font-size: 12px; width: 92px; }
		main.swipe-page :global(.bar-track)  { width: 110px; height: 12px; }
		main.swipe-page :global(.bar-val)    { font-size: 12px; }
		main.swipe-page :global(.chart-note) { font-size: 10px; margin-top: 4px; }
		main.swipe-page :global(.bar-row)    { margin-bottom: 4px; gap: 4px; }

		/* Walking + Transit box and Weekday/Weekend toggle */
		main.swipe-page :global(.right-label) {
			right: 8px;
			font-size: 15px;
			padding: 8px 10px;
			gap: 6px;
		}
		main.swipe-page :global(.toggle button) {
			font-size: 13px;
			padding: 7px 14px;
		}

		/* Legends */
		main.swipe-page :global(.legend)          { padding: 10px 12px; }
		main.swipe-page :global(.legend-name)     { font-size: 13px; margin-bottom: 4px; }
		main.swipe-page :global(.legend-subtitle) { font-size: 12px; }
		main.swipe-page :global(.color-bar)       { width: 170px; height: 13px; }
		main.swipe-page :global(.break-labels)    { width: 170px; font-size: 11px; }
		main.swipe-page :global(.legend-item)     { font-size: 12px; }
		main.swipe-page :global(.swatch)          { width: 12px; height: 12px; }
		main.swipe-page :global(.swatch.line)     { height: 3px; }
		main.swipe-page :global(.left-legend)     { bottom: 12px; left: 12px; }

		/* Bigger slider handle, easier to grab with a finger */
		main.swipe-page :global(.divider-handle) { width: 40px; height: 40px; font-size: 20px; }

		/* "i" button: bigger, and just below the Walking + Transit box */
		.info-btn {
			top: 92px;
			width: 36px;
			height: 36px;
			font-size: 18px;
		}
	}

	/* Large upright tablets (iPad Pro, Surface Pro): scale the map's
	   controls up so they take the same share of the screen as on an
	   iPad mini. "zoom" enlarges an element and everything inside it. */
	@media (min-width: 900px) and (max-width: 1100px) and (orientation: portrait) {
		main.swipe-page :global(.dropdown-wrap),
		main.swipe-page :global(.map-label),
		main.swipe-page :global(.legend-slot),
		main.swipe-page :global(.divider-handle),
		.info-btn {
			zoom: 1.3;
		}
	}

	/* Phones held upright (≤600px): compact, uncluttered */
	@media (max-width: 600px) {
		main.swipe-page :global(.dropdown-wrap) {
			left: 8px;
			top: 8px;
			padding: 4px 6px;
		}
		main.swipe-page :global(.dropdown-wrap select) {
			font-size: 12px;
			padding: 3px 4px;
			max-width: 140px;
		}
		main.swipe-page :global(.right-label) {
			right: 6px;
			top: 8px;
			font-size: 11px;
			padding: 5px 7px;
			gap: 4px;
		}
		main.swipe-page :global(.toggle button) {
			font-size: 11px;
			padding: 5px 8px;
		}

		/* Demographic card: bars and minutes only */
		main.swipe-page :global(.left-label) {
			display: block;
			top: 72px;
			left: 8px;
			max-width: 200px;
			padding: 5px 8px;
		}
		main.swipe-page :global(.label-sub)  { display: none; }
		main.swipe-page :global(.label-text) { font-size: 11px; margin-bottom: 3px; }
		main.swipe-page :global(.bar-label)  { font-size: 10px; width: 70px; }
		main.swipe-page :global(.bar-track)  { width: 60px; height: 8px; }
		main.swipe-page :global(.bar-val)    { font-size: 10px; }
		main.swipe-page :global(.chart-note) { font-size: 8px; margin-top: 2px; }
		main.swipe-page :global(.bar-row)    { margin-bottom: 2px; gap: 3px; }

		/* Legends: smaller; the Library / Transit key appears once,
		   stacked, in the travel-time legend */
		main.swipe-page :global(.legend)          { padding: 6px 8px; }
		main.swipe-page :global(.legend-name)     { font-size: 11px; margin-bottom: 2px; }
		main.swipe-page :global(.legend-subtitle) { font-size: 10px; margin: 1px 0 4px; }
		main.swipe-page :global(.color-bar)       { width: 110px; height: 9px; }
		main.swipe-page :global(.break-labels)    { width: 110px; font-size: 9px; margin-bottom: 4px; }
		main.swipe-page :global(.legend-item)     { font-size: 10px; }
		main.swipe-page :global(.swatch)          { width: 9px; height: 9px; }
		main.swipe-page :global(.left-legend .legend-extras) { display: none; }
		main.swipe-page :global(.legend-extras) {
			flex-direction: column;
			align-items: flex-start;
			gap: 2px;
		}
		main.swipe-page :global(.left-legend)  { bottom: 10px; left: 8px; }
		main.swipe-page :global(.right-legend) { bottom: 32px; right: 8px; }

		main.swipe-page :global(.divider-handle) { width: 32px; height: 32px; font-size: 16px; }

		.info-btn {
			top: 72px;
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
	/* Phones held sideways: hide the "% of population per census tract" line */
	@media (orientation: landscape) and (max-height: 500px) {
		main.swipe-page :global(.label-sub) { display: none; }
	}
</style>
