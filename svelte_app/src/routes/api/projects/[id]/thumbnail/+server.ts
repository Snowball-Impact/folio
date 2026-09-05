import { env } from '$env/dynamic/private';
import { json, type RequestHandler } from '@sveltejs/kit';
import { authFailureResponse, authenticateBearerRequest, getOwnedProjectQuery } from '$lib/server/request-auth';

const DEFAULT_BUCKET = 'project-thumbnails';
const MAX_THUMBNAIL_BYTES = 5 * 1024 * 1024;
const ALLOWED_TYPES = new Map([
	['image/jpeg', 'jpg'],
	['image/png', 'png'],
	['image/webp', 'webp']
]);

export const POST: RequestHandler = async ({ params, request }) => {
	const projectId = params.id;
	if (!projectId) {
		return json({ error: '프로젝트 ID가 없습니다.' }, { status: 400 });
	}

	const auth = await authenticateBearerRequest(request);
	if (!auth.ok) {
		return authFailureResponse(auth, {
			missingToken: '로그인 후 썸네일을 업로드할 수 있습니다.',
			unavailable: '썸네일 업로드 서버 환경 변수가 설정되지 않았습니다.',
			invalidSession: '로그인 세션을 확인하지 못했습니다.'
		});
	}

	const { data: project, error: projectError } = await getOwnedProjectQuery(auth, projectId, 'id,author_id').maybeSingle();
	if (projectError || !project) {
		return json({ error: '수정할 프로젝트를 찾을 수 없습니다.' }, { status: 404 });
	}

	const formData = await safeFormData(request);
	const file = formData?.get('thumbnail');
	if (!(file instanceof File)) {
		return json({ error: '썸네일 파일을 선택하세요.', error_code: 'THUMBNAIL_FILE_MISSING' }, { status: 400 });
	}

	const validationError = validateThumbnail(file);
	if (validationError) {
		return json({ error: validationError, error_code: 'THUMBNAIL_FILE_INVALID' }, { status: 400 });
	}

	const extension = ALLOWED_TYPES.get(file.type) ?? 'jpg';
	const bucketName = env.THUMBNAIL_STORAGE_BUCKET || DEFAULT_BUCKET;
	const path = `projects/${safeStorageName(projectId)}/thumbnail-${Date.now()}.${extension}`;
	console.info('Thumbnail upload started', {
		projectId,
		bucketName,
		size: file.size,
		type: file.type
	});
	const bytes = new Uint8Array(await file.arrayBuffer());
	const bucket = auth.serviceClient.storage.from(bucketName);
	const { error: uploadError } = await bucket.upload(path, bytes, {
		contentType: file.type,
		cacheControl: '3600',
		upsert: true
	});
	if (uploadError) {
		console.error('Thumbnail storage upload failed', {
			projectId,
			bucketName,
			message: uploadError.message
		});
		return json({ error: '썸네일 업로드에 실패했습니다.', error_code: 'THUMBNAIL_STORAGE_UPLOAD_FAILED' }, { status: 502 });
	}

	await removeOldThumbnails(bucket, projectId, path);
	const publicUrl = cacheBustedUrl(bucket.getPublicUrl(path).data.publicUrl);
	const { error: updateError } = await auth.serviceClient
		.from('projects')
		.update({
			thumbnail_url: publicUrl,
			thumbnail_mode: 'upload'
		})
		.eq('id', projectId)
		.eq('author_id', auth.user.id);
	if (updateError) {
		console.error('Thumbnail project update failed', {
			projectId,
			message: updateError.message
		});
		await bucket.remove([path]);
		return json({ error: '프로젝트에 썸네일을 연결하지 못했습니다.', error_code: 'THUMBNAIL_PROJECT_UPDATE_FAILED' }, { status: 502 });
	}

	console.info('Thumbnail upload completed', { projectId, path });
	return json({ thumbnail_url: publicUrl });
};


export const DELETE: RequestHandler = async ({ params, request }) => {
	const projectId = params.id;
	if (!projectId) {
		return json({ error: '프로젝트 ID가 없습니다.' }, { status: 400 });
	}

	const auth = await authenticateBearerRequest(request);
	if (!auth.ok) {
		return authFailureResponse(auth, {
			missingToken: '로그인 후 썸네일을 삭제할 수 있습니다.',
			unavailable: '썸네일 삭제 서버 환경 변수가 설정되지 않았습니다.',
			invalidSession: '로그인 세션을 확인하지 못했습니다.'
		});
	}

	const { data: project, error: projectError } = await getOwnedProjectQuery(auth, projectId, 'id,author_id').maybeSingle();
	if (projectError || !project) {
		return json({ error: '수정할 프로젝트를 찾을 수 없습니다.' }, { status: 404 });
	}

	const bucketName = env.THUMBNAIL_STORAGE_BUCKET || DEFAULT_BUCKET;
	await removeOldThumbnails(auth.serviceClient.storage.from(bucketName), projectId, '');
	const { error: updateError } = await auth.serviceClient
		.from('projects')
		.update({
			thumbnail_url: null,
			thumbnail_mode: 'auto_cover'
		})
		.eq('id', projectId)
		.eq('author_id', auth.user.id);
	if (updateError) {
		return json({ error: '프로젝트 썸네일 연결을 삭제하지 못했습니다.' }, { status: 502 });
	}

	return json({ ok: true, message: '기존 썸네일을 삭제했습니다.' });
};
async function safeFormData(request: Request) {
	try {
		return await request.formData();
	} catch {
		return null;
	}
}

function validateThumbnail(file: File) {
	if (!ALLOWED_TYPES.has(file.type)) {
		return '썸네일은 JPG, PNG, WebP 이미지만 업로드할 수 있습니다.';
	}
	if (file.size <= 0) {
		return '썸네일 파일이 비어 있습니다.';
	}
	if (file.size > MAX_THUMBNAIL_BYTES) {
		return '썸네일 이미지는 최대 5MB까지 업로드할 수 있습니다.';
	}
	const filename = file.name.toLowerCase();
	if (!filename.endsWith('.jpg') && !filename.endsWith('.jpeg') && !filename.endsWith('.png') && !filename.endsWith('.webp')) {
		return '썸네일은 JPG, PNG, WebP 이미지만 업로드할 수 있습니다.';
	}
	return '';
}

async function removeOldThumbnails(
	bucket: {
		list: (path: string) => Promise<{ data: Array<{ name: string }> | null }>;
		remove: (paths: string[]) => Promise<unknown>;
	},
	projectId: string,
	keepPath: string
) {
	const directory = `projects/${safeStorageName(projectId)}`;
	const { data } = await bucket.list(directory);
	const oldPaths = (data ?? [])
		.map((item: { name: string }) => `${directory}/${item.name}`)
		.filter((path: string) => path !== keepPath);
	if (oldPaths.length > 0) {
		await bucket.remove(oldPaths);
	}
}

function safeStorageName(value: string) {
	return value.replace(/[^a-zA-Z0-9_-]/g, '_');
}

function cacheBustedUrl(url: string) {
	const separator = url.includes('?') ? '&' : '?';
	return `${url}${separator}v=${Date.now()}`;
}
