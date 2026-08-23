import { currentSession } from '$lib/auth';
import { getSupabaseClient } from '$lib/supabase';

export type NotificationItem = {
	id: string;
	user_id: string;
	actor_id: string | null;
	project_id: string | null;
	comment_id: string | null;
	type: 'project_comment';
	title: string;
	body: string | null;
	is_read: boolean;
	read_at: string | null;
	created_at: string;
};

export async function listNotifications(limit = 20) {
	const supabase = getSupabaseClient();
	const session = await currentSession();
	if (!supabase || !session) {
		return { notifications: [], error: '로그인 후 알림을 확인할 수 있습니다.' };
	}

	const { data, error } = await supabase
		.from('notifications')
		.select('id,user_id,actor_id,project_id,comment_id,type,title,body,is_read,read_at,created_at')
		.eq('user_id', session.user.id)
		.order('created_at', { ascending: false })
		.limit(limit);
	if (error) {
		return { notifications: [], error: '알림을 불러오지 못했습니다. 잠시 후 다시 시도하세요.' };
	}

	return {
		notifications: (Array.isArray(data) ? data : []).map(normalizeNotification),
		error: ''
	};
}

export async function countUnreadNotifications() {
	const result = await listNotifications(50);
	return result.notifications.filter((notification) => !notification.is_read).length;
}

export async function markNotificationRead(notificationId: string) {
	const supabase = getSupabaseClient();
	const session = await currentSession();
	if (!supabase || !session) {
		return false;
	}

	const { error } = await supabase
		.from('notifications')
		.update({ is_read: true, read_at: new Date().toISOString() })
		.eq('id', notificationId)
		.eq('user_id', session.user.id);
	return !error;
}

export async function markAllNotificationsRead() {
	const supabase = getSupabaseClient();
	const session = await currentSession();
	if (!supabase || !session) {
		return false;
	}

	const { error } = await supabase
		.from('notifications')
		.update({ is_read: true, read_at: new Date().toISOString() })
		.eq('user_id', session.user.id)
		.eq('is_read', false);
	return !error;
}

function normalizeNotification(value: unknown): NotificationItem {
	const record = value && typeof value === 'object' ? (value as Record<string, unknown>) : {};
	return {
		id: String(record.id ?? ''),
		user_id: String(record.user_id ?? ''),
		actor_id: nullableString(record.actor_id),
		project_id: nullableString(record.project_id),
		comment_id: nullableString(record.comment_id),
		type: 'project_comment',
		title: String(record.title ?? '새 알림'),
		body: nullableString(record.body),
		is_read: Boolean(record.is_read ?? false),
		read_at: nullableString(record.read_at),
		created_at: String(record.created_at ?? '')
	};
}

function nullableString(value: unknown) {
	const text = String(value ?? '').trim();
	return text || null;
}
