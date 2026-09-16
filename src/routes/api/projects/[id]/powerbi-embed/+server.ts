import { json } from '@sveltejs/kit';
import { loadProjectEmbedState } from '$lib/projects';
import { getPowerBIEmbedConfig, PowerBIServiceError } from '$lib/server/powerbi';
import { enforceRateLimit, rateLimitResponseInit } from '$lib/server/rate-limit';
import { rateLimitPolicy } from '$lib/server/rate-limit-policy';
import { getSupabaseServerClient } from '$lib/server/supabase';

export async function GET({ params, request }) {
	const projectId = params.id;
	if (!isUuid(projectId)) {
		return json({ error: '프로젝트 ID가 올바르지 않습니다.' }, { status: 400 });
	}

	const rateLimit = await enforceRateLimit(getSupabaseServerClient(), request.headers, rateLimitPolicy('powerbi-embed'));
	if (!rateLimit.ok) {
		return json(
			{ error: rateLimit.reason === 'limited' ? 'Power BI 보고서 요청이 너무 많습니다. 잠시 후 다시 시도하세요.' : '요청 제한 설정을 확인하지 못했습니다.' },
			rateLimitResponseInit(rateLimit)
		);
	}

	const projectState = await loadProjectEmbedState(projectId);
	const project = projectState.state;

	if (!project || project.status === 'deleted' || !project.is_public) {
		return json({ error: projectState.error || '프로젝트를 찾을 수 없습니다.' }, { status: 404 });
	}
	if (project.status !== 'published' || project.project_type !== 'powerbi') {
		return json({ error: 'Power BI 임베드를 사용할 수 없는 프로젝트입니다.' }, { status: 409 });
	}

	try {
		const config = await getPowerBIEmbedConfig(projectId);
		if (!config) {
			return json({ error: 'Power BI Report 메타데이터가 없습니다.' }, { status: 404 });
		}
		return json(config);
	} catch (error) {
		if (error instanceof PowerBIServiceError) {
			return json(
				{
					error: error.message,
					error_code: error.code,
					upstream_status: error.upstreamStatus,
					upstream_code: error.upstreamCode
				},
				{ status: error.status }
			);
		}
		return json({ error: 'Power BI Embed Token 발급 중 오류가 발생했습니다.', error_code: 'PBI_UNKNOWN' }, { status: 500 });
	}
}

function isUuid(value: string | undefined): value is string {
	return /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(value ?? '');
}
