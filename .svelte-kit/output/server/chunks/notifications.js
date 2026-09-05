import { t as getSupabaseClient } from "./supabase2.js";
import { r as currentSession } from "./auth.js";
//#region lib/notifications.ts
async function listNotifications(limit = 20) {
	const supabase = getSupabaseClient();
	const session = await currentSession();
	if (!supabase || !session) return {
		notifications: [],
		error: "로그인 후 알림을 확인할 수 있습니다."
	};
	const { data, error } = await supabase.from("notifications").select("id,user_id,actor_id,project_id,comment_id,type,title,body,is_read,read_at,created_at").eq("user_id", session.user.id).order("created_at", { ascending: false }).limit(limit);
	if (error) return {
		notifications: [],
		error: "알림을 불러오지 못했습니다. 잠시 후 다시 시도하세요."
	};
	return {
		notifications: (Array.isArray(data) ? data : []).map(normalizeNotification),
		error: ""
	};
}
async function countUnreadNotifications() {
	return (await listNotifications(50)).notifications.filter((notification) => !notification.is_read).length;
}
async function markAllNotificationsRead() {
	const supabase = getSupabaseClient();
	const session = await currentSession();
	if (!supabase || !session) return false;
	const { error } = await supabase.from("notifications").update({
		is_read: true,
		read_at: (/* @__PURE__ */ new Date()).toISOString()
	}).eq("user_id", session.user.id).eq("is_read", false);
	return !error;
}
function normalizeNotification(value) {
	const record = value && typeof value === "object" ? value : {};
	return {
		id: String(record.id ?? ""),
		user_id: String(record.user_id ?? ""),
		actor_id: nullableString(record.actor_id),
		project_id: nullableString(record.project_id),
		comment_id: nullableString(record.comment_id),
		type: "project_comment",
		title: String(record.title ?? "새 알림"),
		body: nullableString(record.body),
		is_read: Boolean(record.is_read ?? false),
		read_at: nullableString(record.read_at),
		created_at: String(record.created_at ?? "")
	};
}
function nullableString(value) {
	return String(value ?? "").trim() || null;
}
//#endregion
export { listNotifications as n, markAllNotificationsRead as r, countUnreadNotifications as t };
