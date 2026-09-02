import { currentSession } from '$lib/auth';
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

export type OnboardingStatus = {
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

export async function getOnboardingStatus(): Promise<OnboardingStatus> {
	const supabase = getSupabaseClient();
	const session = await currentSession();
	if (!supabase || !session) {
		return emptyStatus();
	}

	const policyResult = await getActivePolicyVersions();
	if (policyResult.error) {
		return errorStatus(policyResult.error);
	}

	const policies = policyResult.policies;
	if (policies.length === 0) {
		return {
			required: false,
			isComplete: true,
			policies: [],
			consentedPolicyIds: [],
			error: ''
		};
	}

	const { data: consentData, error: consentError } = await supabase
		.from('user_policy_consents')
		.select('policy_version_id')
		.eq('user_id', session.user.id);
	if (consentError) {
		return errorStatus('온보딩 정보를 불러오지 못했습니다. 잠시 후 다시 시도하세요.');
	}

	const consentedPolicyIds = (Array.isArray(consentData) ? consentData : [])
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

export async function completeOnboarding(policyVersionIds: string[]) {
	const supabase = getSupabaseClient();
	const session = await currentSession();
	if (!supabase || !session) {
		return { ok: false, message: '로그인 후 동의할 수 있습니다.' };
	}

	const status = await getOnboardingStatus();
	if (status.error) {
		return { ok: false, message: status.error };
	}
	const requiredPolicyIds = status.policies.map((policy) => policy.id);
	if (!requiredPolicyIds.every((policyId) => policyVersionIds.includes(policyId))) {
		return { ok: false, message: '필수 정책 동의를 모두 확인하세요.' };
	}

	const existingPolicyIds = new Set(status.consentedPolicyIds);
	const rows = policyVersionIds
		.filter((policyId) => !existingPolicyIds.has(policyId))
		.map((policyId) => ({
			user_id: session.user.id,
			policy_version_id: policyId
		}));
	if (rows.length === 0) {
		return { ok: true, message: '이미 동의가 완료되었습니다.' };
	}

	const { error } = await supabase.from('user_policy_consents').insert(rows);
	if (error) {
		return { ok: false, message: '온보딩 정보를 저장하지 못했습니다. 잠시 후 다시 시도하세요.' };
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

function emptyStatus(): OnboardingStatus {
	return {
		required: false,
		isComplete: true,
		policies: [],
		consentedPolicyIds: [],
		error: ''
	};
}

function errorStatus(message: string): OnboardingStatus {
	return {
		required: true,
		isComplete: false,
		policies: [],
		consentedPolicyIds: [],
		error: message
	};
}

function nullableString(value: unknown) {
	const text = String(value ?? '').trim();
	return text || null;
}
