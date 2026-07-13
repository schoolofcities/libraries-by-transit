<script>

	import { geoPath, geoMercator, scaleThreshold } from "d3";
	import ctData from "../assets/census_tracts_demographics.geo.json";
	import librariesData from "../assets/libraries.geo.json";
	import ttcData from "../assets/ttc_main_lines.geo.json";
	import { VARIABLES_BY_ID, CITY_AVG } from './demographics.js';
	import { lighten } from './utils.js';

	export let variable = 'visible_minority_pct';

	const maxBarVal = 35;
	const barMaxW   = 150;

	$: cfg = VARIABLES_BY_ID[variable];

	$: barColor      = cfg.colors[cfg.colors.length - 1];
	$: barColorLight = lighten(barColor);
	$: transitBarW   = (cfg.transit / maxBarVal) * barMaxW;
	$: walkBarW      = (cfg.walk    / maxBarVal) * barMaxW;

	$: colorScale = scaleThreshold()
		.domain(cfg.breaks)
		.range(cfg.colors);

	$: ct = ctData.features.map(f => ({
		...f,
		_color: f.properties[variable] != null
			? colorScale(f.properties[variable])
			: '#e0e0e0'
	}));

	const W   = 600;
	const H   = 420;
	const sw  = 44;   
	const sh  = 14;   
	const gap = 2;    
	const pad = 8;   
	const lx = W - 230;
	const ly = H - 110;

	$: projection = (() => {
		const proj = geoMercator().angle([-17]);
		proj.fitSize([W, H - 40], { type: 'FeatureCollection', features: ctData.features });
		return proj;
	})();

	$: path = geoPath(projection);

	$: lw = cfg.colors.length * (sw + gap) - gap + pad * 2;

	$: unit = cfg.suffix ?? '%';

</script>



<div class="wrap">
	<svg
		viewBox="0 0 {W} {H}"
		preserveAspectRatio="xMidYMid meet"
		style="width:100%; height:auto; display:block;"
	>

		<!-- Census tract fills -->
		{#each ct as feature}
			<path
				d={path(feature)}
				fill={feature._color}
				stroke="gray"
				stroke-width="0.2"
				opacity="0.8"
			/>
		{/each}

		<!-- TTC lines -->
		{#each ttcData.features as feature}
			<path
				d={path(feature)}
				fill="none"
				stroke="#333"
				stroke-width="2"
				opacity="0.8"
			/>
		{/each}

		<!-- Library dots -->
		{#each librariesData.features as feature}
			<circle
				cx={projection(feature.geometry.coordinates)[0]}
				cy={projection(feature.geometry.coordinates)[1]}
				r="3.5"
				fill="#015FC1"
				stroke="white"
				stroke-width="1.5"
			/>
		{/each}

		<!-- Legend title -->
	<text x={lx + lw/2} y={ly - 4} class="leg-title" text-anchor="middle">{cfg.label} ({unit})</text>
	
		<!-- Swatches -->
		{#each cfg.colors as color, i}
			<rect
				x={lx + pad + i * (sw + gap)}
				y={ly}
				width={sw} height={sh}
				fill={color} stroke="black" stroke-width="0.3"
			/>
		{/each}

		<!-- Break labels -->
		{#each cfg.breaks as brk, i}
			<text
				x={lx + pad + (i + 1) * (sw + gap) - gap}
				y={ly + sh + 11}
				class="leg-label" text-anchor="middle"
			>{brk}</text>
		{/each}


		<!-- Bar chart — bottom right empty space -->
		<rect x={8} y={H - 126} width={220} height={72}
		fill="white" fill-opacity="0" rx="3"/>
	<text x={14} y={H - 60} class="bar-title">Avg. travel time to nearest library</text>
	<text x={14} y={H - 44} class="bar-label">Walk + Transit</text>
	<rect x={84} y={H - 54} width={transitBarW} height={9} fill={barColor} rx="1"/>
	<text x={88 + transitBarW} y={H - 45} class="bar-label">{cfg.transit} min</text>
	<text x={14} y={H - 28} class="bar-label">Walking only</text>
	<rect x={84} y={H - 38} width={walkBarW} height={9} fill={barColorLight} rx="1"/>
	<text x={88 + walkBarW} y={H - 29} class="bar-label">{cfg.walk} min</text>
	<text x={14} y={H - 12} class="bar-label" style="fill:#aaa;">City avg — Transit: {CITY_AVG.transit} · Walk: {CITY_AVG.walk} min</text>
				
		<!-- North arrow — bottom right -->
		<g transform="translate({W - 10}, 55) rotate({-17})">
			<line x1="0" y1="10" x2="0" y2="-10" stroke="#333" stroke-width="1.5"/>
			<polygon points="0,-14 -3,-7 3,-7" fill="#333"/>
			<text y="20" text-anchor="middle" class="north-label">N</text>
		</g>

		<!-- Scale bar — bottom right -->
		<line x1={W - 60} y1={H - 204} x2={W - 20} y2={H - 204} stroke="#333" stroke-width="1.5"/>
		<line x1={W - 60} y1={H - 208} x2={W - 60} y2={H - 200} stroke="#333" stroke-width="1"/>
		<line x1={W - 20} y1={H - 208} x2={W - 20} y2={H - 200} stroke="#333" stroke-width="1"/>
		<text x={W - 60} y={H - 212} class="leg-label" text-anchor="start">0</text>
		<text x={W - 20} y={H - 212} class="leg-label" text-anchor="middle">5 km</text>

	</svg>
</div>



<style>

	.wrap { width: 100%; }

	.leg-title   { font-family: 'TradeGothicBold', sans-serif; font-size: 14px; fill: #222; }
	.leg-label   { font-family: 'OpenSans', sans-serif; font-size: 11px; fill: #444; }
	.north-label { font-family: 'OpenSans', sans-serif; font-size: 10px; font-weight: 700; fill: #333; }
	.bar-title { font-family: 'TradeGothicBold', sans-serif; font-size: 10px; fill: #222; }
	.bar-label { font-family: 'OpenSans', sans-serif; font-size: 9px; fill: #444; }

</style>
