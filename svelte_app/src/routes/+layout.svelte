<script lang="ts">
	import '../app.css';
	import AuthNav from '$lib/components/AuthNav.svelte';
	import favicon from '$lib/assets/favicon.svg';

	let { children } = $props();
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

<div class="app-shell">
	<header class="site-header">
		<div class="site-header-inner">
			<a class="brand" href="/">FOLIO</a>
			<AuthNav />
		</div>
	</header>
	<main class="page-shell">
		{@render children()}
	</main>
	<footer class="site-footer">Copyright © 2026 Snowball Impact. All rights reserved.</footer>
</div>
