import type { RequiredPolicyType } from '$lib/policyRequirements';

export type PolicyVersionConsentRecord = {
	id: string;
	policy_type: RequiredPolicyType | string | null;
};

const UUID_PATTERN = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
const MAX_USER_AGENT_CHARS = 512;
const MAX_IP_CHARS = 45;

export function normalizePolicyVersionIds(value: unknown) {
	const items = Array.isArray(value) ? value : [];
	return [...new Set(items.map((item) => String(item ?? '').trim()).filter((item) => UUID_PATTERN.test(item)))];
}

export function consentEvidenceFromHeaders(headers: Headers) {
	return {
		ipAddress: clientIpFromHeaders(headers),
		userAgent: truncateHeader(headers.get('user-agent'), MAX_USER_AGENT_CHARS)
	};
}

export function policyConsentRows(userId: string, policyVersionIds: string[], headers: Headers) {
	const { ipAddress, userAgent } = consentEvidenceFromHeaders(headers);
	return policyVersionIds.map((policyVersionId) => ({
		user_id: userId,
		policy_version_id: policyVersionId,
		ip_address: ipAddress,
		user_agent: userAgent
	}));
}

export function latestRequiredPolicyVersions(value: unknown) {
	const rows = Array.isArray(value) ? (value as PolicyVersionConsentRecord[]) : [];
	const byType = new Map<RequiredPolicyType, PolicyVersionConsentRecord>();
	for (const row of rows) {
		if ((row.policy_type === 'terms' || row.policy_type === 'privacy') && row.id && !byType.has(row.policy_type)) {
			byType.set(row.policy_type, row);
		}
	}
	return [...byType.values()];
}

function clientIpFromHeaders(headers: Headers) {
	const candidates = [
		headers.get('cf-connecting-ip'),
		headers.get('true-client-ip'),
		headers.get('x-real-ip'),
		headers.get('x-forwarded-for')?.split(',')[0] ?? null
	];
	for (const candidate of candidates) {
		const ip = normalizeIp(candidate);
		if (ip) {
			return ip;
		}
	}
	return null;
}

function normalizeIp(value: string | null) {
	const candidate = value?.trim().replace(/^\[|\]$/g, '') ?? '';
	if (!candidate || candidate.length > MAX_IP_CHARS || /\s/.test(candidate)) {
		return null;
	}
	if (!/^[0-9a-f:.]+$/i.test(candidate) || (!candidate.includes('.') && !candidate.includes(':'))) {
		return null;
	}
	return candidate;
}

function truncateHeader(value: string | null, maxChars: number) {
	const text = value?.trim() ?? '';
	return text ? text.slice(0, maxChars) : null;
}
