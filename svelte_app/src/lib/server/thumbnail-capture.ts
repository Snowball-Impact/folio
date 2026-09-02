import { env } from '$env/dynamic/private';
import { getSupabaseServerClient } from '$lib/server/supabase';

const DEFAULT_BUCKET = 'project-thumbnails';
const THUMBNAIL_WIDTH = 960;
const THUMBNAIL_HEIGHT = 540;
const DEFAULT_CAPTURE_TIMEOUT_SECONDS = 30;
const DEFAULT_CAPTURE_SETTLE_SECONDS = 10;
const CLOUDFLARE_SCREENSHOT_ENDPOINT = 'https://api.cloudflare.com/client/v4/accounts/{accountId}/browser-rendering/screenshot';

type ThumbnailCaptureErrorCode =
	| 'CAPTURE_SOURCE_MISSING'
	| 'CAPTURE_DISABLED'
	| 'CAPTURE_PROVIDER_UNSUPPORTED'
	| 'CAPTURE_CLOUDFLARE_CONFIG_MISSING'
	| 'CAPTURE_CLOUDFLARE_LOCAL_URL'
	| 'CAPTURE_CLOUDFLARE_FAILED'
	| 'CAPTURE_CLOUDFLARE_REQUEST_FAILED'
	| 'CAPTURE_CLOUDFLARE_EMPTY'
	| 'CAPTURE_SUPABASE_CONFIG_MISSING'
	| 'CAPTURE_UPLOAD_FAILED'
	| 'CAPTURE_PROJECT_UPDATE_FAILED'
	| 'CAPTURE_PLAYWRIGHT_MISSING'
	| 'CAPTURE_RESPONSE_INVALID';

type PlaywrightModule = {
	chromium: {
		launch: (options: Record<string, unknown>) => Promise<{
			newPage: (options: Record<string, unknown>) => Promise<{
				setDefaultTimeout: (timeout: number) => void;
				goto: (url: string, options: Record<string, unknown>) => Promise<unknown>;
				waitForLoadState: (state: string, options: Record<string, unknown>) => Promise<unknown>;
				waitForTimeout: (timeout: number) => Promise<unknown>;
				screenshot: (options: Record<string, unknown>) => Promise<Buffer>;
			}>;
			close: () => Promise<unknown>;
		}>;
	};
};

export class ThumbnailCaptureError extends Error {
	constructor(
		message: string,
		readonly status = 500,
		readonly code: ThumbnailCaptureErrorCode = 'CAPTURE_CLOUDFLARE_FAILED'
	) {
		super(message);
		this.name = 'ThumbnailCaptureError';
	}
}

export async function captureProjectThumbnail(projectId: string, sourceUrl: string) {
	const normalizedUrl = normalizeCaptureUrl(sourceUrl);
	if (!normalizedUrl) {
		throw new ThumbnailCaptureError('캡처할 URL을 찾지 못했습니다.', 400, 'CAPTURE_SOURCE_MISSING');
	}

	if (!isThumbnailCaptureEnabled()) {
		throw new ThumbnailCaptureError('자동 썸네일 캡처가 비활성화되어 있습니다.', 503, 'CAPTURE_DISABLED');
	}

	if (thumbnailCaptureProvider() === 'cloudflare') {
		if (isLoopbackUrl(normalizedUrl)) {
			throw new ThumbnailCaptureError(
				'Cloudflare 자동 캡처는 로컬 프리뷰 주소를 직접 캡처할 수 없습니다. 공개 배포 URL에서 캡처하거나 로컬 Playwright 캡처 설정을 사용하세요.',
				400,
				'CAPTURE_CLOUDFLARE_LOCAL_URL'
			);
		}
		const pngBytes = await captureWithCloudflareBrowserRun(normalizedUrl);
		return uploadCapturedThumbnail(projectId, pngBytes);
	}

	if (thumbnailCaptureProvider() !== 'local') {
		throw new ThumbnailCaptureError('지원하지 않는 썸네일 캡처 방식입니다.', 503, 'CAPTURE_PROVIDER_UNSUPPORTED');
	}

	const pngBytes = await captureWithLocalPlaywright(normalizedUrl);
	return uploadCapturedThumbnail(projectId, pngBytes);
}

async function captureWithLocalPlaywright(normalizedUrl: string) {
	const playwright = await loadPlaywright();
	const browser = await playwright.chromium.launch(launchOptions());
	try {
		const page = await browser.newPage({
			viewport: { width: THUMBNAIL_WIDTH, height: THUMBNAIL_HEIGHT },
			deviceScaleFactor: 1
		});
		page.setDefaultTimeout(captureTimeoutMs());
		await page.goto(fullscreenIframeCaptureUrl(normalizedUrl), {
			waitUntil: 'domcontentloaded',
			timeout: captureTimeoutMs()
		});
		await page.waitForLoadState('networkidle', { timeout: 7_000 }).catch(() => null);
		await page.waitForTimeout(captureSettleMs());
		const pngBytes = await page.screenshot({
			type: 'png',
			fullPage: false
		});
		return pngBytes;
	} finally {
		await browser.close();
	}
}

