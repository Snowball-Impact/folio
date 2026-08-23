import { currentSession } from '$lib/auth';

export async function uploadProjectThumbnail(projectId: string, file: File) {
	const session = await currentSession();
	if (!session) {
		return { ok: false, message: '로그인 후 썸네일을 업로드할 수 있습니다.', thumbnailUrl: null };
	}

	const formData = new FormData();
	formData.set('thumbnail', file);
	const response = await fetch(`/api/projects/${projectId}/thumbnail`, {
		method: 'POST',
		headers: {
			Authorization: `Bearer ${session.access_token}`
		},
		body: formData
	});
	const payload = (await response.json().catch(() => ({}))) as {
		error?: string;
		thumbnail_url?: string;
	};
	if (!response.ok || !payload.thumbnail_url) {
		return {
			ok: false,
			message: payload.error || '썸네일 업로드에 실패했습니다.',
			thumbnailUrl: null
		};
	}

	return {
		ok: true,
		message: '썸네일이 업로드되었습니다.',
		thumbnailUrl: payload.thumbnail_url
	};
}
