import { json, type RequestHandler } from '@sveltejs/kit';
import { getSupabaseServerClient, getSupabaseUserClient } from '$lib/server/supabase';
import { captureProjectThumbnail, ThumbnailCaptureError } from '$lib/server/thumbnail-capture';

type ProjectRecord = {
	id: string;
	author_id: string;
	status: string | null;
	power_bi_url: string | null;
	report_url: string | null;
};

export const POST: RequestHandler = async ({ params, request }) => {
	const projectId = params.id;
	if (!projectId) {
		return json({ error: '프로젝트 ID가 없습니다.' }, { status: 400 });
	}

	const accessToken = bearerToken(request);
	if (!accessToken) {
		return json({ error: '로그인 후 썸네일을 캡처할 수 있습니다.' }, { status: 401 });
	}

	const userClient = getSupabaseUserClient(accessToken);
	const serviceClient = getSupabaseServerClient();
	if (!userClient || !serviceClient) {
		return json({ error: '썸네일 캡처 서버 환경 변수가 설정되지 않았습니다.' }, { status: 503 });
	}

	const { data: userData, error: userError } = await userClient.auth.getUser(accessToken);
	const user = userData.user;
	if (userError || !user) {
		return json({ error: '로그인 세션을 확인하지 못했습니다.' }, { status: 401 });
	}

	const { data: project, error: projectError } = await serviceClient
		.from('projects')
		.select('id,author_id,status,power_bi_url,report_url')
		.eq('id', projectId)
		.eq('author_id', user.id)
		.maybeSingle<ProjectRecord>();
	if (projectError || !project || project.status === 'deleted') {
		return json({ error: '캡처할 프로젝트를 찾을 수 없습니다.' }, { status: 404 });
	}

	const sourceUrl = project.power_bi_url || project.report_url;
	if (!sourceUrl) {
		return json({ error: '캡처할 Embed Code 또는 Web App URL이 없습니다.' }, { status: 400 });
	}

	try {
		const thumbnailUrl = await captureProjectThumbnail(projectId, sourceUrl);
		return json({ thumbnail_url: thumbnailUrl });
	} catch (error) {
		if (error instanceof ThumbnailCaptureError) {
			return json({ error: error.message }, { status: error.status });
		}
		return json({ error: '썸네일 캡처 중 오류가 발생했습니다.' }, { status: 500 });
	}
};

function bearerToken(request: Request) {
	const header = request.headers.get('authorization') ?? '';
	const match = header.match(/^Bearer\s+(.+)$/i);
	return match?.[1]?.trim() ?? '';
}
