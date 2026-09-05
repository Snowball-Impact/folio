import { n as getSupabaseUserClient, t as getSupabaseServerClient } from "./supabase.js";
import { json } from "@sveltejs/kit";
//#region lib/server/request-auth.ts
async function authenticateBearerRequest(request) {
	const accessToken = bearerToken(request);
	if (!accessToken) return {
		ok: false,
		reason: "missing-token"
	};
	const userClient = getSupabaseUserClient(accessToken);
	const serviceClient = getSupabaseServerClient();
	if (!userClient || !serviceClient) return {
		ok: false,
		reason: "unavailable"
	};
	const { data, error } = await userClient.auth.getUser(accessToken);
	if (error || !data.user) return {
		ok: false,
		reason: "invalid-session"
	};
	return {
		ok: true,
		accessToken,
		user: data.user,
		userClient,
		serviceClient
	};
}
function authFailureResponse(result, messages) {
	const message = result.reason === "missing-token" ? messages.missingToken : result.reason === "unavailable" ? messages.unavailable : messages.invalidSession;
	const status = result.reason === "unavailable" ? 503 : 401;
	return json({ error: message }, { status });
}
function getOwnedProjectQuery(context, projectId, columns) {
	return context.serviceClient.from("projects").select(columns).eq("id", projectId).eq("author_id", context.user.id);
}
function bearerToken(request) {
	return (request.headers.get("authorization") ?? "").match(/^Bearer\s+(.+)$/i)?.[1]?.trim() ?? "";
}
//#endregion
export { authenticateBearerRequest as n, getOwnedProjectQuery as r, authFailureResponse as t };
