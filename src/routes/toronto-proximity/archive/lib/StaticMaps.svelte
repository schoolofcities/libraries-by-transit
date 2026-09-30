<script>

	import ChoroplethMap from './ChoroplethMap.svelte';
	import { ALL_VARIABLE_IDS } from '../../lib/demographics.js';

	let open = false;

</script>



<div class="accordion">

	<button class="accordion-btn" on:click={() => open = !open}>
		{open ? '▲' : '▼'} View demographic maps by census tract
	</button>

	{#if open}
		<div class="map-grid">
			{#each ALL_VARIABLE_IDS as v}
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
		max-width: 1120px;
		margin: 0 auto;
		padding: 0 6px;
		box-sizing: border-box;
	}

	.accordion-btn {
		width: 100%;
		padding: 8px 12px;
		background: #f5f5f5;
		border: 1px solid #ddd;
		border-radius: 6px;
		font-family: 'OpenSans', sans-serif;
		font-size: 14px;
		font-weight: bold;
		color: #1E3765;
		cursor: pointer;
		text-align: left;
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
