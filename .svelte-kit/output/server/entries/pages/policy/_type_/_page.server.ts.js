import { redirect } from "@sveltejs/kit";
import { createClient } from "@supabase/supabase-js";
//#region routes/policy/[type]/+page.server.ts
var POLICY_LABELS = {
	privacy: "개인정보 처리방침",
	terms: "서비스 이용약관"
};
var load = async ({ params, url }) => {
	const queryType = url.searchParams.get("type");
	const routeType = params.type;
	const policyType = normalizePolicyType(routeType || queryType);
	if (!routeType && queryType === policyType) throw redirect(301, `/policy/${policyType}`);
	const { data, error } = await createClient("https://vfvcpxrmirlnsfdjuaaz.supabase.co", "sb_publishable_so5bInU80pmX1chi5Fi33A_ZWK3L3Hp", { auth: {
		autoRefreshToken: false,
		persistSession: false
	} }).from("policy_versions").select("policy_type,version,title,content,content_url,summary,effective_at").eq("is_active", true).eq("policy_type", policyType).order("effective_at", { ascending: false }).limit(1).maybeSingle();
	if (error) return emptyPolicy(policyType, "현재 정책 본문을 불러오지 못했습니다. 잠시 후 다시 시도하세요.");
	return {
		policyType,
		label: POLICY_LABELS[policyType],
		policy: data,
		error: data ? "" : "현재 표시할 정책 본문이 없습니다. 문의가 필요하면 admin@foilo.it.kr로 연락해 주세요."
	};
};
function normalizePolicyType(value) {
	return value === "terms" ? "terms" : "privacy";
}
function emptyPolicy(policyType, error) {
	return {
		policyType,
		label: POLICY_LABELS[policyType],
		policy: null,
		error
	};
}
//#endregion
export { load };
