<script lang="ts">
	import '../app.css';
	import { page } from '$app/state';
	import { afterNavigate } from '$app/navigation';
	import { onMount } from 'svelte';
	import AuthNav from '$lib/components/AuthNav.svelte';
	import { initGoogleAnalytics } from '$lib/googleAnalytics';
	import PolicyConsentGate from '$lib/components/PolicyConsentGate.svelte';
	import { initRum } from '$lib/rum';

	let { children } = $props();
	const isThumbnailCapture = $derived(page.url.searchParams.get('capture') === 'thumbnail');

	initGoogleAnalytics();

	let isFirstNavigation = true;
	afterNavigate(() => {
		if (isFirstNavigation) {
			isFirstNavigation = false;
			return;
		}
		if (typeof window !== 'undefined' && typeof (window as unknown as { fbq?: (...args: unknown[]) => void }).fbq === 'function') {
			(window as unknown as { fbq: (...args: unknown[]) => void }).fbq('track', 'PageView');
		}
	});

	onMount(() => {
		initRum();
	});
</script>

<svelte:head>
	<link rel="icon" href="/favicon.ico" sizes="any" />
	<link rel="icon" href="/favicon.png" type="image/png" />
	<link rel="apple-touch-icon" href="/apple-touch-icon.png" />
	<meta property="og:type" content="website" />
	<meta property="og:site_name" content="FOLIO" />
	<meta property="og:title" content="FOLIO | 데이터 시각화 커뮤니티" />
	<meta property="og:description" content="올리면 만나요, 폴리오. 좋은 데이터 시각화 프로젝트를 발견하고 직접 경험하는 커뮤니티" />
	<meta property="og:image" content="/og.png" />
	<meta property="og:image:width" content="1920" />
	<meta property="og:image:height" content="1080" />
	<meta name="twitter:card" content="summary_large_image" />
	<meta name="twitter:title" content="FOLIO | 데이터 시각화 커뮤니티" />
	<meta name="twitter:description" content="올리면 만나요, 폴리오. 좋은 데이터 시각화 프로젝트를 발견하고 직접 경험하는 커뮤니티" />
	<meta name="twitter:image" content="/og.png" />
</svelte:head>

<div class="app-shell">
	{#if !isThumbnailCapture}
		<PolicyConsentGate />
	{/if}
	{#if !isThumbnailCapture}
		<header class="site-header">
			<div class="site-header-inner">
				<a class="brand" href="/" aria-label="FOLIO 홈으로 이동">
					<img src="/logo.webp" alt="FOLIO" />
				</a>
				<AuthNav />
			</div>
		</header>
	{/if}
	<main class="page-shell" class:thumbnail-capture-page={isThumbnailCapture}>
		{@render children()}
	</main>
	{#if !isThumbnailCapture}
		<footer class="site-footer">
			<div class="site-footer-inner">
				<span>Copyright © 2026 Snowball Impact. All rights reserved.</span>
				<span class="site-footer-version">v2026.09.09.01</span>
				<nav aria-label="푸터 링크">
					<a href="/policy/terms">이용약관</a>
					<a href="/policy/privacy">개인정보 처리방침</a>
					<a href="mailto:contact@snowballimpact.com?subject=FOLIO%20%EC%84%9C%EB%B9%84%EC%8A%A4%20%EB%AC%B8%EC%9D%98">문의</a>
				</nav>
			</div>
		</footer>
	{/if}
</div>
