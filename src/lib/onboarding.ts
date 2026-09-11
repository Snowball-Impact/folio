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

function nullableString(value: unknown) {
	const text = String(value ?? '').trim();
	return text || null;
}
