import { env } from '$env/dynamic/public';
import { redirect } from '@sveltejs/kit';
import { createClient } from '@supabase/supabase-js';
import type { PageServerLoad } from './$types';

type PolicyType = 'privacy' | 'terms';

type PolicyRow = {
	policy_type: PolicyType;
	version: string | null;
	title: string | null;
	content: string | null;
	content_url: string | null;
	summary: string | null;
	effective_at: string | null;
};

const POLICY_LABELS: Record<PolicyType, string> = {
	privacy: '개인정보 처리방침',
	terms: '서비스 이용약관'
};

export const load: PageServerLoad = async ({ params, url }) => {
	const queryType = url.searchParams.get('type');
	const routeType = params.type;
	const policyType = normalizePolicyType(routeType || queryType);

	if (!routeType && queryType === policyType) {
		throw redirect(301, `/policy/${policyType}`);
	}

	if (!env.PUBLIC_SUPABASE_URL || !env.PUBLIC_SUPABASE_PUBLISHABLE_KEY) {
		return emptyPolicy(policyType, 'Supabase 공개 환경 변수가 없어 정책 본문을 불러오지 못했습니다.');
	}

	const supabase = createClient(env.PUBLIC_SUPABASE_URL, env.PUBLIC_SUPABASE_PUBLISHABLE_KEY, {
		auth: {
			autoRefreshToken: false,
			persistSession: false
		}
	});

	const { data, error } = await supabase
		.from('policy_versions')
		.select('policy_type,version,title,content,content_url,summary,effective_at')
		.eq('is_active', true)
		.eq('policy_type', policyType)
		.order('effective_at', { ascending: false })
		.limit(1)
		.maybeSingle<PolicyRow>();

	if (error) {
		return emptyPolicy(policyType, '현재 정책 본문을 불러오지 못했습니다. 잠시 후 다시 시도하세요.');
	}

	return {
		policyType,
		label: POLICY_LABELS[policyType],
		policy: data,
		error: data ? '' : '현재 표시할 정책 본문이 없습니다. 문의가 필요하면 contact@snowballimpact.com으로 연락해 주세요.'
	};
};

function normalizePolicyType(value: string | null): PolicyType {
	return value === 'terms' ? 'terms' : 'privacy';
}

function emptyPolicy(policyType: PolicyType, error: string) {
	return {
		policyType,
		label: POLICY_LABELS[policyType],
		policy: null,
		error
	};
}