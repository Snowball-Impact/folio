import { env } from '$env/dynamic/private';
import type { RateLimitPolicy } from '$lib/server/rate-limit';

export type RateLimitAction =
	| 'powerbi-embed'
	| 'powerbi-publish'
	| 'thumbnail-capture'
	| 'thumbnail-upload'
	| 'body-image-upload'
	| 'comment-email'
	| 'project-view';

type PolicyDefaults = Pick<RateLimitPolicy, 'maxRequests' | 'windowSeconds'>;

const DEFAULT_POLICIES: Record<RateLimitAction, PolicyDefaults> = {
	'powerbi-embed': { maxRequests: 20, windowSeconds: 60 },
	'powerbi-publish': { maxRequests: 3, windowSeconds: 60 * 60 },
	'thumbnail-capture': { maxRequests: 5, windowSeconds: 10 * 60 },
	'thumbnail-upload': { maxRequests: 20, windowSeconds: 10 * 60 },
	'body-image-upload': { maxRequests: 20, windowSeconds: 10 * 60 },
	'comment-email': { maxRequests: 5, windowSeconds: 60 * 60 },
	'project-view': { maxRequests: 60, windowSeconds: 10 * 60 }
};

const ENVIRONMENT_NAMES: Record<RateLimitAction, { requests: string; window: string }> = {
	'powerbi-embed': {
		requests: 'RATE_LIMIT_POWERBI_EMBED_MAX_REQUESTS',
		window: 'RATE_LIMIT_POWERBI_EMBED_WINDOW_SECONDS'
	},
	'powerbi-publish': {
		requests: 'RATE_LIMIT_POWERBI_PUBLISH_MAX_REQUESTS',
		window: 'RATE_LIMIT_POWERBI_PUBLISH_WINDOW_SECONDS'
	},
	'thumbnail-capture': {
		requests: 'RATE_LIMIT_THUMBNAIL_CAPTURE_MAX_REQUESTS',
		window: 'RATE_LIMIT_THUMBNAIL_CAPTURE_WINDOW_SECONDS'
	},
	'thumbnail-upload': {
		requests: 'RATE_LIMIT_THUMBNAIL_UPLOAD_MAX_REQUESTS',
		window: 'RATE_LIMIT_THUMBNAIL_UPLOAD_WINDOW_SECONDS'
	},
	'body-image-upload': {
		requests: 'RATE_LIMIT_BODY_IMAGE_UPLOAD_MAX_REQUESTS',
		window: 'RATE_LIMIT_BODY_IMAGE_UPLOAD_WINDOW_SECONDS'
	},
	'comment-email': {
		requests: 'RATE_LIMIT_COMMENT_EMAIL_MAX_REQUESTS',
		window: 'RATE_LIMIT_COMMENT_EMAIL_WINDOW_SECONDS'
	},
	'project-view': {
		requests: 'RATE_LIMIT_PROJECT_VIEW_MAX_REQUESTS',
		window: 'RATE_LIMIT_PROJECT_VIEW_WINDOW_SECONDS'
	}
};

export function rateLimitPolicy(action: RateLimitAction, userId?: string | null): RateLimitPolicy {
	const defaults = DEFAULT_POLICIES[action];
	const names = ENVIRONMENT_NAMES[action];
	return {
		action,
		maxRequests: configuredPositiveInteger(env[names.requests], defaults.maxRequests, 10_000),
		windowSeconds: configuredPositiveInteger(env[names.window], defaults.windowSeconds, 86_400),
		userId
	};
}

function configuredPositiveInteger(value: string | undefined, fallback: number, maximum: number) {
	const parsed = Number(value);
	return Number.isInteger(parsed) && parsed >= 1 && parsed <= maximum ? parsed : fallback;
}
