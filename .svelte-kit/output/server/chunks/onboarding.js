import { t as getSupabaseClient } from "./supabase2.js";
import { r as currentSession, t as applyPendingPolicyConsents } from "./auth.js";
//#region lib/onboarding.ts
var POLICY_ORDER = ["terms", "privacy"];
async function getActivePolicyVersions() {
	const supabase = getSupabaseClient();
	if (!supabase) return {
		policies: [],
		error: "Supabase 환경 변수가 설정되지 않았습니다."
	};
	const { data, error } = await supabase.from("policy_versions").select("id,policy_type,version,title,content,content_url,summary,effective_at").eq("is_active", true).order("effective_at", { ascending: false });
	if (error) return {
		policies: [],
		error: "정책 정보를 불러오지 못했습니다. 잠시 후 다시 시도하세요."
	};
	return {
		policies: latestPoliciesByType(data),
		error: ""
	};
}
async function getOnboardingStatus() {
	const supabase = getSupabaseClient();
	const session = await currentSession();
	if (!supabase || !session) return emptyStatus();
	await applyPendingPolicyConsents(session.user);
	const policyResult = await getActivePolicyVersions();
	if (policyResult.error) return errorStatus(policyResult.error);
	const policies = policyResult.policies;
	if (policies.length === 0) return {
		required: false,
		isComplete: true,
		policies: [],
		consentedPolicyIds: [],
		error: ""
	};
	const { data: consentData, error: consentError } = await supabase.from("user_policy_consents").select("policy_version_id").eq("user_id", session.user.id);
	if (consentError) return errorStatus("온보딩 정보를 불러오지 못했습니다. 잠시 후 다시 시도하세요.");
	const consentedPolicyIds = (Array.isArray(consentData) ? consentData : []).map((item) => String(item.policy_version_id ?? "")).filter(Boolean);
	return {
		required: true,
		isComplete: policies.map((policy) => policy.id).every((policyId) => consentedPolicyIds.includes(policyId)),
		policies,
		consentedPolicyIds,
		error: ""
	};
}
function latestPoliciesByType(value) {
	const rows = Array.isArray(value) ? value : [];
	const byType = /* @__PURE__ */ new Map();
	for (const item of rows) {
		const row = item;
		if ((row.policy_type === "terms" || row.policy_type === "privacy") && row.id && !byType.has(row.policy_type)) byType.set(row.policy_type, {
			id: String(row.id),
			policy_type: row.policy_type,
			version: String(row.version ?? ""),
			title: String(row.title ?? ""),
			content: nullableString(row.content),
			content_url: nullableString(row.content_url),
			summary: nullableString(row.summary),
			effective_at: String(row.effective_at ?? "")
		});
	}
	return POLICY_ORDER.map((policyType) => byType.get(policyType)).filter((policy) => Boolean(policy));
}
function emptyStatus() {
	return {
		required: false,
		isComplete: true,
		policies: [],
		consentedPolicyIds: [],
		error: ""
	};
}
function errorStatus(message) {
	return {
		required: true,
		isComplete: false,
		policies: [],
		consentedPolicyIds: [],
		error: message
	};
}
function nullableString(value) {
	return String(value ?? "").trim() || null;
}
//#endregion
export { getOnboardingStatus as n, getActivePolicyVersions as t };
