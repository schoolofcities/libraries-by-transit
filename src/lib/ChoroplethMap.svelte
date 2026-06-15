<script>

	import { geoPath, geoMercator, scaleThreshold } from "d3";
	import ctData from "../assets/census_tracts_demographics.geo.json";

	export let variable = 'visible_minority_pct';

	const config = {
		visible_minority_pct: {
			name: 'Visible Minority',
			breaks: [31.4, 52.1, 74.4],
			colors: ['#F0E9F1','#C4A7C9','#9865A1','#6D247A'],
			transit: 16.9, walk: 21.7,
		},
		low_income_pct: {
			name: 'Low Income',
			breaks: [28.0, 34.1, 37.8],
			colors: ['#FBECEA','#F1B5AD','#E67D70','#DC4633'],
			transit: 16.5, walk: 20.9,
		},
		recent_immigrants_pct: {
			name: 'Recent Immigrants (last 10 yrs)',
			breaks: [3.2, 5.6, 8.3],
			colors: ['#E5F2F5','#99CBDA','#4CA5BE','#007FA3'],
			transit: 16.1, walk: 20.5,
		},
		first_gen_immigrants_pct: {
			name: 'First Generation Immigrants',
			breaks: [37.6, 52.9, 63.3],
			colors: ['#E5F5F3','#99D9CF','#4CBDAC','#00A189'],
			transit: 16.7, walk: 21.4,
		},
		seniors_pct: {
			name: 'Seniors (65+)',
			breaks: [14.1, 17.0, 20.4],
			colors: ['#E8EBEF','#A5AFC1','#617393','#1E3765'],
			transit: 16.8, walk: 21.4,
		},
		children_pct: {
			name: 'Children (0–14)',
			breaks: [11.7, 14.1, 16.3],
			colors: ['#F3F8EA','#D1E5AB','#AFD26C','#8DBF2E'],
			transit: 16.7, walk: 21.1,
		},
	};

	const totalTransit = 16.4;
	const totalWalk    = 20.7;
	const maxBarVal    = 26;
	const barMaxW      = 150;  // SVG units for max bar width

	function lighten(hex) {
		const r = parseInt(hex.slice(1,3), 16);
		const g = parseInt(hex.slice(3,5), 16);
		const b = parseInt(hex.slice(5,7), 16);
		const mix = (c) => Math.round(255 + (c - 255) * 0.4);
		return 'rgb(' + mix(r) + ',' + mix(g) + ',' + mix(b) + ')';
	}

	$: barColor      = cfg.colors[cfg.colors.length - 1];
	$: barColorLight = lighten(barColor);
	$: transitBarW   = (cfg.transit / maxBarVal) * barMaxW;
	$: walkBarW      = (cfg.walk    / maxBarVal) * barMaxW;

	$: cfg = config[variable];

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
	const sw  = 44;   // was 32
	const sh  = 14;   // was 11
	const gap = 2;    // was 1
	const pad = 8;    // was 6
	const lx = W - 230;
	const ly = H - 110;

	$: projection = (() => {
		const proj = geoMercator().angle([-17]);
		proj.fitSize([W, H - 40], { type: 'FeatureCollection', features: ctData.features });
		return proj;
	})();

	$: path = geoPath(projection);

	$: lw = cfg.colors.length * (sw + gap) - gap + pad * 2;

	$: legendLabels = [
		`<${cfg.breaks[0]}%`,
		...cfg.breaks.slice(0, -1).map((b, i) => `${b}–${cfg.breaks[i + 1]}%`),
		`>${cfg.breaks[cfg.breaks.length - 1]}%`,
	];

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

		<!-- Legend title -->
	<text x={lx + lw / 2} y={ly - 4} class="leg-title" text-anchor="middle">{cfg.name}</text>

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
			>{brk}%</text>
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
	<text x={14} y={H - 12} class="bar-label" style="fill:#aaa;">City avg — Transit: {totalTransit} · Walk: {totalWalk} min</text>
				
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

	.leg-title   { font-family: 'TradeGothicBold', Arial, sans-serif; font-size: 14px; fill: #222; }
	.leg-label   { font-family: 'OpenSans', Arial, sans-serif; font-size: 11px; fill: #444; }
	.north-label { font-family: 'OpenSans', Arial, sans-serif; font-size: 10px; font-weight: 700; fill: #333; }
	.bar-title { font-family: 'TradeGothicBold', Arial, sans-serif; font-size: 10px; fill: #222; }
	.bar-label { font-family: 'OpenSans', Arial, sans-serif; font-size: 9px; fill: #444; }
	.bar-note  { font-family: 'OpenSans', Arial, sans-serif; font-size: 8px; fill: #aaa; }

</style>
