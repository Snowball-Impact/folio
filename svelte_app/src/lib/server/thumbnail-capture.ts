import { env } from '$env/dynamic/private';
import { getSupabaseServerClient } from '$lib/server/supabase';

const DEFAULT_BUCKET = 'project-thumbnails';
const THUMBNAIL_WIDTH = 960;
const THUMBNAIL_HEIGHT = 540;
const CAPTURE_TIMEOUT_MS = 18_000;
const DEFAULT_CAPTURE_SETTLE_SECONDS = 10;

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
		readonly status = 500
	) {
		super(message);
		this.name = 'ThumbnailCaptureError';
	}
}

export async function captureProjectThumbnail(projectId: string, sourceUrl: string) {
	const normalizedUrl = normalizeCaptureUrl(sourceUrl);
	if (!normalizedUrl) {
		throw new ThumbnailCaptureError('캡처할 URL을 찾지 못했습니다.', 400);
	}

	const playwright = await loadPlaywright();
	const browser = await playwright.chromium.launch(launchOptions());
	try {
		const page = await browser.newPage({
			viewport: { width: THUMBNAIL_WIDTH, height: THUMBNAIL_HEIGHT },
			deviceScaleFactor: 1
		});
		page.setDefaultTimeout(CAPTURE_TIMEOUT_MS);
		await page.goto(fullscreenIframeCaptureUrl(normalizedUrl), {
			waitUntil: 'domcontentloaded',
			timeout: CAPTURE_TIMEOUT_MS
		});
		await page.waitForLoadState('networkidle', { timeout: 7_000 }).catch(() => null);
		await page.waitForTimeout(captureSettleMs());
		const pngBytes = await page.screenshot({
			type: 'png',
			fullPage: false
		});
		return uploadCapturedThumbnail(projectId, pngBytes);
	} finally {
		await browser.close();
	}
}

async function uploadCapturedThumbnail(projectId: string, bytes: Uint8Array) {
	const serviceClient = getSupabaseServerClient();
	if (!serviceClient) {
		throw new ThumbnailCaptureError('Supabase 서버 환경 변수가 설정되지 않았습니다.', 503);
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
		throw new ThumbnailCaptureError('캡처 썸네일 업로드에 실패했습니다.', 502);
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
		throw new ThumbnailCaptureError('프로젝트에 캡처 썸네일을 연결하지 못했습니다.', 502);
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
		throw new ThumbnailCaptureError('서버 런타임에 Playwright가 설치되어 있지 않습니다.', 503);
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

function fullscreenIframeCaptureUrl(url: string) {
	const escapedUrl = cacheBustedCaptureSourceUrl(url).replaceAll('"', '%22');
	const html = `<!doctype html>
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
	return `data:text/html;charset=utf-8,${encodeURIComponent(html)}`;
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
