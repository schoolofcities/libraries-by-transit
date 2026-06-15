<script>

	import ChoroplethMap from './ChoroplethMap.svelte';

	let open = false;

	const variables = [
		'visible_minority_pct',
		'low_income_pct',
		'recent_immigrants_pct',
		'first_gen_immigrants_pct',
		'seniors_pct',
		'children_pct',
	];

</script>



<div class="accordion">

	<button class="accordion-btn" on:click={() => open = !open}>
		{open ? '▲' : '▼'} View demographic maps by census tract
	</button>

	{#if open}
		<div class="map-grid">
			{#each variables as v}
				<div class="map-cell">
					<ChoroplethMap variable={v}/>
				</div>
			{/each}
		</div>
	{/if}

</div>



<style>

	.accordion {
		width: 100%;
		max-width: 1400px;
		margin: 0 auto;
		padding: 0 12px;
		box-sizing: border-box;
	}

	.accordion-btn {
		width: 100%;
		padding: 12px 16px;
		background: #f5f5f5;
		border: 1px solid #ddd;
		border-radius: 6px;
		font-family: Arial, sans-serif;
		font-size: 14px;
		font-weight: bold;
		color: #1E3765;
		cursor: pointer;
		text-align: left;
		transition: background 0.15s;
		box-sizing: border-box;
	}

	.accordion-btn:hover {
		background: #ececec;
	}

	.map-grid {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: 12px;
		padding: 16px 0;
	}

	@media (max-width: 900px) {
		.map-grid { grid-template-columns: repeat(2, 1fr); }
	}

	@media (max-width: 560px) {
		.map-grid { grid-template-columns: 1fr; }
	}

	.map-cell {
		width: 100%;
		min-width: 0;
		overflow: hidden;
	}

</style>