async function captureWithCloudflareBrowserRun(normalizedUrl: string) {
	const accountId = env.CLOUDFLARE_ACCOUNT_ID?.trim();
	const apiToken = env.CLOUDFLARE_BROWSER_RENDERING_API_TOKEN?.trim();
	if (!accountId || !apiToken) {
		throw new ThumbnailCaptureError('Cloudflare Browser Run 환경 변수가 설정되지 않았습니다.', 503, 'CAPTURE_CLOUDFLARE_CONFIG_MISSING');
	}

	const response = await cloudflareFetch(cloudflareScreenshotUrl(accountId), {
		method: 'POST',
		headers: {
			Authorization: `Bearer ${apiToken}`,
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({
			html: fullscreenIframeCaptureHtml(normalizedUrl),
			actionTimeout: captureTimeoutMs(),
			waitForTimeout: Math.min(captureSettleMs(), 60_000),
			viewport: {
				width: THUMBNAIL_WIDTH,
				height: THUMBNAIL_HEIGHT
			},
			screenshotOptions: {
				type: 'png',
				fullPage: false
			}
		})
	});

	if (!response.ok) {
		throw new ThumbnailCaptureError(
			await cloudflareErrorMessage(response),
			response.status >= 500 ? 502 : response.status,
			'CAPTURE_CLOUDFLARE_FAILED'
		);
	}

	const contentType = response.headers.get('content-type') ?? '';
	if (contentType.includes('application/json')) {
		return pngBytesFromCloudflareJson(await response.json().catch(() => null));
	}

	const bytes = new Uint8Array(await response.arrayBuffer());
	if (bytes.length === 0) {
		throw new ThumbnailCaptureError('Cloudflare Browser Run이 빈 스크린샷을 반환했습니다.', 502, 'CAPTURE_CLOUDFLARE_EMPTY');
	}
	return bytes;
}

async function uploadCapturedThumbnail(projectId: string, bytes: Uint8Array) {
	const serviceClient = getSupabaseServerClient();
	if (!serviceClient) {
		throw new ThumbnailCaptureError('Supabase 서버 환경 변수가 설정되지 않았습니다.', 503, 'CAPTURE_SUPABASE_CONFIG_MISSING');
	}

	const bucketName = env.THUMBNAIL_STORAGE_BUCKET || DEFAULT_BUCKET;
	const path = `projects/${safeStorageName(projectId)}/thumbnail-${Date.now()}.png`;
	const bucket = serviceClient.storage.from(bucketName);
	const { error: uploadError } = await bucket.upload(path, bytes, {
		contentType: 'image/png',
		cacheControl: '3600',
		upsert: true
	});
	if (uploadError) {
		throw new ThumbnailCaptureError('캡처 썸네일 업로드에 실패했습니다.', 502, 'CAPTURE_UPLOAD_FAILED');
	}

	await removeOldThumbnails(bucket, projectId, path);
	const publicUrl = cacheBustedUrl(bucket.getPublicUrl(path).data.publicUrl);
	const { error: updateError } = await serviceClient
		.from('projects')
		.update({
			thumbnail_url: publicUrl,
			thumbnail_mode: 'capture'
		})
		.eq('id', projectId);
	if (updateError) {
		throw new ThumbnailCaptureError('프로젝트에 캡처 썸네일을 연결하지 못했습니다.', 502, 'CAPTURE_PROJECT_UPDATE_FAILED');
	}

	return publicUrl;
}

async function loadPlaywright(): Promise<PlaywrightModule> {
	try {
		const dynamicImport = new Function('specifier', 'return import(specifier)') as (
			specifier: string
		) => Promise<PlaywrightModule>;
		return await dynamicImport('playwright');
	} catch {
		throw new ThumbnailCaptureError('서버 런타임에 Playwright가 설치되어 있지 않습니다.', 503, 'CAPTURE_PLAYWRIGHT_MISSING');
	}
}

function launchOptions() {
	const executablePath = env.CHROME_BINARY_PATH?.trim();
	return {
		headless: true,
		args: ['--disable-dev-shm-usage', '--no-sandbox'],
		...(executablePath ? { executablePath } : {})
	};
}

function captureSettleMs() {
	return Math.max(Number(env.POWERBI_CAPTURE_READY_WAIT_SECONDS ?? DEFAULT_CAPTURE_SETTLE_SECONDS), 0) * 1000;
}

function captureTimeoutMs() {
	return Math.max(Number(env.THUMBNAIL_CAPTURE_ACTION_TIMEOUT_SECONDS ?? DEFAULT_CAPTURE_TIMEOUT_SECONDS), 1) * 1000;
}

function isThumbnailCaptureEnabled() {
	return env.THUMBNAIL_CAPTURE_ENABLED !== 'false';
}

function thumbnailCaptureProvider() {
	const provider = env.THUMBNAIL_CAPTURE_PROVIDER?.trim().toLowerCase();
	if (provider) {
		return provider;
	}
	return env.CLOUDFLARE_ACCOUNT_ID && env.CLOUDFLARE_BROWSER_RENDERING_API_TOKEN ? 'cloudflare' : 'local';
}

function normalizeCaptureUrl(value: string) {
	let rawValue = value.trim();
	if (!rawValue) {
		return null;
	}
	if (rawValue.toLowerCase().startsWith('<iframe')) {
		const match = rawValue.match(/\ssrc=["']([^"']+)["']/i);
		rawValue = match?.[1]?.trim() || rawValue;
	}
	try {
		const url = new URL(rawValue);
		return ['http:', 'https:'].includes(url.protocol) && url.hostname ? rawValue : null;
	} catch {
		return null;
	}
}

function isLoopbackUrl(value: string) {
	const hostname = new URL(value).hostname.toLowerCase();
	return hostname === 'localhost' || hostname === '127.0.0.1' || hostname === '::1' || hostname.endsWith('.localhost');
}

function fullscreenIframeCaptureUrl(url: string) {
	return `data:text/html;charset=utf-8,${encodeURIComponent(fullscreenIframeCaptureHtml(url))}`;
}

function fullscreenIframeCaptureHtml(url: string) {
	const escapedUrl = cacheBustedCaptureSourceUrl(url).replaceAll('"', '%22');
	return `<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
html, body { background: #ffffff; height: 100%; margin: 0; overflow: hidden; width: 100%; }
iframe { border: 0; height: 100vh; inset: 0; position: fixed; width: 100vw; }
</style>
</head>
<body>
<iframe src="${escapedUrl}" allowfullscreen></iframe>
</body>
</html>`;
}

function cacheBustedCaptureSourceUrl(value: string) {
	const url = new URL(value);
	url.searchParams.set('folio_capture_v', String(Date.now()));
	return url.toString();
}

async function removeOldThumbnails(
	bucket: {
		list: (path: string) => Promise<{ data: Array<{ name: string }> | null }>;
		remove: (paths: string[]) => Promise<unknown>;
	},
	projectId: string,
	keepPath: string
) {
	const directory = `projects/${safeStorageName(projectId)}`;
	const { data } = await bucket.list(directory);
	const oldPaths = (data ?? []).map((item) => `${directory}/${item.name}`).filter((path) => path !== keepPath);
	if (oldPaths.length > 0) {
		await bucket.remove(oldPaths);
	}
}

function safeStorageName(value: string) {
	return value.replace(/[^a-zA-Z0-9_-]/g, '_');
}

function cacheBustedUrl(url: string) {
	const separator = url.includes('?') ? '&' : '?';
	return `${url}${separator}v=${Date.now()}`;
}

function cloudflareScreenshotUrl(accountId: string) {
	const url = new URL(CLOUDFLARE_SCREENSHOT_ENDPOINT.replace('{accountId}', encodeURIComponent(accountId)));
	url.searchParams.set('cacheTTL', '0');
	return url.toString();
}

async function cloudflareFetch(input: string, init: RequestInit) {
	try {
		return await fetch(input, init);
	} catch (error) {
		const message = error instanceof Error ? ` ${error.message.replace(/\s+/g, ' ').trim().slice(0, 240)}` : '';
		throw new ThumbnailCaptureError(
			`Cloudflare Browser Run 요청에 실패했습니다.${message}`,
			502,
			'CAPTURE_CLOUDFLARE_REQUEST_FAILED'
		);
	}
}

async function cloudflareErrorMessage(response: Response) {
	const fallback = 'Cloudflare Browser Run 썸네일 캡처에 실패했습니다.';
	const payload = await response.json().catch(() => null);
	if (!payload || typeof payload !== 'object') {
		return fallback;
	}
	const errors: unknown[] = 'errors' in payload && Array.isArray(payload.errors) ? payload.errors : [];
	const message = errors
		.map((error: unknown) => (error && typeof error === 'object' && 'message' in error ? String(error.message) : ''))
		.find(Boolean);
	return message ? `${fallback} ${message}` : fallback;
}

function pngBytesFromCloudflareJson(payload: unknown) {
	if (!payload || typeof payload !== 'object') {
		throw new ThumbnailCaptureError('Cloudflare Browser Run 응답을 확인할 수 없습니다.', 502, 'CAPTURE_RESPONSE_INVALID');
	}
	const record = payload as { result?: unknown; screenshot?: unknown };
	const screenshot = typeof record.screenshot === 'string'
		? record.screenshot
		: record.result && typeof record.result === 'object' && 'screenshot' in record.result
			? (record.result as { screenshot?: unknown }).screenshot
			: null;
	if (typeof screenshot !== 'string' || !screenshot) {
		throw new ThumbnailCaptureError('Cloudflare Browser Run 스크린샷 응답이 비어 있습니다.', 502, 'CAPTURE_CLOUDFLARE_EMPTY');
	}
	return Uint8Array.from(Buffer.from(screenshot, 'base64'));
}
