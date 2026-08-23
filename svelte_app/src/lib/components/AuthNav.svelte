<script lang="ts">
	import { onDestroy, onMount } from 'svelte';
	import type { Session } from '@supabase/supabase-js';
	import { currentProfile, currentSession, signOut, type AuthProfile } from '$lib/auth';
	import { countUnreadNotifications } from '$lib/notifications';
	import { getSupabaseClient } from '$lib/supabase';

	let session = $state<Session | null>(null);
	let profile = $state<AuthProfile | null>(null);
	let unreadCount = $state(0);

	onMount(() => {
		const supabase = getSupabaseClient();
		currentSession().then(async (value) => {
			session = value;
			profile = value?.user ? await currentProfile(value.user) : null;
			unreadCount = value?.user ? await countUnreadNotifications() : 0;
		});
		if (!supabase) {
			return;
		}
		const { data } = supabase.auth.onAuthStateChange(async (_event, value) => {
			session = value;
			profile = value?.user ? await currentProfile(value.user) : null;
			unreadCount = value?.user ? await countUnreadNotifications() : 0;
		});
		return () => data.subscription.unsubscribe();
	});

	onDestroy(() => {
		profile = null;
	});

	async function handleSignOut() {
		await signOut();
		session = null;
		profile = null;
		unreadCount = 0;
	}
</script>

<nav class="nav" aria-label="주요 메뉴">
	<a href="/">홈 갤러리</a>
	<a href="/references/powerbi">레퍼런스</a>
	<a href="/powerbi">Power BI</a>
	{#if session}
		<a href="/submit">프로젝트 등록</a>
		<a href="/my">마이 페이지</a>
		<a class="notification-link" href="/notifications">
			알림
			{#if unreadCount > 0}
				<span>{unreadCount}</span>
			{/if}
		</a>
		<span class="nav-user">{profile?.name ?? session.user.email}</span>
		<button type="button" onclick={handleSignOut}>로그아웃</button>
	{:else}
		<a href="/login">로그인</a>
		<a href="/signup">회원가입</a>
	{/if}
</nav>
