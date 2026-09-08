import { json } from '@sveltejs/kit';
import type { User } from '@supabase/supabase-js';
import { getSupabaseServerClient, getSupabaseUserClient } from '$lib/server/supabase';

export type ServerAuthContext = {
	accessToken: string;
	user: User;
	userClient: NonNullable<ReturnType<typeof getSupabaseUserClient>>;
	serviceClient: NonNullable<ReturnType<typeof getSupabaseServerClient>>;
};

export type ServerAuthFailureReason = 'missing-token' | 'unavailable' | 'invalid-session';

export type ServerAuthResult =
	| ({ ok: true } & ServerAuthContext)
	| { ok: false; reason: ServerAuthFailureReason };

type AuthFailureMessages = {
	missingToken: string;
	unavailable: string;
	invalidSession: string;
};

export async function authenticateBearerRequest(request: Request): Promise<ServerAuthResult> {
	const accessToken = bearerToken(request);
	if (!accessToken) {
		return { ok: false, reason: 'missing-token' };
	}

	const userClient = getSupabaseUserClient(accessToken);
	const serviceClient = getSupabaseServerClient();
	if (!userClient || !serviceClient) {
		return { ok: false, reason: 'unavailable' };
	}

	const { data, error } = await userClient.auth.getUser(accessToken);
	if (error || !data.user) {
		return { ok: false, reason: 'invalid-session' };
	}

	return { ok: true, accessToken, user: data.user, userClient, serviceClient };
}

export function authFailureResponse(
	result: Extract<ServerAuthResult, { ok: false }>,
	messages: AuthFailureMessages
) {
	const message =
		result.reason === 'missing-token'
			? messages.missingToken
			: result.reason === 'unavailable'
				? messages.unavailable
				: messages.invalidSession;
	const status = result.reason === 'unavailable' ? 503 : 401;
	return json({ error: message }, { status });
}

export function getOwnedProjectQuery(context: ServerAuthContext, projectId: string, columns: string) {
	return context.serviceClient
		.from('projects')
		.select(columns)
		.eq('id', projectId)
		.eq('author_id', context.user.id);
}

function bearerToken(request: Request) {
	const header = request.headers.get('authorization') ?? '';
	return header.match(/^Bearer\s+(.+)$/i)?.[1]?.trim() ?? '';
}
