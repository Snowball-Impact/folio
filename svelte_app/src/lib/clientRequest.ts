export async function fetchWithTimeout(url: string, init: RequestInit, timeoutMs: number) {
	const controller = new AbortController();
	const timeout = setTimeout(() => controller.abort(), timeoutMs);
	try {
		return await fetch(url, { ...init, signal: controller.signal });
	} finally {
		clearTimeout(timeout);
	}
}

export function requestErrorResponse(error: unknown, fallbackMessage: string, errorCode?: string) {
	const message = error instanceof Error && error.name !== 'AbortError' ? error.message : fallbackMessage;
	return new Response(JSON.stringify({ error: message, ...(errorCode ? { error_code: errorCode } : {}) }), {
		status: 408,
		headers: {
			'Content-Type': 'application/json'
		}
	});
}
