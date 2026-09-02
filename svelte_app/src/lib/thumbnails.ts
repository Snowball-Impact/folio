import { currentSession } from '$lib/auth';

const THUMBNAIL_UPLOAD_TIMEOUT_MS = 45_000;
const THUMBNAIL_CAPTURE_TIMEOUT_MS = 90_000;
const THUMBNAIL_DELETE_TIMEOUT_MS = 30_000;

export async function uploadProjectThumbnail(projectId: string, file: File) {
	const session = await currentSession();
	if (!session) {
		return { ok: false, message: '로그인 후 썸네일을 업로드할 수 있습니다.', thumbnailUrl: null };
	}

	const formData = new FormData();
	formData.set('thumbnail', file);
	const response = await fetchWithTimeout(
		`/api/projects/${projectId}/thumbnail`,
		{
			method: 'POST',
			headers: {
				Authorization: `Bearer ${session.access_token}`
			},
			body: formData
		},
		THUMBNAIL_UPLOAD_TIMEOUT_MS
	).catch((error) => errorResponse(error, '썸네일 업로드 요청 시간이 초과되었습니다. 이미지 용량이나 네트워크 상태를 확인하세요.'));
	const payload = (await response.json().catch(() => ({}))) as {
		error?: string;
		error_code?: string;
		thumbnail_url?: string;
	};
	if (!response.ok || !payload.thumbnail_url) {
		return {
			ok: false,
			message: withErrorCode(payload.error || '썸네일 업로드에 실패했습니다.', payload),
			thumbnailUrl: null
		};
	}

	return {
		ok: true,
		message: '썸네일이 업로드되었습니다.',
		thumbnailUrl: payload.thumbnail_url
	};
}

export async function captureProjectThumbnail(projectId: string) {
	const session = await currentSession();
	if (!session) {
		return { ok: false, message: '로그인 후 썸네일을 캡처할 수 있습니다.', thumbnailUrl: null };
	}

	const response = await fetchWithTimeout(
		`/api/projects/${projectId}/thumbnail-capture`,
		{
			method: 'POST',
			headers: {
				Authorization: `Bearer ${session.access_token}`
			}
		},
		THUMBNAIL_CAPTURE_TIMEOUT_MS
	).catch((error) => errorResponse(error, '썸네일 자동 캡처 요청 시간이 초과되었습니다. 잠시 후 다시 시도하세요.'));
	const payload = (await response.json().catch(() => ({}))) as {
		error?: string;
		error_code?: string;
		thumbnail_url?: string;
	};
	if (!response.ok || !payload.thumbnail_url) {
		return {
			ok: false,
			message: withErrorCode(payload.error || '썸네일 캡처에 실패했습니다.', payload),
			thumbnailUrl: null
		};
	}

	return {
		ok: true,
		message: '썸네일이 캡처되었습니다.',
		thumbnailUrl: payload.thumbnail_url
	};
}

export async function deleteProjectThumbnail(projectId: string) {
	const session = await currentSession();
	if (!session) {
		return { ok: false, message: '로그인 후 썸네일을 삭제할 수 있습니다.' };
	}

	const response = await fetchWithTimeout(
		`/api/projects/${projectId}/thumbnail`,
		{
			method: 'DELETE',
			headers: {
				Authorization: `Bearer ${session.access_token}`
			}
		},
		THUMBNAIL_DELETE_TIMEOUT_MS
	).catch((error) => errorResponse(error, '썸네일 삭제 요청 시간이 초과되었습니다. 잠시 후 다시 시도하세요.'));
	const payload = (await response.json().catch(() => ({}))) as {
		ok?: boolean;
		message?: string;
		error?: string;
		error_code?: string;
	};
	if (!response.ok || payload.ok === false) {
		return { ok: false, message: withErrorCode(payload.error || payload.message || '썸네일 삭제에 실패했습니다.', payload) };
	}
	return { ok: true, message: payload.message || '기존 썸네일을 삭제했습니다.' };
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

function withErrorCode(message: string, payload: { error_code?: string }) {
	return payload.error_code ? `${message} [${payload.error_code}]` : message;
}
