import { env as publicEnv } from '$env/dynamic/public';
import type { Handle } from '@sveltejs/kit';
import { applySecurityHeaders } from '$lib/server/security-headers';

export const handle: Handle = async ({ event, resolve }) => {
	const scriptNonce = createScriptNonce();
	const response = await resolve(event, {
		transformPageChunk: ({ html }) => html.replace(/<script(?![^>]*\bnonce=)(\s|>)/g, `<script nonce="${scriptNonce}"$1`)
	});
	applySecurityHeaders(response.headers, {
		supabaseUrl: publicEnv.PUBLIC_SUPABASE_URL,
		rumEndpoint: publicEnv.PUBLIC_RUM_ENDPOINT,
		googleAnalyticsMeasurementId: publicEnv.PUBLIC_GA_MEASUREMENT_ID,
		scriptNonce
	});
	return response;
};

function createScriptNonce() {
	const bytes = new Uint8Array(16);
	crypto.getRandomValues(bytes);
	let binary = '';
	for (const byte of bytes) {
		binary += String.fromCharCode(byte);
	}
	return btoa(binary);
}
