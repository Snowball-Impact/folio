<script lang="ts">
	import '../app.css';
	import AuthNav from '$lib/components/AuthNav.svelte';
	import OnboardingGate from '$lib/components/OnboardingGate.svelte';

	let { children } = $props();
</script>

<svelte:head>
	<link rel="icon" href="/logo.webp" />
</svelte:head>

<div class="app-shell">
	<OnboardingGate />
	<header class="site-header">
		<div class="site-header-inner">
			<a class="brand" href="/" aria-label="FOLIO 홈으로 이동">
				<img src="/logo.webp" alt="FOLIO" />
			</a>
			<AuthNav />
		</div>
	</header>
	<main class="page-shell">
		{@render children()}
	</main>
	<footer class="site-footer">
		<div class="site-footer-inner">
			<span>Copyright © 2026 Snowball Impact. All rights reserved.</span>
			<span class="site-footer-version">v2026.08.24.01</span>
			<nav aria-label="푸터 링크">
				<a href="/policy/terms">이용약관</a>
				<a href="/policy/privacy">개인정보 처리방침</a>
				<a href="mailto:contact@snowballimpact.com?subject=FOLIO%20%EC%84%9C%EB%B9%84%EC%8A%A4%20%EB%AC%B8%EC%9D%98">문의</a>
			</nav>
		</div>
	</footer>
</div>
