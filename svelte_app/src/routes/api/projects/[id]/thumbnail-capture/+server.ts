import { json, type RequestHandler } from '@sveltejs/kit';
import { env } from '$env/dynamic/private';
import { authFailureResponse, authenticateBearerRequest, getOwnedProjectQuery } from '$lib/server/request-auth';
import { captureProjectThumbnail, ThumbnailCaptureError } from '$lib/server/thumbnail-capture';

type ProjectRecord = {
	id: string;
	author_id: string;
	status: string | null;
	project_type: string | null;
	embed_status: string | null;
	power_bi_url: string | null;
	report_url: string | null;
};

export const POST: RequestHandler = async ({ params, request, url }) => {
	const projectId = params.id;
	if (!projectId) {
		return json({ error: '프로젝트 ID가 없습니다.' }, { status: 400 });
	}

	const auth = await authenticateBearerRequest(request);
	if (!auth.ok) {
		return authFailureResponse(auth, {
			missingToken: '로그인 후 썸네일을 캡처할 수 있습니다.',
			unavailable: '썸네일 캡처 서버 환경 변수가 설정되지 않았습니다.',
			invalidSession: '로그인 세션을 확인하지 못했습니다.'
		});
	}

	const { data: project, error: projectError } = await getOwnedProjectQuery(
		auth,
		projectId,
		'id,author_id,status,project_type,embed_status,power_bi_url,report_url'
	).maybeSingle<ProjectRecord>();
	if (projectError || !project || project.status === 'deleted') {
		return json({ error: '캡처할 프로젝트를 찾을 수 없습니다.' }, { status: 404 });
	}

	const sourceUrl = captureSourceUrl(project, projectId, url);
	if (!sourceUrl) {
		return json({ error: '캡처할 Embed Code 또는 Web App URL이 없습니다.' }, { status: 400 });
	}

	try {
		const thumbnailUrl = await captureProjectThumbnail(projectId, sourceUrl);
		return json({ thumbnail_url: thumbnailUrl });
	} catch (error) {
		if (error instanceof ThumbnailCaptureError) {
			return json({ error: error.message, error_code: error.code }, { status: error.status });
		}
		return json({ error: '썸네일 캡처 중 오류가 발생했습니다.', error_code: 'CAPTURE_UNKNOWN' }, { status: 500 });
	}
};

function captureSourceUrl(project: ProjectRecord, projectId: string, requestUrl: URL) {
	if (project.project_type === 'powerbi' && project.embed_status === 'supported') {
		const detailUrl = new URL(`/projects/${encodeURIComponent(projectId)}`, captureDetailOrigin(requestUrl));
		detailUrl.searchParams.set('capture', 'thumbnail');
		return detailUrl.toString();
	}
	return project.power_bi_url || project.report_url;
}

function captureDetailOrigin(requestUrl: URL) {
	if (thumbnailCaptureProvider() !== 'cloudflare' || !isLoopbackUrl(requestUrl)) {
		return requestUrl.origin;
	}

	const appUrl = publicAppUrl();
	if (appUrl && !isLoopbackUrl(appUrl)) {
		return appUrl.origin;
	}

	return requestUrl.origin;
}

function publicAppUrl() {
	const rawValue = env.APP_URL?.trim();
	if (!rawValue) {
		return null;
	}
	try {
		return new URL(rawValue);
	} catch {
		return null;
	}
}

function thumbnailCaptureProvider() {
	const provider = env.THUMBNAIL_CAPTURE_PROVIDER?.trim().toLowerCase();
	if (provider) {
		return provider;
	}
	return env.CLOUDFLARE_ACCOUNT_ID && env.CLOUDFLARE_BROWSER_RENDERING_API_TOKEN ? 'cloudflare' : 'local';
}

function isLoopbackUrl(url: URL) {
	const hostname = url.hostname.toLowerCase();
	return hostname === 'localhost' || hostname === '127.0.0.1' || hostname === '::1' || hostname.endsWith('.localhost');
}
