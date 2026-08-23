import { json, type RequestHandler } from '@sveltejs/kit';
import { getSupabaseServerClient, getSupabaseUserClient } from '$lib/server/supabase';
import { publishPbixForProject, PowerBIServiceError } from '$lib/server/powerbi';

export const POST: RequestHandler = async ({ params, request }) => {
	const projectId = params.id;
	if (!projectId) {
		return json({ error: '프로젝트 ID가 없습니다.' }, { status: 400 });
	}

	const accessToken = bearerToken(request);
	if (!accessToken) {
		return json({ error: '로그인 후 PBIX를 게시할 수 있습니다.' }, { status: 401 });
	}

	const userClient = getSupabaseUserClient(accessToken);
	const serviceClient = getSupabaseServerClient();
	if (!userClient || !serviceClient) {
		return json({ error: 'PBIX 게시 서버 환경 변수가 설정되지 않았습니다.' }, { status: 503 });
	}

	const { data: userData, error: userError } = await userClient.auth.getUser(accessToken);
	const user = userData.user;
	if (userError || !user) {
		return json({ error: '로그인 세션을 확인하지 못했습니다.' }, { status: 401 });
	}

	const { data: project, error: projectError } = await serviceClient
		.from('projects')
		.select('id,author_id,status')
		.eq('id', projectId)
		.eq('author_id', user.id)
		.maybeSingle();
	if (projectError || !project || project.status === 'deleted') {
		return json({ error: '게시할 프로젝트를 찾을 수 없습니다.' }, { status: 404 });
	}

	const formData = await safeFormData(request);
	const file = formData?.get('pbix');
	if (!(file instanceof File)) {
		return json({ error: 'PBIX 파일을 선택하세요.' }, { status: 400 });
	}

	try {
		const result = await publishPbixForProject(projectId, file);
		return json(result, { status: result.ok ? 200 : 202 });
	} catch (error) {
		if (error instanceof PowerBIServiceError) {
			return json({ error: error.message }, { status: error.status });
		}
		return json({ error: 'Power BI 게시 중 오류가 발생했습니다.' }, { status: 500 });
	}
};

async function safeFormData(request: Request) {
	try {
		return await request.formData();
	} catch {
		return null;
	}
}

function bearerToken(request: Request) {
	const header = request.headers.get('authorization') ?? '';
	const match = header.match(/^Bearer\s+(.+)$/i);
	return match?.[1]?.trim() ?? '';
}
