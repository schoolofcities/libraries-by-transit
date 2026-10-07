<script>

	// title: e.g. "Travel time to nearest library" or a demographic label
	// subtitle: optional, e.g. the active weekday/weekend time window
	// colors: the color-bar segments, left to right
	// breakLabels: labels for the dividers between segments
	//   (length should be colors.length - 1, e.g. ['15 min', '30 min'] for 3 colors)
	export let title;
	export let subtitle = null;
	export let colors;
	export let breakLabels = [];
	// horizontal: lay the sections out side by side instead of stacked
	export let horizontal = false;
	// showExtras: show the Library / Major transit lines key
	export let showExtras = true;
	// leadLast: render the "lead" slot after everything else instead of before
	export let leadLast = false;
	// slots: "lead" renders as its own section before everything else (e.g. a toggle),
	//   "header" renders above the title (e.g. the variable dropdown),
	//   the default slot renders between the color bar and the library/transit items

</script>



<div class="legend" class:horizontal>
	{#if $$slots.lead && !leadLast}
		<div class="legend-section">
			<slot name="lead" />
		</div>
	{/if}
	<div class="legend-section">
		<slot name="header" />
		<div class="legend-name">{title}</div>
		{#if subtitle}
			<div class="legend-subtitle">{subtitle}</div>
		{/if}
		<div class="color-bar">
			{#each colors as color}
				<div class="color-segment" style="background:{color};"></div>
			{/each}
		</div>
		<div class="break-labels">
			<span></span>
			{#each breakLabels as label}
				<span>{label}</span>
			{/each}
			<span></span>
		</div>
	</div>
	{#if $$slots.default}
		<div class="legend-section legend-custom">
			<slot />
		</div>
	{/if}
	{#if showExtras}
		<div class="legend-section legend-extras">
			<div class="legend-item">
				<div class="swatch circle" style="background:#F9DD4E;"></div>
				<span>Library</span>
			</div>
			<div class="legend-item">
				<div class="swatch line"></div>
				<span>Major transit lines</span>
			</div>
		</div>
	{/if}
	{#if $$slots.lead && leadLast}
		<div class="legend-section">
			<slot name="lead" />
		</div>
	{/if}
</div>



<style>

	.legend {
		background: white;
		padding: 10px 12px;
		border: 1px solid #ccc;
		border-radius: 6px;
		font-family: 'OpenSans', sans-serif;
		font-size: 13px;
		box-shadow: 1px 1px 3px rgba(0,0,0,0.15);
		pointer-events: none;
	}

	.legend-name {
		font-family: 'TradeGothicBold', sans-serif;
		font-size: 12px;
		margin-bottom: 4px;
	}

	.legend-subtitle {
		color: #666;
		font-size: 11px;
		margin: 2px 0 6px;
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
		font-size: 10px;
		color: #444;
		margin-top: 2px;
		margin-bottom: 6px;
	}

	.legend-extras {
		display: flex;
		gap: 10px;
		align-items: center;
	}

	/* Horizontal — sections side by side, separated by thin rules; wraps if space runs out */
	.legend.horizontal {
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		gap: 8px 0;
	}

	.horizontal .legend-section {
		padding: 0 12px;
		border-left: 1px solid #eee;
		min-width: 0;   
	}

	.horizontal .legend-section:first-child {
		padding-left: 0;
		border-left: none;
	}

	.horizontal .legend-section:last-child { padding-right: 0; }

	
	.horizontal .legend-custom { flex: 1 1 180px; }

	.horizontal .break-labels { margin-bottom: 0; }

	.horizontal .legend-extras {
		flex-direction: column;
		align-items: flex-start;
		gap: 4px;
	}

	.legend-item {
		display: flex;
		align-items: center;
		gap: 4px;
		font-size: 12px;
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

	/* Tablet and below — compact sizing */
	@media (max-width: 1024px) {
		.legend { padding: 6px 8px; font-size: 11px; }
		.color-bar { width: 120px; height: 9px; }
		.break-labels { width: 120px; font-size: 9px; }
		.legend-name { font-size: 10px; margin-bottom: 2px; }
		.legend-item { font-size: 10px; }
		.swatch { width: 9px; height: 9px; }
		.horizontal .legend-section { padding: 0 8px; }
	}

	/* Phones */
	@media (max-width: 600px) {
		.horizontal .legend-custom {
			order: 1;
			flex-basis: 100%;
			border-left: none;
			border-top: 1px solid #eee;
			padding: 6px 0 0;
		}
	}

</style>
