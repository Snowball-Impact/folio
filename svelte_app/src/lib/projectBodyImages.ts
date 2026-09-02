import { currentSession } from '$lib/auth';
import { publicConfigMilliseconds } from '$lib/clientRuntimeConfig';

const BODY_IMAGE_UPLOAD_TIMEOUT_MS = publicConfigMilliseconds('PUBLIC_BODY_IMAGE_UPLOAD_TIMEOUT_SECONDS', 10);

export type PendingProjectBodyImage = {
	file: File;
	objectUrl: string;
};

export function stripPendingBodyImages(html: string, images: PendingProjectBodyImage[]) {
	return images.reduce(
		(result, image) => result.replace(new RegExp(`<img\\b[^>]*\\bsrc=["']${escapeRegExp(image.objectUrl)}["'][^>]*>`, 'gi'), ''),
		html
	);
}

export function replacePendingBodyImages(html: string, images: PendingProjectBodyImage[], urls: string[]) {
	return images.reduce((result, image, index) => result.replaceAll(image.objectUrl, urls[index] ?? ''), html);
}

export async function uploadProjectBodyImages(projectId: string, images: PendingProjectBodyImage[]) {
	const session = await currentSession();
	if (!session) {
		return { ok: false, message: '로그인 후 본문 이미지를 업로드할 수 있습니다.', urls: [] as string[] };
	}

	const urls: string[] = [];
	for (const image of images) {
		const formData = new FormData();
		formData.set('image', image.file);
		const response = await fetchWithTimeout(
			`/api/projects/${projectId}/body-image`,
			{
				method: 'POST',
				headers: { Authorization: `Bearer ${session.access_token}` },
				body: formData
			},
			BODY_IMAGE_UPLOAD_TIMEOUT_MS
		).catch((error) => errorResponse(error, '본문 이미지 업로드 요청 시간이 초과되었습니다. 이미지 용량이나 네트워크 상태를 확인하세요.'));
		const payload = (await response.json().catch(() => ({}))) as { image_url?: string; error?: string };
		if (!response.ok || !payload.image_url) {
			return { ok: false, message: payload.error || '본문 이미지 업로드에 실패했습니다.', urls };
		}
		urls.push(payload.image_url);
	}

	return { ok: true, message: '본문 이미지가 업로드되었습니다.', urls };
}

function escapeRegExp(value: string) {
	return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

async function fetchWithTimeout(url: string, init: RequestInit, timeoutMs: number) {
	const controller = new AbortController();
	const timeout = setTimeout(() => controller.abort(), timeoutMs);
	try {
		return await fetch(url, { ...init, signal: controller.signal });
	} finally {
		clearTimeout(timeout);
	}
}

function errorResponse(error: unknown, fallbackMessage: string) {
	const message = error instanceof Error && error.name !== 'AbortError' ? error.message : fallbackMessage;
	return new Response(JSON.stringify({ error: message }), {
		status: 408,
		headers: {
			'Content-Type': 'application/json'
		}
	});
}
