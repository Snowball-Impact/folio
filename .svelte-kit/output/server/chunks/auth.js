import { t as getSupabaseClient } from "./supabase2.js";
//#region lib/authConsent.ts
function pendingPolicyConsentIdsFromUser(user) {
	const rawIds = user.user_metadata?.consented_policy_version_ids;
	if (!Array.isArray(rawIds)) return [];
	return [...new Set(rawIds.filter((policyId) => typeof policyId === "string").map((policyId) => policyId.trim()).filter(Boolean))];
}
//#endregion
//#region lib/auth.ts
async function currentSession() {
	const supabase = getSupabaseClient();
	if (!supabase) return null;
	const { data } = await supabase.auth.getSession();
	return data.session;
}
async function currentProfile(user) {
	const supabase = getSupabaseClient();
	const fallback = profileFromUser(user);
	if (!supabase) return fallback;
	const { data } = await supabase.from("profiles").select("id,email,name,organization,bio").eq("id", user.id).maybeSingle();
	if (!data) return fallback;
	return {
		id: String(data.id ?? user.id),
		email: String(data.email ?? user.email ?? ""),
		name: String(data.name ?? fallback.name),
		organization: nullableString(data.organization),
		bio: nullableString(data.bio)
	};
}
async function applyPendingPolicyConsents(user) {
	const supabase = getSupabaseClient();
	const policyIds = pendingPolicyConsentIdsFromUser(user);
	if (!supabase || policyIds.length === 0) return;
	const { data: existingData } = await supabase.from("user_policy_consents").select("policy_version_id").eq("user_id", user.id).in("policy_version_id", policyIds);
	const existingPolicyIds = new Set((Array.isArray(existingData) ? existingData : []).map((row) => String(row.policy_version_id ?? "")));
	const rows = policyIds.filter((policyId) => !existingPolicyIds.has(policyId)).map((policyId) => ({
		user_id: user.id,
		policy_version_id: policyId
	}));
	if (rows.length === 0) return;
	await supabase.from("user_policy_consents").insert(rows);
}
function profileFromUser(user) {
	const metadata = user.user_metadata ?? {};
	return {
		id: user.id,
		email: user.email ?? "",
		name: String(metadata.name ?? user.email?.split("@")[0] ?? "사용자"),
		organization: nullableString(metadata.organization),
		bio: null
	};
}
function nullableString(value) {
	return String(value ?? "").trim() || null;
}
//#endregion
export { currentProfile as n, currentSession as r, applyPendingPolicyConsents as t };
