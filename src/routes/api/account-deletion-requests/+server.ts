import { json, type RequestHandler } from '@sveltejs/kit';
import {
	ACTIVE_ACCOUNT_DELETION_REQUEST_STATUSES,
	accountDeletionRequestPayload,
	accountDeletionRequestSelectColumns,
	normalizeAccountDeletionRequestNote
} from '$lib/server/account-deletion-requests';
import { authFailureResponse, authenticateBearerRequest, type ServerAuthContext } from '$lib/server/request-auth';

const ACCOUNT_DELETION_REQUESTS_ENABLED = import.meta.env.ACCOUNT_DELETION_REQUEST_ENABLED === 'true';

export const GET: RequestHandler = async ({ request }) => {
	if (!ACCOUNT_DELETION_REQUESTS_ENABLED) {
		return disabledResponse();
	}
	const auth = await authenticateBearerRequest(request);
	if (!auth.ok) {
		return authFailureResponse(auth, authFailureMessages);
	}

	const { data, error } = await activeRequestQuery(auth.serviceClient, auth.user.id);
	if (error) {
		return json({ error: '계정 삭제 요청 상태를 확인하지 못했습니다.' }, { status: 502 });
	}
	return json({ request: data ?? null });
};

export const POST: RequestHandler = async ({ request }) => {
	if (!ACCOUNT_DELETION_REQUESTS_ENABLED) {
		return disabledResponse();
	}
	const auth = await authenticateBearerRequest(request);
	if (!auth.ok) {
		return authFailureResponse(auth, authFailureMessages);
	}

	const { data: existingRequest, error: existingError } = await activeRequestQuery(auth.serviceClient, auth.user.id);
	if (existingError) {
		return json({ error: '계정 삭제 요청 상태를 확인하지 못했습니다.' }, { status: 502 });
	}
	if (existingRequest) {
		return json({
			ok: true,
			request: existingRequest,
			message: '이미 계정 삭제 요청이 접수되어 있습니다.'
		});
	}

	const payload = await safeJson(request);
	const requestNote = normalizeAccountDeletionRequestNote(
		payload && typeof payload === 'object'
			? (payload as { request_note?: unknown; note?: unknown }).request_note ?? (payload as { note?: unknown }).note
			: null
	);
	const { data, error } = await auth.serviceClient
		.from('account_deletion_requests')
		.insert(
			accountDeletionRequestPayload({
				userId: auth.user.id,
				email: auth.user.email,
				requestNote
			})
		)
		.select(accountDeletionRequestSelectColumns)
		.single();

	if (error) {
		if (error.code === '23505') {
			const { data: latestRequest } = await activeRequestQuery(auth.serviceClient, auth.user.id);
			if (latestRequest) {
				return json({
					ok: true,
					request: latestRequest,
					message: '이미 계정 삭제 요청이 접수되어 있습니다.'
				});
			}
		}
		return json({ error: '계정 삭제 요청을 접수하지 못했습니다.' }, { status: 502 });
	}

	return json(
		{
			ok: true,
			request: data,
			message: '계정 삭제 요청을 접수했습니다. 운영자가 확인 후 처리합니다.'
		},
		{ status: 201 }
	);
};

const authFailureMessages = {
	missingToken: '로그인 후 계정 삭제를 요청할 수 있습니다.',
	unavailable: '계정 삭제 요청 서버 환경 변수가 설정되지 않았습니다.',
	invalidSession: '로그인 세션을 확인하지 못했습니다.'
};

function disabledResponse() {
	return json({ error: '계정 삭제 요청 기능은 현재 준비 중입니다.' }, { status: 404 });
}

function activeRequestQuery(serviceClient: ServerAuthContext['serviceClient'], userId: string) {
	return serviceClient
		.from('account_deletion_requests')
		.select(accountDeletionRequestSelectColumns)
		.eq('user_id', userId)
		.in('status', ACTIVE_ACCOUNT_DELETION_REQUEST_STATUSES)
		.order('requested_at', { ascending: false })
		.limit(1)
		.maybeSingle();
}

async function safeJson(request: Request) {
	try {
		return await request.json();
	} catch {
		return null;
	}
}
