import { env } from '$env/dynamic/private';
import { json, type RequestHandler } from '@sveltejs/kit';
import { getSupabaseServerClient, getSupabaseUserClient } from '$lib/server/supabase';

const DEFAULT_BUCKET = 'project-body-assets';
const MAX_BODY_IMAGE_BYTES = 5 * 1024 * 1024;
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

	const accessToken = bearerToken(request);
	if (!accessToken) {
		return json({ error: '로그인 후 본문 이미지를 업로드할 수 있습니다.' }, { status: 401 });
	}

	const userClient = getSupabaseUserClient(accessToken);
	const serviceClient = getSupabaseServerClient();
	if (!userClient || !serviceClient) {
		return json({ error: '본문 이미지 업로드 서버 환경 변수가 설정되지 않았습니다.' }, { status: 503 });
	}

	const { data: userData, error: userError } = await userClient.auth.getUser(accessToken);
	const user = userData.user;
	if (userError || !user) {
		return json({ error: '로그인 세션을 확인하지 못했습니다.' }, { status: 401 });
	}

	const { data: project, error: projectError } = await serviceClient
		.from('projects')
		.select('id,author_id')
		.eq('id', projectId)
		.eq('author_id', user.id)
		.maybeSingle();
	if (projectError || !project) {
		return json({ error: '수정할 프로젝트를 찾을 수 없습니다.' }, { status: 404 });
	}

	const formData = await safeFormData(request);
	const file = formData?.get('image');
	if (!(file instanceof File)) {
		return json({ error: '본문 이미지 파일을 선택하세요.' }, { status: 400 });
	}

	const extension = ALLOWED_TYPES.get(file.type);
	const validationError = validateImage(file, extension);
	if (validationError) {
		return json({ error: validationError }, { status: 400 });
	}

	const bucketName = env.BODY_IMAGE_STORAGE_BUCKET || DEFAULT_BUCKET;
	const bucket = serviceClient.storage.from(bucketName);
	await ensureBucket(serviceClient, bucketName);
	const path = `projects/${safeStorageName(projectId)}/body-${crypto.randomUUID()}.${extension}`;
	const bytes = new Uint8Array(await file.arrayBuffer());
	const { error: uploadError } = await bucket.upload(path, bytes, {
		contentType: file.type,
		cacheControl: '3600',
		upsert: false
	});
	if (uploadError) {
		return json({ error: '본문 이미지 업로드에 실패했습니다.' }, { status: 502 });
	}

	return json({ image_url: bucket.getPublicUrl(path).data.publicUrl });
};

async function ensureBucket(serviceClient: NonNullable<ReturnType<typeof getSupabaseServerClient>>, bucketName: string) {
	const { data } = await serviceClient.storage.getBucket(bucketName);
	if (data) {
		return;
	}
	await serviceClient.storage.createBucket(bucketName, {
		public: true,
		fileSizeLimit: `${MAX_BODY_IMAGE_BYTES}`,
		allowedMimeTypes: [...ALLOWED_TYPES.keys()]
	});
}

async function safeFormData(request: Request) {
	try {
		return await request.formData();
	} catch {
		return null;
	}
}

function bearerToken(request: Request) {
	const header = request.headers.get('authorization') ?? '';
	return header.match(/^Bearer\s+(.+)$/i)?.[1]?.trim() ?? '';
}

function validateImage(file: File, extension: string | undefined) {
	if (!extension) {
		return '본문 이미지는 JPG, PNG, WebP 이미지만 업로드할 수 있습니다.';
	}
	if (file.size <= 0) {
		return '본문 이미지 파일이 비어 있습니다.';
	}
	if (file.size > MAX_BODY_IMAGE_BYTES) {
		return '본문 이미지는 최대 5MB까지 업로드할 수 있습니다.';
	}
	return '';
}

function safeStorageName(value: string) {
	return value.replace(/[^a-zA-Z0-9_-]/g, '_');
}
