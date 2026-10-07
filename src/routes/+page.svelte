<script>
	import { base } from '$app/paths';
	import '../assets/global-styles.css';
</script>

<svelte:head>
	<title>Libraries by transit | School of Cities</title>
</svelte:head>

<main>
	<a href="{base}/toronto-proximity">Spatial access to public libraries</a>
	<a href="{base}/toronto-tour">Visit every Toronto library by transit</a>
</main>

<style>
	main {
		min-height: 100vh;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		gap: 1.5rem;
		font-family: TradeGothic, sans-serif;
		font-size: 1.5rem;
	}

	a {
		color: inherit;
	}
</style>
