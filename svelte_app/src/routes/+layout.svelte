<script lang="ts">
	import '../app.css';
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
			<nav class="nav" aria-label="주요 메뉴">
				<a href="/">홈 갤러리</a>
				<a href="/references/powerbi">레퍼런스</a>
				<a href="/powerbi">Power BI</a>
			</nav>
		</div>
	</header>
	<main class="page-shell">
		{@render children()}
	</main>
	<footer class="site-footer">Copyright © 2026 Snowball Impact. All rights reserved.</footer>
</div>
