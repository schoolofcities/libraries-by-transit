<script>

	import { DOTPLOT_DATA, CITY_AVG } from '../../lib/demographics.js';

	const data = [...DOTPLOT_DATA].sort((a, b) => b.walk - a.walk);  // sorting by walk time descending

	const cityTransit = CITY_AVG.transit;
	const cityWalk = CITY_AVG.walk;

	const W       = 620;
	const rowH    = 36;
	const labelW  = 160;
	const chartW  = W - labelW - 60;
	const padTop  = 40;
	const padBot  = 50;
	const minVal  = 16;
	const maxVal  = 23;
	const H       = padTop + data.length * rowH + padBot;

	function cx(val) {
		return labelW + ((val - minVal) / (maxVal - minVal)) * chartW;
	}

	const ticks = [16, 19, 22];

</script>



<div class="wrap">

	<div class="chart-title">Average travel time to nearest Toronto Public Library branch</div>
	<div class="chart-sub">
		Population-weighted mean · 2021 Census dissemination areas ·
		Transit averaged across weekday (Tue Jun 8) and weekend (Sat Jun 13), 10:00–10:30 departure window
	</div>

	<svg viewBox="0 0 {W} {H}" style="width:100%; height:auto; display:block;">

		<!-- Grid lines -->
		{#each ticks as tick}
			<line
				x1={cx(tick)} y1={padTop - 6}
				x2={cx(tick)} y2={padTop + data.length * rowH}
				stroke="#e8e8e8" stroke-width="1"
			/>
			<text x={cx(tick)} y={padTop - 9} class="tick" text-anchor="middle">{tick}</text>
		{/each}

		<!-- X axis label -->
		<text x={labelW + chartW / 2} y={padTop - 22}
			class="axis-label" text-anchor="middle">Minutes</text>

		<!-- City average reference lines -->
		<line
			x1={cx(cityTransit)} y1={padTop - 4}
			x2={cx(cityTransit)} y2={padTop + data.length * rowH}
			stroke="#6D247A" stroke-width="1" stroke-dasharray="4,3" opacity="0.4"
		/>
		<line
			x1={cx(cityWalk)} y1={padTop - 4}
			x2={cx(cityWalk)} y2={padTop + data.length * rowH}
			stroke="#C4A7C9" stroke-width="1" stroke-dasharray="4,3" opacity="0.4"
		/>
		<text x={cx(cityTransit)} y={padTop - 6} class="ref-label" text-anchor="middle" fill="#6D247A">city avg</text>
		<text x={cx(cityWalk)}    y={padTop - 6} class="ref-label" text-anchor="middle" fill="#C4A7C9">city avg</text>

		<!-- Rows -->
		{#each data as d, i}
			{@const y = padTop + i * rowH + rowH / 2}
			{@const isTotal = d.label === 'Total Population'}

			<!-- Alternating background -->
			{#if i % 2 === 0}
				<rect x={0} y={padTop + i * rowH} width={W} height={rowH}
					fill="#f9f9f9" opacity="0.6"/>
			{/if}

			<!-- Separator above Total Population -->
			{#if isTotal}
				<line x1={0} y1={padTop + i * rowH} x2={W} y2={padTop + i * rowH}
					stroke="#ccc" stroke-width="1"/>
			{/if}

			<!-- Group label -->
			<text x={labelW - 8} y={y + 4}
				class={isTotal ? 'group-label bold' : 'group-label'}
				text-anchor="end">{d.label}</text>

			<!-- Connecting line between transit and walk -->
			<line
				x1={cx(d.transit)} y1={y}
				x2={cx(d.walk)}    y2={y}
				stroke="#ddd" stroke-width="1.5"
			/>

			<!-- Walk dot (open) -->
			<circle cx={cx(d.walk)} cy={y} r="6"
				fill="white" stroke="#C4A7C9" stroke-width="2"
				opacity={isTotal ? 1 : 0.85}
			/>

			<!-- Transit dot (filled) -->
			<circle cx={cx(d.transit)} cy={y} r="6"
				fill="#6D247A"
				opacity={isTotal ? 1 : 0.85}
			/>

			<!-- Value labels -->
			<text x={cx(d.transit) - 9} y={y + 4}
				class="val" text-anchor="end" fill="#6D247A">{d.transit}</text>
			<text x={cx(d.walk) + 9}    y={y + 4}
				class="val" text-anchor="start" fill="#999">{d.walk}</text>

		{/each}

		<!-- Legend -->
		<circle cx={labelW}      cy={H - 24} r="6" fill="#6D247A"/>
		<text   x={labelW + 12}  y={H - 20} class="leg">Walk + Transit</text>

		<circle cx={labelW + 120} cy={H - 24} r="6"
			fill="white" stroke="#C4A7C9" stroke-width="2"/>
		<text   x={labelW + 132} y={H - 20} class="leg">Walking only</text>

		<line   x1={labelW + 250} y1={H - 24} x2={labelW + 265} y2={H - 24}
			stroke="#6D247A" stroke-width="1" stroke-dasharray="4,3" opacity="0.5"/>
		<text   x={labelW + 268} y={H - 20} class="leg">City average</text>

	</svg>

</div>



<style>

	.wrap {
		width: 100%;
		max-width: 680px;
		font-family: 'OpenSans', Arial, sans-serif;
	}

	.chart-title {
		font-family: 'TradeGothicBold', Arial, sans-serif;
		font-size: 13px;
		color: #222;
		margin-bottom: 3px;
	}

	.chart-sub {
		font-size: 10px;
		color: #999;
		margin-bottom: 8px;
		line-height: 1.5;
	}

	.group-label {
		font-family: 'OpenSans', Arial, sans-serif;
		font-size: 11px;
		fill: #333;
	}

	.group-label.bold {
		font-weight: bold;
		fill: #111;
	}

	.val {
		font-family: 'OpenSans', Arial, sans-serif;
		font-size: 9px;
	}

	.tick {
		font-family: 'OpenSans', Arial, sans-serif;
		font-size: 9px;
		fill: #bbb;
	}

	.axis-label {
		font-family: 'OpenSans', Arial, sans-serif;
		font-size: 9px;
		fill: #999;
	}

	.ref-label {
		font-family: 'OpenSans', Arial, sans-serif;
		font-size: 8px;
		opacity: 0.7;
	}

	.leg {
		font-family: 'OpenSans', Arial, sans-serif;
		font-size: 10px;
		fill: #555;
	}

</style>
