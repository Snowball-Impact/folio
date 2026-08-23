<script lang="ts">
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import { onMount } from 'svelte';
	import { getSupabaseClient } from '$lib/supabase';
	import { getOnboardingStatus } from '$lib/onboarding';

	const PUBLIC_AUTH_PATHS = new Set(['/login', '/signup', '/reset-password', '/onboarding']);
	let checking = false;

	onMount(() => {
		void checkOnboarding();
		const supabase = getSupabaseClient();
		if (!supabase) {
			return;
		}
		const { data } = supabase.auth.onAuthStateChange(() => {
			void checkOnboarding();
		});
		return () => data.subscription.unsubscribe();
	});

	$effect(() => {
		if (typeof window !== 'undefined') {
			void checkOnboarding();
		}
	});

	async function checkOnboarding() {
		const path = page.url.pathname;
		if (checking || PUBLIC_AUTH_PATHS.has(path)) {
			return;
		}

		checking = true;
		const status = await getOnboardingStatus();
		checking = false;
		if (status.required && !status.isComplete) {
			await goto(`/onboarding?next=${encodeURIComponent(page.url.pathname + page.url.search)}`);
		}
	}
</script>
