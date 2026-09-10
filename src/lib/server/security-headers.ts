type SecurityHeaderOptions = {
	supabaseUrl?: string | null;
	rumEndpoint?: string | null;
	googleAnalyticsMeasurementId?: string | null;
	scriptNonce?: string | null;
};

const STATIC_CONNECT_SOURCES = [
	"'self'",
	'https://api.powerbi.com',
	'https://login.microsoftonline.com',
	'https://*.analysis.windows.net'
];

const FRAME_SOURCES = ["'self'", 'https://app.powerbi.com', 'https://*.powerbi.com', 'https://*.analysis.windows.net'];

const GOOGLE_ANALYTICS_SCRIPT_SOURCES = ['https://www.googletagmanager.com'];
const GOOGLE_ANALYTICS_CONNECT_SOURCES = [
	'https://www.google-analytics.com',
	'https://*.google-analytics.com',
	'https://stats.g.doubleclick.net'
];

export function securityHeaders(options: SecurityHeaderOptions = {}) {
	return {
		'Content-Security-Policy': contentSecurityPolicy(options),
		'Cross-Origin-Opener-Policy': 'same-origin-allow-popups',
		'Permissions-Policy': 'camera=(), microphone=(), geolocation=(), payment=(), usb=(), interest-cohort=()',
		'Referrer-Policy': 'strict-origin-when-cross-origin',
		'Strict-Transport-Security': 'max-age=15552000',
		'X-Content-Type-Options': 'nosniff',
		'X-Frame-Options': 'DENY'
	};
}

export function applySecurityHeaders(headers: Headers, options: SecurityHeaderOptions = {}) {
	for (const [name, value] of Object.entries(securityHeaders(options))) {
		headers.set(name, value);
	}
}

function contentSecurityPolicy(options: SecurityHeaderOptions) {
	const googleAnalyticsEnabled = isGoogleAnalyticsMeasurementId(options.googleAnalyticsMeasurementId);
	const connectSources = uniqueSources([
		...STATIC_CONNECT_SOURCES,
		...(googleAnalyticsEnabled ? GOOGLE_ANALYTICS_CONNECT_SOURCES : []),
		originSource(options.supabaseUrl),
		webSocketSource(options.supabaseUrl),
		originSource(options.rumEndpoint)
	]);
	const directives = [
		["default-src", "'self'"],
		["base-uri", "'self'"],
		['object-src', "'none'"],
		['frame-ancestors', "'none'"],
		['form-action', "'self'"],
		['img-src', "'self'", 'data:', 'blob:', 'https:'],
		['font-src', "'self'", 'data:'],
		['style-src', "'self'", "'unsafe-inline'"],
		['script-src', "'self'", nonceSource(options.scriptNonce), ...(googleAnalyticsEnabled ? GOOGLE_ANALYTICS_SCRIPT_SOURCES : [])],
		['connect-src', ...connectSources],
		['frame-src', ...FRAME_SOURCES],
		['child-src', ...FRAME_SOURCES],
		['worker-src', "'self'", 'blob:'],
		['media-src', "'self'", 'https:'],
		['manifest-src', "'self'"]
	];
	return directives.map((directive) => directive.filter(Boolean).join(' ')).join('; ');
}

function isGoogleAnalyticsMeasurementId(value: string | null | undefined) {
	return /^G-[A-Z0-9]+$/i.test(String(value ?? '').trim());
}

function nonceSource(value: string | null | undefined) {
	const nonce = String(value ?? '').trim();
	return nonce ? `'nonce-${nonce}'` : '';
}

function originSource(value: string | null | undefined) {
	try {
		const url = new URL(String(value ?? '').trim());
		return url.protocol === 'http:' || url.protocol === 'https:' ? url.origin : '';
	} catch {
		return '';
	}
}

function webSocketSource(value: string | null | undefined) {
	const origin = originSource(value);
	if (!origin) {
		return '';
	}
	return origin.replace(/^http:/, 'ws:').replace(/^https:/, 'wss:');
}

function uniqueSources(values: string[]) {
	return [...new Set(values.filter(Boolean))];
}
