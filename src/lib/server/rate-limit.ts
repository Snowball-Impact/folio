type RateLimitClient = {
	rpc: (
		functionName: string,
		parameters: Record<string, unknown>
	) => PromiseLike<{ data: boolean | null; error: { message: string } | null }>;
};

export type RateLimitPolicy = {
	action: string;
	maxRequests: number;
	windowSeconds: number;
	userId?: string | null;
};

export type RateLimitResult =
	| { ok: true }
	| { ok: false; reason: 'limited'; retryAfterSeconds: number }
	| { ok: false; reason: 'unavailable'; retryAfterSeconds: number };

// Cloudflare Pages overwrites this header at the edge. Do not accept client-controlled
// forwarding headers such as X-Forwarded-For for an unauthenticated rate-limit key.
const CLOUDFLARE_CLIENT_IP_HEADER = 'cf-connecting-ip';
const IP_ADDRESS_PATTERN = /^[0-9a-f:.]+$/i;
const ACTION_PATTERN = /^[a-z0-9-]{1,64}$/;

export async function enforceRateLimit(
	client: RateLimitClient | null,
	headers: Headers,
	policy: RateLimitPolicy
): Promise<RateLimitResult> {
	if (!client || !ACTION_PATTERN.test(policy.action) || !isValidPolicy(policy)) {
		return unavailable(policy.windowSeconds);
	}

	for (const subject of rateLimitSubjects(headers, policy.userId)) {
		const rateKey = await opaqueIdentifier(`${policy.action}:${subject}`);
		const { data, error } = await client.rpc('consume_server_rate_limit', {
			p_rate_key: rateKey,
			p_max_requests: policy.maxRequests,
			p_window_seconds: policy.windowSeconds
		});
		if (error) {
			return unavailable(policy.windowSeconds);
		}
		if (data !== true) {
			return {
				ok: false,
				reason: 'limited',
				retryAfterSeconds: policy.windowSeconds
			};
		}
	}

	return { ok: true };
}

export function rateLimitSubjects(headers: Headers, userId?: string | null) {
	const subjects = [`ip:${clientIpAddress(headers)}`];
	if (isUuid(userId)) {
		subjects.push(`user:${String(userId).toLowerCase()}`);
	}
	return subjects;
}

export function clientIpAddress(headers: Headers) {
	const value = headers.get(CLOUDFLARE_CLIENT_IP_HEADER)?.trim().replace(/^\[|\]$/g, '') ?? '';
	if (value.length <= 45 && IP_ADDRESS_PATTERN.test(value) && (value.includes('.') || value.includes(':'))) {
		return value.toLowerCase();
	}
	return 'unknown';
}

export function rateLimitResponseInit(result: Exclude<RateLimitResult, { ok: true }>) {
	return {
		status: result.reason === 'limited' ? 429 : 503,
		headers: {
			'Retry-After': String(result.retryAfterSeconds)
		}
	};
}

export async function opaqueIdentifier(value: string) {
	const bytes = new TextEncoder().encode(value);
	const digest = await crypto.subtle.digest('SHA-256', bytes);
	return Array.from(new Uint8Array(digest), (byte) => byte.toString(16).padStart(2, '0')).join('');
}

function isValidPolicy(policy: RateLimitPolicy) {
	return (
		Number.isInteger(policy.maxRequests) &&
		policy.maxRequests >= 1 &&
		policy.maxRequests <= 10_000 &&
		Number.isInteger(policy.windowSeconds) &&
		policy.windowSeconds >= 1 &&
		policy.windowSeconds <= 86_400
	);
}

function unavailable(windowSeconds: number): RateLimitResult {
	return {
		ok: false,
		reason: 'unavailable',
		retryAfterSeconds: Number.isInteger(windowSeconds) && windowSeconds > 0 ? windowSeconds : 60
	};
}

function isUuid(value: string | null | undefined) {
	return /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(
		String(value ?? '')
	);
}
