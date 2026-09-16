import { json, type RequestHandler } from '@sveltejs/kit';
import { authenticateBearerRequest, authFailureResponse } from '$lib/server/request-auth';
import { clientIpAddress, enforceRateLimit, opaqueIdentifier, rateLimitResponseInit } from '$lib/server/rate-limit';
import { rateLimitPolicy } from '$lib/server/rate-limit-policy';
import { getSupabaseServerClient } from '$lib/server/supabase';

export const POST: RequestHandler = async ({ params, request }) => {
	const projectId = params.id;
	if (!isUuid(projectId)) {
		return json({ error: '프로젝트 ID가 올바르지 않습니다.' }, { status: 400 });
	}

	const authenticated = await authenticateBearerRequest(request);
	if (!authenticated.ok && authenticated.reason !== 'missing-token') {
		return authFailureResponse(authenticated, {
			missingToken: '로그인 세션을 확인하지 못했습니다.',
			unavailable: '조회수 기록 서버 환경 변수가 설정되지 않았습니다.',
			invalidSession: '로그인 세션을 확인하지 못했습니다.'
		});
	}

	const serviceClient = authenticated.ok ? authenticated.serviceClient : getSupabaseServerClient();
	const rateLimit = await enforceRateLimit(
		serviceClient,
		request.headers,
		rateLimitPolicy('project-view', authenticated.ok ? authenticated.user.id : null)
	);
	if (!rateLimit.ok) {
		return json(
			{ error: rateLimit.reason === 'limited' ? '조회수 기록 요청이 너무 많습니다. 잠시 후 다시 시도하세요.' : '요청 제한 설정을 확인하지 못했습니다.' },
			rateLimitResponseInit(rateLimit)
		);
	}

	const anonymousViewerKey = await opaqueIdentifier(`project-view:${clientIpAddress(request.headers)}`);

	const { data, error } = await serviceClient!.rpc('record_server_project_view', {
		p_project_id: projectId,
		p_viewer_user_id: authenticated.ok ? authenticated.user.id : null,
		p_anonymous_viewer_key: anonymousViewerKey
	});
	if (error) {
		return json({ error: '조회수를 기록하지 못했습니다.' }, { status: 502 });
	}
	return json({ counted: data === true });
};

function isUuid(value: string | undefined): value is string {
	return /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(value ?? '');
}
