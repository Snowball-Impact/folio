import { currentSession } from '$lib/auth';

export async function publishProjectPbix(projectId: string, file: File) {
	const session = await currentSession();
	if (!session) {
		return { ok: false, message: '로그인 후 PBIX를 게시할 수 있습니다.' };
	}

	const formData = new FormData();
	formData.set('pbix', file);
	const response = await fetch(`/api/projects/${projectId}/powerbi-publish`, {
		method: 'POST',
		headers: {
			Authorization: `Bearer ${session.access_token}`
		},
		body: formData
	});
	const payload = (await response.json().catch(() => ({}))) as {
		ok?: boolean;
		message?: string;
		error?: string;
	};

	if (!response.ok || payload.ok === false) {
		return {
			ok: false,
			message: payload.error || payload.message || 'Power BI 게시에 실패했습니다.'
		};
	}

	return {
		ok: true,
		message: payload.message || 'Power BI 보고서가 게시되었습니다.'
	};
}

export async function unlinkProjectPbix(projectId: string) {
	const session = await currentSession();
	if (!session) {
		return { ok: false, message: '로그인 후 Power BI 연결을 삭제할 수 있습니다.' };
	}

	const response = await fetch(`/api/projects/${projectId}/powerbi-publish`, {
		method: 'DELETE',
		headers: {
			Authorization: `Bearer ${session.access_token}`
		}
	});
	const payload = (await response.json().catch(() => ({}))) as {
		ok?: boolean;
		message?: string;
		error?: string;
	};
	if (!response.ok || payload.ok === false) {
		return { ok: false, message: payload.error || payload.message || 'Power BI 연결 삭제에 실패했습니다.' };
	}
	return { ok: true, message: payload.message || '기존 Power BI 연결을 삭제했습니다.' };
}
export async function projectPbixExists(projectId: string) {
	const session = await currentSession();
	if (!session) {
		return false;
	}

	const response = await fetch(`/api/projects/${projectId}/powerbi-publish`, {
		method: 'GET',
		headers: {
			Authorization: `Bearer ${session.access_token}`
		}
	});
	if (!response.ok) {
		return false;
	}
	const payload = (await response.json().catch(() => ({}))) as { exists?: boolean };
	return Boolean(payload.exists);
}