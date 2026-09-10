import { currentSession } from '$lib/auth';
import { fetchWithTimeout, requestErrorResponse } from '$lib/clientRequest';
import { publicConfigMilliseconds } from '$lib/clientRuntimeConfig';

const ACCOUNT_DELETION_REQUEST_TIMEOUT_MS = publicConfigMilliseconds('PUBLIC_ACCOUNT_DELETION_REQUEST_TIMEOUT_SECONDS', 10);

export type AccountDeletionRequest = {
	id: string;
	status: string;
	request_note: string | null;
	requested_at: string;
};

export type AccountDeletionResult = {
	ok: boolean;
	message: string;
	request: AccountDeletionRequest | null;
};

export async function getAccountDeletionRequest(): Promise<AccountDeletionResult> {
	const session = await currentSession();
	if (!session) {
		return { ok: false, message: '로그인 후 계정 삭제 요청 상태를 확인할 수 있습니다.', request: null };
	}

	const response = await fetchWithTimeout(
		'/api/account-deletion-requests',
		{
			method: 'GET',
			headers: {
				Authorization: `Bearer ${session.access_token}`
			}
		},
		ACCOUNT_DELETION_REQUEST_TIMEOUT_MS
	).catch((error) => errorResponse(error, '계정 삭제 요청 상태 확인 시간이 초과되었습니다.'));
	const payload = (await response.json().catch(() => ({}))) as {
		request?: AccountDeletionRequest | null;
		error?: string;
		message?: string;
	};
	if (!response.ok) {
		return { ok: false, message: payload.error || payload.message || '계정 삭제 요청 상태를 확인하지 못했습니다.', request: null };
	}
	return { ok: true, message: '', request: payload.request ?? null };
}

export async function requestAccountDeletion(note: string): Promise<AccountDeletionResult> {
	const session = await currentSession();
	if (!session) {
		return { ok: false, message: '로그인 후 계정 삭제를 요청할 수 있습니다.', request: null };
	}

	const response = await fetchWithTimeout(
		'/api/account-deletion-requests',
		{
			method: 'POST',
			headers: {
				Authorization: `Bearer ${session.access_token}`,
				'content-type': 'application/json'
			},
			body: JSON.stringify({ request_note: note })
		},
		ACCOUNT_DELETION_REQUEST_TIMEOUT_MS
	).catch((error) => errorResponse(error, '계정 삭제 요청 시간이 초과되었습니다.'));
	const payload = (await response.json().catch(() => ({}))) as {
		ok?: boolean;
		request?: AccountDeletionRequest | null;
		error?: string;
		message?: string;
	};
	if (!response.ok || payload.ok === false) {
		return { ok: false, message: payload.error || payload.message || '계정 삭제 요청을 접수하지 못했습니다.', request: null };
	}
	return {
		ok: true,
		message: payload.message || '계정 삭제 요청을 접수했습니다.',
		request: payload.request ?? null
	};
}

function errorResponse(error: unknown, fallbackMessage: string) {
	return requestErrorResponse(error, fallbackMessage, 'ACCOUNT_DELETION_CLIENT_TIMEOUT');
}
