<script lang="ts">
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import { onMount, tick } from 'svelte';
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
	let powerBiOpen = $state(false);
	let notificationOpen = $state(false);
	let powerBiMenuElement = $state<HTMLDivElement | null>(null);
	let notificationMenuElement = $state<HTMLDivElement | null>(null);
	let notificationSubmenuElement = $state<HTMLDivElement | null>(null);
	let notificationPopoverShift = $state(0);

	const pathname = $derived(page.url.pathname);
	const topic = $derived(page.url.searchParams.get('topic') ?? 'news');

	onMount(() => {
		const supabase = getSupabaseClient();
		const closeOnOutsideClick = (event: MouseEvent) => {
			if (!powerBiMenuElement?.contains(event.target as Node)) {
				powerBiOpen = false;
			}
			if (!notificationMenuElement?.contains(event.target as Node)) {
				notificationOpen = false;
			}
		};
		const closeOnEscape = (event: KeyboardEvent) => {
			if (event.key === 'Escape') {
				powerBiOpen = false;
				notificationOpen = false;
			}
		};
		document.addEventListener('click', closeOnOutsideClick);
		document.addEventListener('keydown', closeOnEscape);
		const syncNotificationsRead = () => {
			unreadCount = 0;
			notifications = notifications.map((notification) => ({
				...notification,
				is_read: true,
				read_at: notification.read_at ?? new Date().toISOString()
			}));
		};
		window.addEventListener('folio:notifications-read', syncNotificationsRead);
		currentSession().then(applySessionState);
		if (!supabase) {
			return () => {
				document.removeEventListener('click', closeOnOutsideClick);
				document.removeEventListener('keydown', closeOnEscape);
				window.removeEventListener('folio:notifications-read', syncNotificationsRead);
			};
		}
		const { data } = supabase.auth.onAuthStateChange(async (_event, value) => {
			await applySessionState(value);
		});
		return () => {
			document.removeEventListener('click', closeOnOutsideClick);
			document.removeEventListener('keydown', closeOnEscape);
		window.removeEventListener('folio:notifications-read', syncNotificationsRead);
			data.subscription.unsubscribe();
		};
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

	async function toggleNotifications(event: MouseEvent) {
		event.preventDefault();
		event.stopPropagation();
		if (!notificationOpen) {
			await refreshHeaderNotifications();
		}
		notificationOpen = !notificationOpen;
		if (notificationOpen) {
			await tick();
			positionNotificationPopover();
		}
	}

	async function togglePowerBi(event: MouseEvent) {
		event.preventDefault();
		event.stopPropagation();
		powerBiOpen = !powerBiOpen;
		if (powerBiOpen) {
			notificationOpen = false;
			await tick();
		}
	}

	function positionNotificationPopover() {
		if (!notificationSubmenuElement) {
			return;
		}
		const rect = notificationSubmenuElement.getBoundingClientRect();
		const margin = 12;
		const leftShift = rect.left < margin ? margin - rect.left : 0;
		const rightShift = rect.right > window.innerWidth - margin ? window.innerWidth - margin - rect.right : 0;
		notificationPopoverShift = leftShift || rightShift;
	}

	function closeNotifications() {
		notificationOpen = false;
	}

	async function openNotification(notification: NotificationItem) {
		notificationOpen = false;
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
		powerBiOpen = false;
	}
</script>

<nav class="nav" aria-label="주요 메뉴">
	<a class:active={isPathActive('/')} aria-current={isPathActive('/') ? 'page' : undefined} href="/">홈 갤러리</a>
	<a class:active={isPathActive('/about')} aria-current={isPathActive('/about') ? 'page' : undefined} href="/about">서비스 소개</a>
	<div bind:this={powerBiMenuElement} class="nav-menu powerbi-menu" class:open={powerBiOpen}>
		<button
			type="button"
			class="nav-menu-trigger"
			class:active={isPowerBiActive()}
			aria-current={isPowerBiActive() ? 'page' : undefined}
			aria-expanded={powerBiOpen}
			aria-haspopup="menu"
			onclick={togglePowerBi}
		>
			Power BI <span class="nav-caret" aria-hidden="true"></span>
		</button>
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
		<div bind:this={notificationMenuElement} class="nav-menu notification-menu" class:open={notificationOpen}>
			<button
				type="button"
				class="notification-link"
				class:active={isPathActive('/notifications')}
				aria-current={isPathActive('/notifications') ? 'page' : undefined}
				aria-expanded={notificationOpen}
				aria-haspopup="menu"
				onclick={toggleNotifications}
			>
				알림 <span class="nav-caret" aria-hidden="true"></span>
				{#if unreadCount > 0}
					<span aria-label={`${unreadCount}개 새 알림`}>N</span>
				{/if}
			</button>
			<div
				bind:this={notificationSubmenuElement}
				class="nav-submenu notification-submenu"
				class:open={notificationOpen}
				style={'--notification-popover-shift: ' + notificationPopoverShift + 'px'}
				aria-label="최근 알림"
				role="menu"
			>
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
				<a class="notification-popover-action" href="/notifications" onclick={closeNotifications}>모두 보기</a>
			</div>
		</div>
	{:else}
		<a class:active={isPathActive('/login')} aria-current={isPathActive('/login') ? 'page' : undefined} href="/login">로그인</a>
	{/if}
</nav>
