import { json, type RequestHandler } from '@sveltejs/kit';
import { missingRequiredPolicyTypes } from '$lib/policyRequirements';
import { authFailureResponse, authenticateBearerRequest } from '$lib/server/request-auth';
import { latestRequiredPolicyVersions, normalizePolicyVersionIds, policyConsentRows } from '$lib/server/policy-consents';

export const POST: RequestHandler = async ({ request }) => {
	const auth = await authenticateBearerRequest(request);
	if (!auth.ok) {
		return authFailureResponse(auth, {
			missingToken: '로그인 후 약관 동의 이력을 저장할 수 있습니다.',
			unavailable: '약관 동의 저장 서버 환경 변수가 설정되지 않았습니다.',
			invalidSession: '로그인 세션을 확인하지 못했습니다.'
		});
	}

	const payload = await safeJson(request);
	const policyVersionIds = normalizePolicyVersionIds(
		payload && typeof payload === 'object'
			? (payload as { policy_version_ids?: unknown; policyVersionIds?: unknown }).policy_version_ids ??
					(payload as { policyVersionIds?: unknown }).policyVersionIds
			: null
	);
	if (policyVersionIds.length === 0) {
		return json({ error: '저장할 약관 동의 항목이 없습니다.' }, { status: 400 });
	}

	const { data, error } = await auth.serviceClient
		.from('policy_versions')
		.select('id,policy_type,effective_at')
		.eq('is_active', true)
		.order('effective_at', { ascending: false });
	if (error) {
		return json({ error: '약관 정보를 확인하지 못했습니다.' }, { status: 502 });
	}

	const policies = latestRequiredPolicyVersions(data);
	if (missingRequiredPolicyTypes(policies).length > 0) {
		return json({ error: '서비스 이용에 필요한 약관 정보를 확인하지 못했습니다.' }, { status: 503 });
	}

	const requiredPolicyIds = policies.map((policy) => policy.id);
	if (!requiredPolicyIds.every((policyVersionId) => policyVersionIds.includes(policyVersionId))) {
		return json({ error: '현재 활성화된 서비스 이용약관과 개인정보 처리방침 동의가 모두 필요합니다.' }, { status: 400 });
	}

	const { error: insertError } = await auth.serviceClient.from('user_policy_consents').upsert(
		policyConsentRows(auth.user.id, requiredPolicyIds, request.headers),
		{
			onConflict: 'user_id,policy_version_id',
			ignoreDuplicates: true
		}
	);
	if (insertError) {
		return json({ error: '약관 동의 이력을 저장하지 못했습니다.' }, { status: 502 });
	}

	return json({ ok: true });
};

async function safeJson(request: Request) {
	try {
		return await request.json();
	} catch {
		return null;
	}
}
