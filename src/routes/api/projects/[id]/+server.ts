import { env } from '$env/dynamic/private';
import { json, type RequestHandler } from '@sveltejs/kit';
import { authFailureResponse, authenticateBearerRequest, getOwnedProjectQuery, type ServerAuthContext } from '$lib/server/request-auth';

const DEFAULT_BODY_IMAGE_BUCKET = 'project-body-assets';
const DEFAULT_THUMBNAIL_BUCKET = 'project-thumbnails';

export const DELETE: RequestHandler = async ({ params, request }) => {
	const projectId = params.id;
	if (!projectId) {
		return json({ error: '프로젝트 ID가 없습니다.' }, { status: 400 });
	}

	const auth = await authenticateBearerRequest(request);
	if (!auth.ok) {
		return authFailureResponse(auth, {
			missingToken: '로그인 후 프로젝트를 삭제할 수 있습니다.',
			unavailable: '프로젝트 삭제 서버 환경 변수가 설정되지 않았습니다.',
			invalidSession: '로그인 세션을 확인하지 못했습니다.'
		});
	}

	const { data: project, error: projectError } = await getOwnedProjectQuery(auth, projectId, 'id,author_id,status').maybeSingle<{
		status: string | null;
	}>();
	if (projectError || !project || project.status === 'deleted') {
		return json({ error: '삭제할 프로젝트를 찾을 수 없습니다.' }, { status: 404 });
	}

	try {
		await removeProjectStoragePrefix(auth, env.BODY_IMAGE_STORAGE_BUCKET || DEFAULT_BODY_IMAGE_BUCKET, projectId);
		await removeProjectStoragePrefix(auth, env.THUMBNAIL_STORAGE_BUCKET || DEFAULT_THUMBNAIL_BUCKET, projectId);
	} catch {
		return json({ error: '프로젝트 파일을 정리하지 못했습니다. 잠시 후 다시 시도하세요.' }, { status: 502 });
	}

	const { error: reportError } = await auth.serviceClient.from('powerbi_reports').delete().eq('project_id', projectId);
	if (reportError) {
		return json({ error: 'Power BI 게시본 연결을 정리하지 못했습니다. 잠시 후 다시 시도하세요.' }, { status: 502 });
	}

	const { error: updateError } = await auth.serviceClient
		.from('projects')
		.update({
		status: 'deleted',
		deleted_at: new Date().toISOString(),
		is_public: false,
		thumbnail_url: null,
		power_bi_url: null,
		embed_status: 'external_only'
		})
		.eq('id', projectId)
		.eq('author_id', auth.user.id);
	if (updateError) {
		return json({ error: '프로젝트 삭제에 실패했습니다. 잠시 후 다시 시도하세요.' }, { status: 502 });
	}

	return json({ ok: true, message: '프로젝트와 연결된 파일을 삭제했습니다.' });
};

async function removeProjectStoragePrefix(
	auth: ServerAuthContext,
	bucketName: string,
	projectId: string
) {
	const { data: bucketInfo, error: bucketError } = await auth.serviceClient.storage.getBucket(bucketName);
	if (bucketError || !bucketInfo) {
		if (String(bucketError?.message ?? '').toLowerCase().includes('not found')) {
			return;
		}
		throw new Error('Storage bucket lookup failed');
	}

	const directory = `projects/${safeStorageName(projectId)}`;
	const bucket = auth.serviceClient.storage.from(bucketName);
	while (true) {
		const { data, error: listError } = await bucket.list(directory, { limit: 1000 });
		if (listError) {
			throw new Error('Storage prefix list failed');
		}
		const paths = (data ?? []).map((item: { name: string }) => `${directory}/${item.name}`);
		if (paths.length === 0) {
			return;
		}
		const { error: removeError } = await bucket.remove(paths);
		if (removeError) {
			throw new Error('Storage prefix removal failed');
		}
	}
}

function safeStorageName(value: string) {
	return value.replace(/[^a-zA-Z0-9_-]/g, '_');
}
