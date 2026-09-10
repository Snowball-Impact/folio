<script lang="ts">
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import { onMount } from 'svelte';
	import { getPolicyConsentStatus } from '$lib/onboarding';
	import { safeInternalNextPath } from '$lib/navigation';
	import { getSupabaseClient } from '$lib/supabase';

	const EXEMPT_PATH_PREFIXES = ['/login', '/signup', '/reset-password', '/policy'];

	let checking = false;
	let mounted = $state(false);

	onMount(() => {
		mounted = true;
		void checkConsent(page.url.pathname, `${page.url.pathname}${page.url.search}`);
		const supabase = getSupabaseClient();
		const subscription = supabase?.auth.onAuthStateChange(() => {
			void checkConsent(page.url.pathname, `${page.url.pathname}${page.url.search}`);
		}).data.subscription;
		return () => {
			mounted = false;
			subscription?.unsubscribe();
		};
	});

	$effect(() => {
		const pathname = page.url.pathname;
		const pathWithSearch = `${page.url.pathname}${page.url.search}`;
		if (mounted) {
			void checkConsent(pathname, pathWithSearch);
		}
	});

	async function checkConsent(pathname: string, pathWithSearch: string) {
		if (checking || isExemptPath(pathname)) {
			return;
		}
		checking = true;
		const status = await getPolicyConsentStatus();
		checking = false;
		if (status.required && !status.isComplete) {
			const next = safeInternalNextPath(pathWithSearch);
			await goto(`/policy/consent?next=${encodeURIComponent(next)}`);
		}
	}

	function isExemptPath(pathname: string) {
		return EXEMPT_PATH_PREFIXES.some((prefix) => pathname === prefix || pathname.startsWith(`${prefix}/`));
	}
</script>
