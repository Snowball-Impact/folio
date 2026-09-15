import type { RequiredPolicyType } from '$lib/policyRequirements';

const UUID_PATTERN = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

export function normalizePolicyVersionIds(value: unknown) {
	return [...new Set((Array.isArray(value) ? value : []).map(String).map((value) => value.trim()).filter((value) => UUID_PATTERN.test(value)))];
}

export function policyConsentRows(userId: string, policyVersionIds: string[], headers: Headers) {
	const ipAddress = [headers.get('cf-connecting-ip'), headers.get('true-client-ip'), headers.get('x-real-ip'), headers.get('x-forwarded-for')?.split(',')[0]]
		.map((value) => value?.trim().replace(/^\[|\]$/g, '') ?? '')
		.find((value) => value.length <= 45 && /^[0-9a-f:.]+$/i.test(value) && (value.includes('.') || value.includes(':'))) || null;
	const userAgent = headers.get('user-agent')?.trim().slice(0, 512) || null;
	return policyVersionIds.map((policyVersionId) => ({ user_id: userId, policy_version_id: policyVersionId, ip_address: ipAddress, user_agent: userAgent }));
}

export function latestRequiredPolicyVersions(value: unknown) {
	const byType = new Map<RequiredPolicyType, { id: string; policy_type: RequiredPolicyType }>();
	for (const row of Array.isArray(value) ? value : []) {
		const item = row as { id?: unknown; policy_type?: unknown };
		if ((item.policy_type === 'terms' || item.policy_type === 'privacy') && item.id && !byType.has(item.policy_type)) {
			byType.set(item.policy_type, { id: String(item.id), policy_type: item.policy_type });
		}
	}
	return [...byType.values()];
}
