<script>
	// Scrollytelling library tours: pick a tour, then scroll through each walk,
	// ride and library stop while the map follows along. The page fills its
	// viewport (or iframe) and scrolls inside the side panel, so it works the
	// same standalone or embedded.

	import { onMount, tick } from 'svelte';
	import { replaceState } from '$app/navigation';
	import '../../assets/global-styles.css';
	import TourMap from './lib/TourMap.svelte';
	import { WALK_COLOR, BOOK_ICON, modeLabel, minutes, distance, segmentsById } from './lib/tour.js';
	import tourDataUrl from './data/tour_app.json?url';

	// Where along the panel's height a step becomes active (0 = top).
	const TRIGGER = 0.4;

	let tours = $state([]);
	let tourId = $state(null);
	let progress = $state(0); // step index + fraction through that step
	let hoveredTour = $state(null);
	let panel;
	let mapWrap;

	const tour = $derived(tours.find((t) => t.id === tourId) ?? null);
	const byId = $derived(tour ? segmentsById(tour) : {});
	const steps = $derived(
		tour ? [{ kind: 'intro', segs: [], bbox: tour.bbox }, ...tour.steps] : []
	);
	const active = $derived(Math.floor(progress));

	onMount(async () => {
		tours = (await (await fetch(tourDataUrl)).json()).tours;
		const m = location.hash.match(/^#tour-(\d+)$/);
		if (m && tours.some((t) => t.id === +m[1])) selectTour(+m[1]);
	});

	async function selectTour(id) {
		tourId = id;
		progress = 0;
		hoveredTour = null;
		replaceState(id == null ? location.pathname + location.search : `#tour-${id}`, {});
		await tick();
		panel?.scrollTo({ top: 0 });
	}

	// Scroll position -> progress. A step runs from when its card's top reaches
	// the trigger line until the next card's top does.
	let frame = null;
	function onScroll() {
		if (!tour || frame) return;
		frame = requestAnimationFrame(() => {
			frame = null;
			const tops = [...panel.querySelectorAll('.step, .end')].map((el) => el.offsetTop);
			const y = panel.scrollTop + panel.clientHeight * TRIGGER;
			let i = 0;
			while (i < tops.length - 2 && tops[i + 1] <= y) i++;
			const frac = (y - tops[i]) / (tops[i + 1] - tops[i]);
			progress = i + Math.max(0, Math.min(0.999, frac));
		});
	}

	// Wheel over the map scrolls the panel, moving through the route. Jumping a
	// whole wheel tick at once feels jolty, so glide toward a target position
	// each frame, like the browser's own smooth scrolling on the panel.
	$effect(() => {
		if (!mapWrap) return;
		let target = null;
		let raf = null;
		let last = 0;
		// Time-based easing: close ~18% of the gap per 60 fps frame, however
		// long frames actually take.
		const glide = (now) => {
			const dt = Math.min(100, now - last);
			last = now;
			const diff = target - panel.scrollTop;
			if (Math.abs(diff) <= 1) {
				panel.scrollTop = target;
				target = null;
				raf = null;
				return;
			}
			const k = 1 - Math.pow(1 - 0.18, dt / 16.7);
			// scrollTop snaps to whole pixels, so always move at least 1px.
			panel.scrollTop += Math.sign(diff) * Math.max(1, Math.abs(diff) * k);
			raf = requestAnimationFrame(glide);
		};
		const forward = (e) => {
			e.preventDefault();
			const unit = e.deltaMode === 1 ? 16 : e.deltaMode === 2 ? panel.clientHeight : 1;
			const max = panel.scrollHeight - panel.clientHeight;
			target = Math.max(0, Math.min(max, (target ?? panel.scrollTop) + e.deltaY * unit));
			if (!raf) {
				last = performance.now();
				raf = requestAnimationFrame(glide);
			}
		};
		// Scrolling the panel directly takes over from any glide in progress.
		const cancel = () => {
			if (raf) cancelAnimationFrame(raf);
			target = raf = null;
		};
		mapWrap.addEventListener('wheel', forward, { passive: false });
		panel.addEventListener('wheel', cancel, { passive: true });
		return () => {
			cancel();
			mapWrap.removeEventListener('wheel', forward);
			panel.removeEventListener('wheel', cancel);
		};
	});

	function goToStep(i) {
		const el = panel.querySelector(`.step[data-index="${i}"]`);
		panel.scrollTo({ top: el.offsetTop - panel.clientHeight * TRIGGER + 1, behavior: 'smooth' });
	}

	// Scroll room after each card, in vh: longer walks and rides get more, so
	// the dot moves at a steadier pace. It's a spacer inside the step (not a
	// margin or padding) so the sticky card stays in view for the whole step.
	function spacing(s) {
		if (s.kind === 'intro' || s.kind === 'library') return 120;
		const metres = s.segs.reduce((sum, id) => sum + byId[id].meters, 0);
		return Math.round(Math.min(480, 120 + metres / 17));
	}

	// Subway and LRT lines read "Line 1"; buses and streetcars just the number
	// (so the 7 Bathurst bus isn't mistaken for a line).
	function chipText(seg) {
		const isLine = seg.mode === 'SUBWAY' || modeLabel(seg) === 'LRT';
		return isLine ? `Line ${seg.line}` : seg.line;
	}

	function chipTextColor(seg) {
		return seg.line === '1' ? 'var(--brandBlack)' : 'var(--brandWhite)';
	}
</script>

<svelte:head>
	<title>Toronto Public Library tours by transit | School of Cities</title>
	<meta name="description" content="Ten tours of Toronto Public Library branches by TTC and on foot." />
</svelte:head>

<div class="app">
	<aside class="panel" bind:this={panel} onscroll={onScroll}>
		<div class="panel-top">
			<header class="site-header">
				<div class="stripe" aria-hidden="true">
					{#each tours as t (t.id)}<span style:background={t.color}></span>{/each}
				</div>
				<div class="title-row">
					<span class="badge" aria-hidden="true">{@html BOOK_ICON}</span>
					<h1>Toronto Public Library tours</h1>
				</div>
				<ul class="facts">
					<li>{tours.length} tours</li>
					<li>{tours.reduce((n, t) => n + t.libraries.length, 0)} branches</li>
					<li>via TTC</li>
				</ul>
			</header>
			{#if tour}
				<header class="tour-header">
					<button class="back" onclick={() => selectTour(null)}>← All tours</button>
					<select
						aria-label="Choose a tour"
						value={tour.id}
						onchange={(e) => selectTour(+e.currentTarget.value)}
					>
						{#each tours as t (t.id)}
							<option value={t.id}>Tour {t.id}: {t.title}</option>
						{/each}
					</select>
				</header>
			{/if}
		</div>

		{#if !tour}
			<ul class="tour-list">
				{#each tours as t (t.id)}
					<li>
						<button
							class="tour-card"
							onclick={() => selectTour(t.id)}
							onmouseenter={() => (hoveredTour = t.id)}
							onmouseleave={() => (hoveredTour = null)}
							onfocus={() => (hoveredTour = t.id)}
							onblur={() => (hoveredTour = null)}
						>
							<span class="swatch" style:background={t.color}></span>
							<span class="tour-card-text">
								<span class="eyebrow">Tour {t.id}</span>
								<span class="tour-title">{t.title}</span>
								<span class="meta">{distance(t.walk_km * 1000)} walking · {t.rides} transit rides</span>
							</span>
						</button>
					</li>
				{/each}
			</ul>
		{:else}

			<ol class="steps" style:--tour-color={tour.color}>
				{#each steps as s, i (i)}
					<li class="step {s.kind}" class:active={i === active} data-index={i}>
						<!-- svelte-ignore a11y_click_events_have_key_events, a11y_no_static_element_interactions -->
						<div class="card" onclick={() => goToStep(i)}>
							{#if s.kind === 'intro'}
								<span class="eyebrow" style:color={tour.color}>Tour {tour.id}</span>
								<h2>{tour.title}</h2>
								<div class="meta">
									{tour.libraries.length} Toronto Public Libraries · {distance(tour.walk_km * 1000)} walking · {tour.rides} transit rides
								</div>
								<ol class="library-list">
									{#each tour.libraries as lib (lib.n)}
										<li><span class="num">{lib.n}</span>{lib.name}</li>
									{/each}
								</ol>
								<div class="hint">Scroll to start ↓</div>
							{:else if s.kind === 'library'}
								{@const lib = tour.libraries[s.library - 1]}
								<div class="library-head">
									<span class="num big">{lib.n}</span>
									<div>
										<span class="eyebrow">
											{s.library === 1 ? 'Start' : s.library === tour.libraries.length ? 'Final stop' : `Toronto Public Library ${lib.n} of ${tour.libraries.length}`}
										</span>
										<h3>{lib.name}</h3>
									</div>
								</div>
								<div class="address">{lib.address}</div>
								<a class="link" href={lib.url} target="_blank" rel="noopener" onclick={(e) => e.stopPropagation()}>
									Hours &amp; info at tpl.ca ↗
								</a>
							{:else if s.kind === 'walk'}
								{@const seg = byId[s.segs[0]]}
								<span class="chip walk" style:background={WALK_COLOR}>Walk</span>
								<div class="instruction">
									{s.transfer ? 'Transfer: walk' : 'Walk'}
									{minutes(seg.minutes)} to <strong>{s.to}</strong>
								</div>
								<div class="meta">{distance(seg.meters)}</div>
							{:else}
								{@const segs = s.segs.map((id) => byId[id])}
								{@const ride = segs[segs.length - 1]}
								<span class="chip" style:background={ride.color} style:color={chipTextColor(ride)}>
									{modeLabel(ride)} {chipText(ride)}
								</span>
								{#if segs.length > 1}
									<div class="meta">Short walk to transfer ({minutes(segs[0].minutes)})</div>
								{/if}
								<div class="instruction">
									Take the
									<a href={ride.url} target="_blank" rel="noopener" onclick={(e) => e.stopPropagation()}>
										{ride.line_name}
									</a>
									from <strong>{ride.from_stop}</strong> to <strong>{ride.to_stop}</strong>
								</div>
								<div class="meta">{minutes(ride.minutes)} · {distance(ride.meters)}</div>
							{/if}
						</div>
						<div class="spacer" style:height="{spacing(s)}vh"></div>
					</li>
				{/each}

				<li class="end">
					<p class="note">
						Durations are rounded travel times on foot or on board, and don't include
						waiting for transit. Routes favour less walking over the fastest trip, using
						the TTC's weekday schedule.
					</p>
					<div class="end-buttons">
						<button class="back" onclick={() => selectTour(null)}>← All tours</button>
						{#if tour.id < tours.length}
							<button class="next" onclick={() => selectTour(tour.id + 1)}>Next: Tour {tour.id + 1} →</button>
						{/if}
					</div>
				</li>
			</ol>
		{/if}
	</aside>

	<div class="map-wrap" bind:this={mapWrap}>
		{#if tours.length}
			<TourMap
				{tours}
				{tour}
				{steps}
				{progress}
				{hoveredTour}
				onselect={(id) => selectTour(id)}
			/>
		{/if}
	</div>
</div>

<style>
	:global(body) {
		overflow: hidden;
	}

	.app {
		display: grid;
		grid-template-columns: minmax(340px, min(40%, 500px)) 1fr;
		height: 100dvh;
		font-family: OpenSans, sans-serif;
		color: var(--brandGray90);
		background: var(--brandWhite);
	}

	.panel {
		overflow-y: auto;
		border-right: 1px solid var(--brandGray);
		position: relative;
	}

	.map-wrap {
		position: relative;
		min-height: 0;
	}

	h1,
	h2,
	h3 {
		font-family: TradeGothicBold, OpenSansBold, sans-serif;
		font-weight: normal;
		color: var(--brandBlack);
		margin: 0;
	}

	h1 {
		font-size: 32px;
	}

	h2 {
		font-size: 24px;
		line-height: 1.15;
		margin: 2px 0 6px;
		color: var(--brandDarkBlue);
	}

	h3 {
		font-size: 20px;
		line-height: 1.15;
	}

	/* The global stylesheet sets Source Serif on li, a and strong; this page
	   uses Open Sans throughout. */
	li {
		font-family: OpenSans, sans-serif;
		font-size: inherit;
		line-height: inherit;
		color: inherit;
		padding: 0;
	}

	strong {
		font-family: OpenSansBold, sans-serif;
		font-weight: normal;
	}

	a {
		font-family: inherit;
		color: var(--brandMedBlue);
	}

	a:hover {
		color: var(--brandDarkBlue);
	}

	button {
		font-family: OpenSans, sans-serif;
	}

	.eyebrow {
		display: block;
		font-family: OpenSansBold, sans-serif;
		font-size: 12px;
		color: var(--brandGray60);
	}

	.meta,
	.address {
		font-size: 13px;
		color: var(--brandGray60);
		line-height: 1.5;
	}

	/* Overview */

	.site-header {
		padding: 0 24px 16px;
	}

	.stripe {
		display: flex;
		height: 8px;
		margin: 0 -24px 18px;
	}

	.stripe span {
		flex: 1;
	}

	.title-row {
		display: flex;
		align-items: center;
		gap: 12px;
	}

	.badge {
		flex: none;
		display: flex;
		align-items: center;
		justify-content: center;
		width: 38px;
		height: 38px;
		border-radius: 50%;
		background: var(--brandDarkBlue);
		color: var(--brandWhite);
	}

	.badge :global(svg) {
		width: 22px;
		height: 22px;
	}

	.site-header h1 {
		font-size: 28px;
		line-height: 1.1;
		color: var(--brandDarkBlue);
	}

	.facts {
		display: flex;
		flex-wrap: wrap;
		gap: 6px;
		list-style: none;
		margin: 12px 0 0;
		padding: 0;
	}

	.facts li {
		font-family: OpenSans, sans-serif;
		font-size: 12px;
		line-height: 1;
		padding: 6px 10px;
		border-radius: 0;
		background: #eef1f6;
		color: var(--brandDarkBlue);
	}

	.tour-list {
		list-style: none;
		margin: 0;
		padding: 0 16px 24px;
	}

	.tour-card {
		display: flex;
		gap: 12px;
		align-items: stretch;
		width: 100%;
		text-align: left;
		background: none;
		border: 0;
		border-bottom: 1px solid var(--brandGray);
		padding: 12px 8px;
		cursor: pointer;
		color: inherit;
	}

	.tour-card:hover,
	.tour-card:focus-visible {
		background: #f4f5f1;
	}

	.swatch {
		flex: 0 0 6px;
		border-radius: 0;
	}

	.tour-card-text {
		display: flex;
		flex-direction: column;
		gap: 2px;
	}

	.tour-title {
		font-family: OpenSansBold, sans-serif;
		font-size: 15px;
		color: var(--brandBlack);
	}

	/* Tour */

	/* Header and tour controls stay pinned together at the top of the panel. */
	.panel-top {
		position: sticky;
		top: 0;
		z-index: 3;
		background: rgba(255, 255, 255, 0.97);
		border-bottom: 1px solid var(--brandGray);
	}

	.tour-header {
		display: flex;
		gap: 8px;
		align-items: center;
		padding: 0 16px 12px;
	}

	.tour-header select {
		flex: 1;
		min-width: 0;
		font-family: OpenSans, sans-serif;
		font-size: 13px;
		padding: 6px;
		border: 1px solid var(--brandGray);
		border-radius: 0;
		background: var(--brandWhite);
	}

	.back,
	.next {
		flex: none;
		font-size: 13px;
		padding: 6px 10px;
		border: 1px solid var(--brandGray);
		border-radius: 0;
		background: var(--brandWhite);
		color: var(--brandDarkBlue);
		cursor: pointer;
	}

	.next {
		background: var(--brandDarkBlue);
		border-color: var(--brandDarkBlue);
		color: var(--brandWhite);
	}

	.steps {
		list-style: none;
		margin: 0;
		padding: 24px 16px 0;
	}

	/* Each card sticks at the trigger line while its step plays out, then the
	   next card pushes it up. */
	.card {
		position: sticky;
		top: 40%;
		padding: 16px 18px;
		border: 1px solid var(--brandGray);
		border-left: 8px solid var(--brandGray);
		border-radius: 0;
		background: var(--brandWhite);
		opacity: 0.45;
		cursor: pointer;
		transition: opacity 0.3s, border-color 0.3s, box-shadow 0.3s;
	}

	.step.intro .card {
		position: static;
	}

	.step.active .card {
		opacity: 1;
		border-left-color: var(--tour-color);
		box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
	}

	.instruction {
		font-size: 16px;
		line-height: 1.45;
		margin: 8px 0 2px;
	}

	.chip {
		display: inline-block;
		font-family: OpenSansBold, sans-serif;
		font-size: 12px;
		padding: 2px 8px;
		border-radius: 0;
		color: var(--brandWhite);
	}

	.library-head {
		display: flex;
		gap: 12px;
		align-items: center;
		margin-bottom: 6px;
	}

	.num {
		display: inline-block;
		width: 20px;
		height: 20px;
		margin-right: 8px;
		border-radius: 50%;
		border: 2px solid var(--brandDarkBlue);
		color: var(--brandDarkBlue);
		font-family: OpenSansBold, sans-serif;
		font-size: 10px;
		line-height: 20px;
		text-align: center;
		flex: none;
	}

	.num.big {
		width: 34px;
		height: 34px;
		line-height: 34px;
		font-size: 15px;
		margin: 0;
		background: var(--brandDarkBlue);
		color: var(--brandWhite);
	}

	.library-list {
		list-style: none;
		padding: 0;
		margin: 12px 0;
		font-size: 13px;
		line-height: 2;
	}

	.link {
		display: inline-block;
		margin-top: 8px;
		font-size: 14px;
	}

	.hint {
		font-family: OpenSansBold, sans-serif;
		font-size: 13px;
		color: var(--brandBlack);
	}

	.end {
		padding: 0 4px 40vh;
	}

	.note {
		font-family: OpenSans, sans-serif;
		font-size: 12px;
		line-height: 1.6;
		color: var(--brandGray60);
	}

	.end-buttons {
		display: flex;
		gap: 8px;
	}

	/* Phones and narrow iframes: map on top, steps underneath. */
	@media (max-width: 700px) {
		.app {
			grid-template-columns: 1fr;
			grid-template-rows: 42dvh 1fr;
		}

		.map-wrap {
			grid-row: 1;
		}

		.facts {
			display: none;
		}

		.site-header h1 {
			font-size: 22px;
		}

		.panel {
			grid-row: 2;
			border-right: 0;
			border-top: 1px solid var(--brandGray);
		}
	}
</style>
