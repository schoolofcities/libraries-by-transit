<script>

	// title: e.g. "Minutes to Library" or a demographic label
	// subtitle: optional, e.g. the active weekday/weekend time window
	// colors: the color-bar segments, left to right
	// breakLabels: labels for the dividers between segments
	//   (length should be colors.length - 1, e.g. ['15 min', '30 min'] for 3 colors)
	export let title;
	export let subtitle = null;
	export let colors;
	export let breakLabels = [];

</script>



<div class="legend">
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
	<div class="legend-extras">
		<div class="legend-item">
			<div class="swatch circle" style="background:#F9DD4E;"></div>
			<span>Library</span>
		</div>
		<div class="legend-item">
			<div class="swatch line"></div>
			<span>Major Transit Lines</span>
		</div>
	</div>
</div>



<style>

	.legend {
		background: white;
		padding: 10px 12px;
		border: 1px solid #ccc;
		border-radius: 6px;
		font-family: 'OpenSans', sans-serif;
		font-size: 12px;
		box-shadow: 1px 1px 3px rgba(0,0,0,0.15);
		pointer-events: none;
	}

	.legend-name {
		font-family: 'TradeGothicBold', sans-serif;
		font-size: 11px;
		margin-bottom: 4px;
	}

	.legend-subtitle {
		color: #666;
		font-size: 10px;
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

	/* Tablet and below — compact sizing (previously only applied in SwipeMap;
	   now consistent everywhere Legend is used, including WalkMap/TransitMap). */
	@media (max-width: 1024px) {
		.legend { padding: 6px 8px; font-size: 10px; }
		.color-bar { width: 120px; height: 9px; }
		.break-labels { width: 120px; font-size: 8px; }
		.legend-name { font-size: 9px; margin-bottom: 2px; }
		.legend-item { font-size: 9px; }
		.swatch { width: 9px; height: 9px; }
	}

</style>
