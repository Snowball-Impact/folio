<script lang="ts">
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import { onMount } from 'svelte';
	import { getPolicyConsentStatus } from '$lib/onboarding';
	import { safeInternalNextPath } from '$lib/navigation';
	import { getSupabaseClient } from '$lib/supabase';

	const exemptPrefixes = ['/login', '/signup', '/reset-password', '/policy'];
	let checking = false;
	let mounted = $state(false);
	onMount(() => {
		mounted = true;
		void checkConsent();
		const subscription = getSupabaseClient()?.auth.onAuthStateChange(() => void checkConsent()).data.subscription;
		return () => { mounted = false; subscription?.unsubscribe(); };
	});
	$effect(() => { page.url.pathname; if (mounted) void checkConsent(); });
	async function checkConsent() {
		const pathname = page.url.pathname;
		if (checking || exemptPrefixes.some((prefix) => pathname === prefix || pathname.startsWith(`${prefix}/`))) return;
		checking = true;
		const status = await getPolicyConsentStatus();
		checking = false;
		if (status.required && !status.isComplete) await goto(`/policy/consent?next=${encodeURIComponent(safeInternalNextPath(`${pathname}${page.url.search}`))}`);
	}
</script>
