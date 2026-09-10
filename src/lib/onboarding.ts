import type { Session } from '@supabase/supabase-js';
import { currentSession } from '$lib/auth';
import { requiredPolicyAvailabilityMessage } from '$lib/policyRequirements';
import { getSupabaseClient } from '$lib/supabase';

export type PolicyType = 'terms' | 'privacy';

export type PolicyVersion = {
	id: string;
	policy_type: PolicyType;
	version: string;
	title: string;
	content: string | null;
	content_url: string | null;
	summary: string | null;
	effective_at: string;
};

export type PolicyConsentStatus = {
	required: boolean;
	isComplete: boolean;
	policies: PolicyVersion[];
	consentedPolicyIds: string[];
	error: string;
};

const POLICY_ORDER: PolicyType[] = ['terms', 'privacy'];

export async function getActivePolicyVersions() {
	const supabase = getSupabaseClient();
	if (!supabase) {
		return { policies: [], error: 'Supabase 환경 변수가 설정되지 않았습니다.' };
	}

	const { data, error } = await supabase
		.from('policy_versions')
		.select('id,policy_type,version,title,content,content_url,summary,effective_at')
		.eq('is_active', true)
		.order('effective_at', { ascending: false });
	if (error) {
		return { policies: [], error: '정책 정보를 불러오지 못했습니다. 잠시 후 다시 시도하세요.' };
	}
	return { policies: latestPoliciesByType(data), error: '' };
}

export async function getPolicyConsentStatus(sessionInput?: Session | null): Promise<PolicyConsentStatus> {
	const supabase = getSupabaseClient();
	const session = sessionInput === undefined ? await currentSession() : sessionInput;
	if (!supabase || !session) {
		return emptyPolicyConsentStatus();
	}

	const policyResult = await getActivePolicyVersions();
	if (policyResult.error) {
		return errorPolicyConsentStatus(policyResult.error);
	}

	const policies = policyResult.policies;
	const policyAvailabilityError = requiredPolicyAvailabilityMessage(policies);
	if (policyAvailabilityError) {
		return errorPolicyConsentStatus(policyAvailabilityError);
	}

	const { data, error } = await supabase
		.from('user_policy_consents')
		.select('policy_version_id')
		.eq('user_id', session.user.id);
	if (error) {
		return errorPolicyConsentStatus('약관 동의 이력을 확인하지 못했습니다. 잠시 후 다시 시도하세요.');
	}

	const consentedPolicyIds = (Array.isArray(data) ? data : [])
		.map((item) => String(item.policy_version_id ?? ''))
		.filter(Boolean);
	const requiredPolicyIds = policies.map((policy) => policy.id);
	const isComplete = requiredPolicyIds.every((policyId) => consentedPolicyIds.includes(policyId));

	return {
		required: true,
		isComplete,
		policies,
		consentedPolicyIds,
		error: ''
	};
}

export async function completePolicyConsent(policyVersionIds: string[]) {
	const session = await currentSession();
	if (!session) {
		return { ok: false, message: '로그인 후 약관에 동의할 수 있습니다.' };
	}

	const status = await getPolicyConsentStatus(session);
	if (status.error) {
		return { ok: false, message: status.error };
	}
	const requiredPolicyIds = status.policies.map((policy) => policy.id);
	if (!requiredPolicyIds.every((policyId) => policyVersionIds.includes(policyId))) {
		return { ok: false, message: '서비스 이용약관과 개인정보 처리방침에 모두 동의해 주세요.' };
	}

	const response = await fetch('/api/policy-consents', {
		method: 'POST',
		headers: {
			Authorization: `Bearer ${session.access_token}`,
			'content-type': 'application/json'
		},
		body: JSON.stringify({ policy_version_ids: requiredPolicyIds })
	});
	if (!response.ok) {
		const payload = (await response.json().catch(() => ({}))) as { error?: string };
		return { ok: false, message: payload.error || '약관 동의 이력을 저장하지 못했습니다. 잠시 후 다시 시도하세요.' };
	}

	return { ok: true, message: '동의가 완료되었습니다.' };
}

function latestPoliciesByType(value: unknown) {
	const rows = Array.isArray(value) ? value : [];
	const byType = new Map<PolicyType, PolicyVersion>();
	for (const item of rows) {
		const row = item as Partial<PolicyVersion>;
		if ((row.policy_type === 'terms' || row.policy_type === 'privacy') && row.id && !byType.has(row.policy_type)) {
			byType.set(row.policy_type, {
				id: String(row.id),
				policy_type: row.policy_type,
				version: String(row.version ?? ''),
				title: String(row.title ?? ''),
				content: nullableString(row.content),
				content_url: nullableString(row.content_url),
				summary: nullableString(row.summary),
				effective_at: String(row.effective_at ?? '')
			});
		}
	}
	return POLICY_ORDER.map((policyType) => byType.get(policyType)).filter((policy): policy is PolicyVersion => Boolean(policy));
}

function emptyPolicyConsentStatus(): PolicyConsentStatus {
	return {
		required: false,
		isComplete: true,
		policies: [],
		consentedPolicyIds: [],
		error: ''
	};
}

function errorPolicyConsentStatus(error: string): PolicyConsentStatus {
	return {
		required: true,
		isComplete: false,
		policies: [],
		consentedPolicyIds: [],
		error
	};
}

function nullableString(value: unknown) {
	const text = String(value ?? '').trim();
	return text || null;
}
