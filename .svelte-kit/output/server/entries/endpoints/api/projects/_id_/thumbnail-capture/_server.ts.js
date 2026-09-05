import { t as private_env } from "../../../../../../chunks/shared-server.js";
import { t as getSupabaseServerClient } from "../../../../../../chunks/supabase.js";
import { n as authenticateBearerRequest, r as getOwnedProjectQuery, t as authFailureResponse } from "../../../../../../chunks/request-auth.js";
import { json } from "@sveltejs/kit";
//#region lib/server/thumbnail-capture.ts
var DEFAULT_BUCKET = "project-thumbnails";
var THUMBNAIL_WIDTH = 960;
var THUMBNAIL_HEIGHT = 540;
var DEFAULT_CAPTURE_TIMEOUT_SECONDS = 30;
var DEFAULT_CAPTURE_SETTLE_SECONDS = 10;
var CLOUDFLARE_SCREENSHOT_ENDPOINT = "https://api.cloudflare.com/client/v4/accounts/{accountId}/browser-rendering/screenshot";
var ThumbnailCaptureError = class extends Error {
	status;
	code;
	constructor(message, status = 500, code = "CAPTURE_CLOUDFLARE_FAILED") {
		super(message);
		this.status = status;
		this.code = code;
		this.name = "ThumbnailCaptureError";
	}
};
async function captureProjectThumbnail(projectId, sourceUrl) {
	const normalizedUrl = normalizeCaptureUrl(sourceUrl);
	if (!normalizedUrl) throw new ThumbnailCaptureError("캡처할 URL을 찾지 못했습니다.", 400, "CAPTURE_SOURCE_MISSING");
	if (!isThumbnailCaptureEnabled()) throw new ThumbnailCaptureError("자동 썸네일 캡처가 비활성화되어 있습니다.", 503, "CAPTURE_DISABLED");
	if (thumbnailCaptureProvider$1() === "cloudflare") {
		if (isLoopbackUrl$1(normalizedUrl)) throw new ThumbnailCaptureError("Cloudflare 자동 캡처는 로컬 프리뷰 주소를 직접 캡처할 수 없습니다. 공개 배포 URL에서 캡처하거나 로컬 Playwright 캡처 설정을 사용하세요.", 400, "CAPTURE_CLOUDFLARE_LOCAL_URL");
		return uploadCapturedThumbnail(projectId, await captureWithCloudflareBrowserRun(normalizedUrl));
	}
	if (thumbnailCaptureProvider$1() !== "local") throw new ThumbnailCaptureError("지원하지 않는 썸네일 캡처 방식입니다.", 503, "CAPTURE_PROVIDER_UNSUPPORTED");
	return uploadCapturedThumbnail(projectId, await captureWithLocalPlaywright(normalizedUrl));
}
async function captureWithLocalPlaywright(normalizedUrl) {
	const browser = await (await loadPlaywright()).chromium.launch(launchOptions());
	try {
		const page = await browser.newPage({
			viewport: {
				width: THUMBNAIL_WIDTH,
				height: THUMBNAIL_HEIGHT
			},
			deviceScaleFactor: 1
		});
		page.setDefaultTimeout(captureTimeoutMs());
		await page.goto(fullscreenIframeCaptureUrl(normalizedUrl), {
			waitUntil: "domcontentloaded",
			timeout: captureTimeoutMs()
		});
		await page.waitForLoadState("networkidle", { timeout: 7e3 }).catch(() => null);
		await page.waitForTimeout(captureSettleMs());
		return await page.screenshot({
			type: "png",
			fullPage: false
		});
	} finally {
		await browser.close();
	}
}
async function captureWithCloudflareBrowserRun(normalizedUrl) {
	const accountId = private_env.CLOUDFLARE_ACCOUNT_ID?.trim();
	const apiToken = private_env.CLOUDFLARE_BROWSER_RENDERING_API_TOKEN?.trim();
	if (!accountId || !apiToken) throw new ThumbnailCaptureError("Cloudflare Browser Run 환경 변수가 설정되지 않았습니다.", 503, "CAPTURE_CLOUDFLARE_CONFIG_MISSING");
	const response = await cloudflareFetch(cloudflareScreenshotUrl(accountId), {
		method: "POST",
		headers: {
			Authorization: `Bearer ${apiToken}`,
			"Content-Type": "application/json"
		},
		body: JSON.stringify({
			html: fullscreenIframeCaptureHtml(normalizedUrl),
			actionTimeout: captureTimeoutMs(),
			waitForTimeout: Math.min(captureSettleMs(), 6e4),
			viewport: {
				width: THUMBNAIL_WIDTH,
				height: THUMBNAIL_HEIGHT
			},
			screenshotOptions: {
				type: "png",
				fullPage: false
			}
		})
	});
	if (!response.ok) throw new ThumbnailCaptureError(await cloudflareErrorMessage(response), response.status >= 500 ? 502 : response.status, "CAPTURE_CLOUDFLARE_FAILED");
	if ((response.headers.get("content-type") ?? "").includes("application/json")) return pngBytesFromCloudflareJson(await response.json().catch(() => null));
	const bytes = new Uint8Array(await response.arrayBuffer());
	if (bytes.length === 0) throw new ThumbnailCaptureError("Cloudflare Browser Run이 빈 스크린샷을 반환했습니다.", 502, "CAPTURE_CLOUDFLARE_EMPTY");
	return bytes;
}
async function uploadCapturedThumbnail(projectId, bytes) {
	const serviceClient = getSupabaseServerClient();
	if (!serviceClient) throw new ThumbnailCaptureError("Supabase 서버 환경 변수가 설정되지 않았습니다.", 503, "CAPTURE_SUPABASE_CONFIG_MISSING");
	const bucketName = private_env.THUMBNAIL_STORAGE_BUCKET || DEFAULT_BUCKET;
	const path = `projects/${safeStorageName(projectId)}/thumbnail-${Date.now()}.png`;
	const bucket = serviceClient.storage.from(bucketName);
	const { error: uploadError } = await bucket.upload(path, bytes, {
		contentType: "image/png",
		cacheControl: "3600",
		upsert: true
	});
	if (uploadError) throw new ThumbnailCaptureError("캡처 썸네일 업로드에 실패했습니다.", 502, "CAPTURE_UPLOAD_FAILED");
	await removeOldThumbnails(bucket, projectId, path);
	const publicUrl = cacheBustedUrl(bucket.getPublicUrl(path).data.publicUrl);
	const { error: updateError } = await serviceClient.from("projects").update({
		thumbnail_url: publicUrl,
		thumbnail_mode: "capture"
	}).eq("id", projectId);
	if (updateError) {
		await bucket.remove([path]).catch(() => null);
		throw new ThumbnailCaptureError("프로젝트에 캡처 썸네일을 연결하지 못했습니다.", 502, "CAPTURE_PROJECT_UPDATE_FAILED");
	}
	return publicUrl;
}
async function loadPlaywright() {
	try {
		return await new Function("specifier", "return import(specifier)")("playwright");
	} catch {
		throw new ThumbnailCaptureError("서버 런타임에 Playwright가 설치되어 있지 않습니다.", 503, "CAPTURE_PLAYWRIGHT_MISSING");
	}
}
function launchOptions() {
	const executablePath = private_env.CHROME_BINARY_PATH?.trim();
	return {
		headless: true,
		args: ["--disable-dev-shm-usage", "--no-sandbox"],
		...executablePath ? { executablePath } : {}
	};
}
function captureSettleMs() {
	return Math.max(Number(private_env.POWERBI_CAPTURE_READY_WAIT_SECONDS ?? DEFAULT_CAPTURE_SETTLE_SECONDS), 0) * 1e3;
}
function captureTimeoutMs() {
	return Math.max(Number(private_env.THUMBNAIL_CAPTURE_ACTION_TIMEOUT_SECONDS ?? DEFAULT_CAPTURE_TIMEOUT_SECONDS), 1) * 1e3;
}
function isThumbnailCaptureEnabled() {
	return private_env.THUMBNAIL_CAPTURE_ENABLED !== "false";
}
function thumbnailCaptureProvider$1() {
	const provider = private_env.THUMBNAIL_CAPTURE_PROVIDER?.trim().toLowerCase();
	if (provider) return provider;
	return private_env.CLOUDFLARE_ACCOUNT_ID && private_env.CLOUDFLARE_BROWSER_RENDERING_API_TOKEN ? "cloudflare" : "local";
}
function normalizeCaptureUrl(value) {
	let rawValue = value.trim();
	if (!rawValue) return null;
	if (rawValue.toLowerCase().startsWith("<iframe")) rawValue = rawValue.match(/\ssrc=["']([^"']+)["']/i)?.[1]?.trim() || rawValue;
	try {
		const url = new URL(rawValue);
		return ["http:", "https:"].includes(url.protocol) && url.hostname ? rawValue : null;
	} catch {
		return null;
	}
}
function isLoopbackUrl$1(value) {
	const hostname = new URL(value).hostname.toLowerCase();
	return hostname === "localhost" || hostname === "127.0.0.1" || hostname === "::1" || hostname.endsWith(".localhost");
}
function fullscreenIframeCaptureUrl(url) {
	return `data:text/html;charset=utf-8,${encodeURIComponent(fullscreenIframeCaptureHtml(url))}`;
}
function fullscreenIframeCaptureHtml(url) {
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
<iframe src="${cacheBustedCaptureSourceUrl(url).replaceAll("\"", "%22")}" allowfullscreen></iframe>
</body>
</html>`;
}
function cacheBustedCaptureSourceUrl(value) {
	const url = new URL(value);
	url.searchParams.set("folio_capture_v", String(Date.now()));
	return url.toString();
}
async function removeOldThumbnails(bucket, projectId, keepPath) {
	const directory = `projects/${safeStorageName(projectId)}`;
	const { data } = await bucket.list(directory);
	const oldPaths = (data ?? []).map((item) => `${directory}/${item.name}`).filter((path) => path !== keepPath);
	if (oldPaths.length > 0) await bucket.remove(oldPaths);
}
function safeStorageName(value) {
	return value.replace(/[^a-zA-Z0-9_-]/g, "_");
}
function cacheBustedUrl(url) {
	return `${url}${url.includes("?") ? "&" : "?"}v=${Date.now()}`;
}
function cloudflareScreenshotUrl(accountId) {
	const url = new URL(CLOUDFLARE_SCREENSHOT_ENDPOINT.replace("{accountId}", encodeURIComponent(accountId)));
	url.searchParams.set("cacheTTL", "0");
	return url.toString();
}
async function cloudflareFetch(input, init) {
	try {
		return await fetch(input, init);
	} catch (error) {
		throw new ThumbnailCaptureError(`Cloudflare Browser Run 요청에 실패했습니다.${error instanceof Error ? ` ${error.message.replace(/\s+/g, " ").trim().slice(0, 240)}` : ""}`, 502, "CAPTURE_CLOUDFLARE_REQUEST_FAILED");
	}
}
async function cloudflareErrorMessage(response) {
	const fallback = "Cloudflare Browser Run 썸네일 캡처에 실패했습니다.";
	const payload = await response.json().catch(() => null);
	if (!payload || typeof payload !== "object") return fallback;
	const message = ("errors" in payload && Array.isArray(payload.errors) ? payload.errors : []).map((error) => error && typeof error === "object" && "message" in error ? String(error.message) : "").find(Boolean);
	return message ? `${fallback} ${message}` : fallback;
}
function pngBytesFromCloudflareJson(payload) {
	if (!payload || typeof payload !== "object") throw new ThumbnailCaptureError("Cloudflare Browser Run 응답을 확인할 수 없습니다.", 502, "CAPTURE_RESPONSE_INVALID");
	const record = payload;
	const screenshot = typeof record.screenshot === "string" ? record.screenshot : record.result && typeof record.result === "object" && "screenshot" in record.result ? record.result.screenshot : null;
	if (typeof screenshot !== "string" || !screenshot) throw new ThumbnailCaptureError("Cloudflare Browser Run 스크린샷 응답이 비어 있습니다.", 502, "CAPTURE_CLOUDFLARE_EMPTY");
	return Uint8Array.from(Buffer.from(screenshot, "base64"));
}
//#endregion
//#region routes/api/projects/[id]/thumbnail-capture/+server.ts
var POST = async ({ params, request, url }) => {
	const projectId = params.id;
	if (!projectId) return json({ error: "프로젝트 ID가 없습니다." }, { status: 400 });
	const auth = await authenticateBearerRequest(request);
	if (!auth.ok) return authFailureResponse(auth, {
		missingToken: "로그인 후 썸네일을 캡처할 수 있습니다.",
		unavailable: "썸네일 캡처 서버 환경 변수가 설정되지 않았습니다.",
		invalidSession: "로그인 세션을 확인하지 못했습니다."
	});
	const { data: project, error: projectError } = await getOwnedProjectQuery(auth, projectId, "id,author_id,status,project_type,embed_status,power_bi_url,report_url").maybeSingle();
	if (projectError || !project || project.status === "deleted") return json({ error: "캡처할 프로젝트를 찾을 수 없습니다." }, { status: 404 });
	const sourceUrl = captureSourceUrl(project, projectId, url);
	if (!sourceUrl) return json({ error: "캡처할 Embed Code 또는 Web App URL이 없습니다." }, { status: 400 });
	try {
		const thumbnailUrl = await captureProjectThumbnail(projectId, sourceUrl);
		return json({ thumbnail_url: thumbnailUrl });
	} catch (error) {
		if (error instanceof ThumbnailCaptureError) return json({
			error: error.message,
			error_code: error.code
		}, { status: error.status });
		return json({
			error: "썸네일 캡처 중 오류가 발생했습니다.",
			error_code: "CAPTURE_UNKNOWN"
		}, { status: 500 });
	}
};
function captureSourceUrl(project, projectId, requestUrl) {
	if (project.project_type === "powerbi" && project.embed_status === "supported") {
		const detailUrl = new URL(`/projects/${encodeURIComponent(projectId)}`, captureDetailOrigin(requestUrl));
		detailUrl.searchParams.set("capture", "thumbnail");
		return detailUrl.toString();
	}
	return project.power_bi_url || project.report_url;
}
function captureDetailOrigin(requestUrl) {
	if (thumbnailCaptureProvider() !== "cloudflare" || !isLoopbackUrl(requestUrl)) return requestUrl.origin;
	const appUrl = publicAppUrl();
	if (appUrl && !isLoopbackUrl(appUrl)) return appUrl.origin;
	return requestUrl.origin;
}
function publicAppUrl() {
	const rawValue = private_env.APP_URL?.trim();
	if (!rawValue) return null;
	try {
		return new URL(rawValue);
	} catch {
		return null;
	}
}
function thumbnailCaptureProvider() {
	const provider = private_env.THUMBNAIL_CAPTURE_PROVIDER?.trim().toLowerCase();
	if (provider) return provider;
	return private_env.CLOUDFLARE_ACCOUNT_ID && private_env.CLOUDFLARE_BROWSER_RENDERING_API_TOKEN ? "cloudflare" : "local";
}
function isLoopbackUrl(url) {
	const hostname = url.hostname.toLowerCase();
	return hostname === "localhost" || hostname === "127.0.0.1" || hostname === "::1" || hostname.endsWith(".localhost");
}
//#endregion
export { POST };
