<script lang="ts">
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import { onMount } from 'svelte';
	import type { Session } from '@supabase/supabase-js';
	import { currentSession, signOut } from '$lib/auth';
	import {
		countUnreadNotifications,
		listNotifications,
		markAllNotificationsRead,
		markNotificationRead,
		type NotificationItem
	} from '$lib/notifications';
	import { getSupabaseClient } from '$lib/supabase';

	let session = $state<Session | null>(null);
	let unreadCount = $state(0);
	let notifications = $state<NotificationItem[]>([]);

	const pathname = $derived(page.url.pathname);
	const topic = $derived(page.url.searchParams.get('topic') ?? 'news');

	onMount(() => {
		const supabase = getSupabaseClient();
		currentSession().then(applySessionState);
		if (!supabase) {
			return;
		}
		const { data } = supabase.auth.onAuthStateChange(async (_event, value) => {
			await applySessionState(value);
		});
		return () => data.subscription.unsubscribe();
	});

	async function applySessionState(value: Session | null) {
		session = value;
		if (!value?.user) {
			unreadCount = 0;
			notifications = [];
			return;
		}
		await refreshHeaderNotifications();
	}

	async function refreshHeaderNotifications() {
		unreadCount = await countUnreadNotifications();
		const result = await listNotifications(5);
		notifications = result.notifications;
	}

	function isPathActive(target: string) {
		if (target === '/') {
			return pathname === '/';
		}
		return pathname === target || pathname.startsWith(`${target}/`);
	}

	function isPowerBiActive() {
		return pathname === '/powerbi' || pathname === '/references/powerbi';
	}

	function isPowerBiTopicActive(targetTopic: string) {
		return pathname === '/powerbi' && topic === targetTopic;
	}

	async function openNotification(notification: NotificationItem) {
		if (!notification.project_id) {
			await goto('/notifications');
			return;
		}
		await markNotificationRead(notification.id);
		await goto(`/projects/${notification.project_id}`);
	}

	async function markAllHeaderNotificationsRead() {
		const ok = await markAllNotificationsRead();
		if (ok) {
			notifications = notifications.map((notification) => ({
				...notification,
				is_read: true,
				read_at: notification.read_at ?? new Date().toISOString()
			}));
			unreadCount = 0;
		}
	}

	async function handleSignOut() {
		await signOut();
		session = null;
		unreadCount = 0;
		notifications = [];
	}
</script>

<nav class="nav" aria-label="주요 메뉴">
	<a class:active={isPathActive('/')} aria-current={isPathActive('/') ? 'page' : undefined} href="/">홈 갤러리</a>
	<a class:active={isPathActive('/about')} aria-current={isPathActive('/about') ? 'page' : undefined} href="/about">서비스 소개</a>
	<div class="nav-menu">
		<a class:active={isPowerBiActive()} aria-current={isPowerBiActive() ? 'page' : undefined} href="/powerbi">Power BI</a>
		<div class="nav-submenu" aria-label="Power BI 콘텐츠 메뉴">
			<a class:active={isPowerBiTopicActive('news')} href="/powerbi">업데이트 소식</a>
			<a class:active={isPowerBiTopicActive('community')} href="/powerbi?topic=community">커뮤니티 소식</a>
			<a class:active={isPowerBiTopicActive('learning')} href="/powerbi?topic=learning">학습 콘텐츠</a>
			<a class:active={isPowerBiTopicActive('certifications')} href="/powerbi?topic=certifications">자격증</a>
			<a class:active={pathname === '/references/powerbi'} href="/references/powerbi">레퍼런스</a>
		</div>
	</div>
	<a class:active={isPathActive('/submit')} aria-current={isPathActive('/submit') ? 'page' : undefined} href="/submit">프로젝트 등록</a>
	{#if session}
		<a class:active={isPathActive('/my')} aria-current={isPathActive('/my') ? 'page' : undefined} href="/my">마이 페이지</a>
		<button type="button" onclick={handleSignOut}>로그아웃</button>
		<div class="nav-menu notification-menu">
			<a class="notification-link" class:active={isPathActive('/notifications')} aria-current={isPathActive('/notifications') ? 'page' : undefined} href="/notifications">
				알림
				{#if unreadCount > 0}
					<span aria-label={`${unreadCount}개 새 알림`}>N</span>
				{/if}
			</a>
			<div class="nav-submenu notification-submenu" aria-label="최근 알림">
				<div class="notification-popover-title">
					<strong>알림</strong>
					<span>{unreadCount}개 새 알림</span>
				</div>
				{#if notifications.length === 0}
					<p class="notification-popover-empty">아직 알림이 없습니다.</p>
				{:else}
					{#each notifications as notification}
						<button type="button" class="notification-preview" onclick={() => openNotification(notification)}>
							<span>{notification.is_read ? '읽음' : '새 알림'}</span>
							<strong>{notification.title}</strong>
						</button>
					{/each}
				{/if}
				{#if unreadCount > 0}
					<button type="button" class="notification-popover-action" onclick={markAllHeaderNotificationsRead}>모두 읽음</button>
				{/if}
				<a class="notification-popover-action" href="/notifications">모두 보기</a>
			</div>
		</div>
	{:else}
		<a class:active={isPathActive('/login')} aria-current={isPathActive('/login') ? 'page' : undefined} href="/login">로그인</a>
	{/if}
</nav>