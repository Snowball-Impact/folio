const FALLBACK_NEXT_PATH = '/';
const SAME_ORIGIN_BASE = 'https://folio.local';

export function safeInternalNextPath(value: string | null | undefined, fallback = FALLBACK_NEXT_PATH) {
	const fallbackPath = safeFallbackPath(fallback);
	const raw = String(value ?? '').trim();
	if (!raw || !raw.startsWith('/') || raw.startsWith('//') || raw.includes('\\') || hasControlCharacter(raw)) {
		return fallbackPath;
	}

	try {
		const url = new URL(raw, SAME_ORIGIN_BASE);
		if (url.origin !== SAME_ORIGIN_BASE || url.pathname === '/login') {
			return fallbackPath;
		}
		return `${url.pathname}${url.search}${url.hash}`;
	} catch {
		return fallbackPath;
	}
}

function safeFallbackPath(value: string) {
	return value.startsWith('/') && !value.startsWith('//') ? value : FALLBACK_NEXT_PATH;
}

function hasControlCharacter(value: string) {
	return /[\u0000-\u001f\u007f]/.test(value);
}
