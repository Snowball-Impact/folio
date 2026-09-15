const SAME_ORIGIN_BASE = 'https://folio.local';

export function safeInternalNextPath(value: string | null | undefined, fallback = '/') {
	const safeFallback = fallback.startsWith('/') && !fallback.startsWith('//') ? fallback : '/';
	const raw = String(value ?? '').trim();
	if (!raw || !raw.startsWith('/') || raw.startsWith('//') || raw.includes('\\') || /[\u0000-\u001f\u007f]/.test(raw)) {
		return safeFallback;
	}
	try {
		const url = new URL(raw, SAME_ORIGIN_BASE);
		return url.origin === SAME_ORIGIN_BASE && url.pathname !== '/login'
			? `${url.pathname}${url.search}${url.hash}`
			: safeFallback;
	} catch {
		return safeFallback;
	}
}
