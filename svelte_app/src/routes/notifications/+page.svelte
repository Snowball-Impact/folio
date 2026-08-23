<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { currentSession } from '$lib/auth';
	import {
		listNotifications,
		markAllNotificationsRead,
		markNotificationRead,
		type NotificationItem
	} from '$lib/notifications';
	import { formatDate } from '$lib/format';

	let notifications = $state<NotificationItem[]>([]);
	let loading = $state(true);
	let message = $state('');
	let error = $state('');
	const unreadCount = $derived(notifications.filter((notification) => !notification.is_read).length);

	onMount(async () => {
		const session = await currentSession();
		if (!session) {
			await goto('/login?next=/notifications');
			return;
		}
		await refreshNotifications();
	});

	async function refreshNotifications() {
		loading = true;
		const result = await listNotifications();
		notifications = result.notifications;
		error = result.error;
		loading = false;
	}

	async function openProject(notification: NotificationItem) {
		if (!notification.project_id) {
			return;
		}
		await markNotificationRead(notification.id);
		await goto(`/projects/${notification.project_id}`);
	}

	async function markAllRead() {
		message = '';
		error = '';
		const ok = await markAllNotificationsRead();
		if (!ok) {
			error = '알림 읽음 처리에 실패했습니다. 잠시 후 다시 시도하세요.';
			return;
		}
		message = '모든 알림을 읽음 처리했습니다.';
		notifications = notifications.map((notification) => ({
			...notification,
			is_read: true,
			read_at: notification.read_at ?? new Date().toISOString()
		}));
	}
</script>

<svelte:head>
	<title>알림 | FOLIO</title>
	<meta name="description" content="FOLIO 프로젝트 댓글 알림을 확인합니다." />
</svelte:head>

<section class="notification-hero">
	<div>
		<div class="eyebrow">Notifications</div>
		<h1>알림</h1>
		<p>내 프로젝트에 새로 들어온 반응을 확인하세요.</p>
	</div>
	<div class="notification-count-card">
		<span>새 알림</span>
		<strong>{unreadCount}</strong>
	</div>
</section>

<section class="notifications-panel">
	<div class="section-header">
		<div>
			<h2>최근 알림</h2>
			<p>프로젝트 보기 또는 모두 읽음으로 알림 상태를 정리할 수 있습니다.</p>
		</div>
		{#if unreadCount > 0}
			<button type="button" onclick={markAllRead}>모두 읽음</button>
		{/if}
	</div>

	{#if message}
		<div class="auth-message success">{message}</div>
	{/if}
	{#if error}
		<div class="auth-message error">{error}</div>
	{/if}

	{#if loading}
		<div class="comments-empty">알림을 불러오는 중입니다.</div>
	{:else if notifications.length === 0}
		<div class="comments-empty">아직 알림이 없습니다.</div>
	{:else}
		<div class="notification-list">
			{#each notifications as notification}
				<article class="notification-item" class:read={notification.is_read}>
					<div>
						<span>{notification.is_read ? '읽음' : '새 알림'}</span>
						<strong>{notification.title}</strong>
						{#if notification.body}
							<p>{notification.body}</p>
						{/if}
						<time>{formatDate(notification.created_at)}</time>
					</div>
					{#if notification.project_id}
						<button type="button" onclick={() => openProject(notification)}>프로젝트 보기</button>
					{/if}
				</article>
			{/each}
		</div>
	{/if}
</section>
