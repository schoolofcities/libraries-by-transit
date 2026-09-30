// Single source for per-demographic map colors/breaks and the
// population-weighted travel-time stats used across ChoroplethMap, SwipeMap,
// and DotPlot.
//
// These values come from the Python analysis pipeline — specifically the
// "Quartile breaks" print in the census-tract aggregation cell and the
// "For DotPlot.svelte" print in the weighted-stats cell. When you rerun the
// notebook and the numbers shift, update them here once rather than in each
// component.

export const CITY_AVG = {
	transit: 16.9,
	walk: 20.9,
};

export const DEMOGRAPHICS = [
	{
		id: 'visible_minority_pct',
		label: 'Visible Minority',
		colors: ['#F0E9F1', '#C4A7C9', '#9865A1', '#6D247A'],
		breaks: [31.4, 52.1, 74.4],
		transit: 17.3,
		walk: 21.8,
	},
	{
		id: 'low_income_pct',
		label: 'Low Income',
		colors: ['#E5F2F5', '#99CBDA', '#4CA5BE', '#007FA3'],
		breaks: [28.0, 34.1, 37.8],
		transit: 16.9,
		walk: 21.1,
	},
	{
		id: 'first_gen_immigrants_pct',
		label: 'First Gen. Immigrants',
		colors: ['#E5F5F3', '#99D9CF', '#4CBDAC', '#00A189'],
		breaks: [37.6, 52.9, 63.3],
		transit: 17.2,
		walk: 21.5,
	},
	{
		id: 'seniors_pct',
		label: 'Seniors (65+)',
		colors: ['#E8EBEF', '#A5AFC1', '#617393', '#1E3765'],
		breaks: [14.1, 17.0, 20.4],
		transit: 17.3,
		walk: 21.6,
	},
	{
		id: 'children_pct',
		label: 'Children (0–14)',
		colors: ['#F3F8EA', '#D1E5AB', '#AFD26C', '#8DBF2E'],
		breaks: [11.7, 14.1, 16.3],
		transit: 17.1,
		walk: 21.3,
	},
];

// pop_density uses a different color ramp and unit than the %-of-population
// variables above, and isn't shown in SwipeMap or DotPlot — kept separate so
// it doesn't have to be filtered out of DEMOGRAPHICS everywhere it's used.
export const POP_DENSITY = {
	id: 'pop_density',
	label: 'Population Density',
	colors: ['#FBECEA', '#F1B5AD', '#E67D70', '#DC4633'],
	breaks: [3411, 5722, 9245],
	suffix: 'ppl/km²',
	transit: CITY_AVG.transit,
	walk: CITY_AVG.walk,
};

// All choropleth variables, in the order StaticMaps displays them.
export const ALL_VARIABLE_IDS = ['pop_density', ...DEMOGRAPHICS.map(d => d.id)];

// Lookup by variable id — used by ChoroplethMap, which receives `variable`
// as a prop and needs the full config object for it.
export const VARIABLES_BY_ID = Object.fromEntries(
	[...DEMOGRAPHICS, POP_DENSITY].map(v => [v.id, v])
);

// { label, transit, walk } for every group including Total Population —
// the shape DotPlot.svelte renders directly.
export const DOTPLOT_DATA = [
	...DEMOGRAPHICS.map(({ label, transit, walk }) => ({ label, transit, walk })),
	{ label: 'Total Population', transit: CITY_AVG.transit, walk: CITY_AVG.walk },
];
