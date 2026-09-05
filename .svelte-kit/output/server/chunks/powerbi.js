import { t as private_env } from "./shared-server.js";
import { t as getSupabaseServerClient } from "./supabase.js";
import { t as getSupabaseClient } from "./supabase2.js";
//#region lib/server/powerbi.ts
var POWERBI_SCOPE = "https://analysis.windows.net/powerbi/api/.default";
var DEFAULT_POWERBI_API_BASE_URL = "https://api.powerbi.com/v1.0/myorg";
var DEFAULT_PBIX_MAX_UPLOAD_MB = 50;
var DEFAULT_IMPORT_POLL_SECONDS = 30;
var IMPORT_SUCCEEDED_STATES = /* @__PURE__ */ new Set(["succeeded", "completed"]);
var IMPORT_FAILED_STATES = /* @__PURE__ */ new Set(["failed"]);
var PowerBIServiceError = class extends Error {
	status;
	code;
	upstreamStatus;
	upstreamCode;
	constructor(message, status = 500, code = "PBI_IMPORT_UPLOAD_FAILED", upstreamStatus = null, upstreamCode = null) {
		super(message);
		this.status = status;
		this.code = code;
		this.upstreamStatus = upstreamStatus;
		this.upstreamCode = upstreamCode;
		this.name = "PowerBIServiceError";
	}
};
function isPowerBIConfigured() {
	return Boolean(private_env.POWERBI_TENANT_ID && private_env.POWERBI_CLIENT_ID && private_env.POWERBI_CLIENT_SECRET && private_env.POWERBI_WORKSPACE_ID);
}
async function publishPbixForProject(projectId, file, originalFilename = file.name) {
	validatePbixUpload(file, originalFilename);
	if (!isPowerBIConfigured()) throw new PowerBIServiceError("Power BI 게시 환경 변수가 설정되지 않았습니다.", 503, "PBI_CONFIG_MISSING");
	if (!getSupabaseServerClient()) throw new PowerBIServiceError("Supabase 서버 환경 변수가 설정되지 않았습니다.", 503, "PBI_SUPABASE_CONFIG_MISSING");
	const accessToken = await fetchPowerBIAccessToken();
	const importId = (await postPbixImport(accessToken, file, datasetDisplayName(projectId, originalFilename))).id?.trim();
	if (!importId) throw new PowerBIServiceError("Power BI Import 응답을 확인할 수 없습니다.", 502, "PBI_IMPORT_RESPONSE_INVALID");
	await markProjectPowerBIProcessing(projectId, importId, "publishing", "Power BI Import를 시작했습니다.");
	const importState = await pollImportCompletion(accessToken, importId);
	const importStatus = normalizeImportStatus(importState);
	if (!IMPORT_SUCCEEDED_STATES.has(importStatus)) {
		const message = IMPORT_FAILED_STATES.has(importStatus) ? "Power BI 게시에 실패했습니다. PBIX 파일과 Workspace 권한을 확인하세요." : "Power BI 게시가 아직 완료되지 않았습니다. 잠시 후 다시 확인하세요.";
		if (IMPORT_FAILED_STATES.has(importStatus)) await markProjectPowerBIFailed(projectId, importId, importStatus, message);
		else await markProjectPowerBIProcessing(projectId, importId, importStatus || "processing", message);
		return emptyImportResult(false, message, IMPORT_FAILED_STATES.has(importStatus) ? "PBI_IMPORT_STATUS_FAILED" : "PBI_IMPORT_INCOMPLETE", projectId, importId, importStatus || "processing");
	}
	const report = firstReportFromImport(importState);
	const reportId = report.id?.trim();
	if (!reportId) throw new PowerBIServiceError("Power BI Report ID를 확인할 수 없습니다.", 502, "PBI_REPORT_ID_MISSING");
	const reportMetadata = await getReportMetadata(accessToken, reportId);
	const datasetId = reportMetadata.datasetId || report.datasetId || null;
	const embedUrl = reportMetadata.embedUrl || report.embedUrl || null;
	await upsertPowerBIReport(projectId, {
		workspace_id: private_env.POWERBI_WORKSPACE_ID,
		report_id: reportId,
		dataset_id: datasetId,
		embed_url: embedUrl,
		web_url: reportMetadata.webUrl || report.webUrl || null,
		import_id: importId,
		import_status: importStatus,
		error_code: null,
		error_message: null
	});
	await markProjectPowerBIPublished(projectId, embedUrl);
	return {
		ok: true,
		message: "Power BI 보고서가 게시되었습니다.",
		projectId,
		importId,
		importStatus,
		reportId,
		datasetId,
		embedUrl
	};
}
async function getPowerBIEmbedConfig(projectId) {
	const report = await getPowerBIReportForProject(projectId);
	if (!report) return null;
	const reportId = report.report_id?.trim();
	const datasetId = report.dataset_id?.trim();
	const embedUrl = report.embed_url?.trim();
	if (!reportId || !datasetId || !embedUrl) return null;
	const tokenPayload = await generateEmbedToken(reportId, datasetId);
	const embedToken = tokenPayload.token;
	if (!embedToken) throw new PowerBIServiceError("Power BI Embed Token 응답을 확인할 수 없습니다.", 502, "PBI_EMBED_TOKEN_EMPTY");
	return {
		report_id: reportId,
		dataset_id: datasetId,
		embed_url: embedUrl,
		embed_token: embedToken,
		token_expiration: tokenPayload.expiration ?? null
	};
}
async function getPowerBIReportForProject(projectId) {
	const supabase = getSupabaseClient();
	if (!supabase) throw new PowerBIServiceError("Supabase 환경 변수가 설정되지 않았습니다.", 503, "PBI_SUPABASE_CONFIG_MISSING");
	const { data, error } = await supabase.from("powerbi_reports").select("report_id,dataset_id,embed_url").eq("project_id", projectId).maybeSingle();
	if (error) throw new PowerBIServiceError("Power BI Report 메타데이터 조회에 실패했습니다.", 502, "PBI_REPORT_METADATA_FAILED");
	return data ?? null;
}
async function generateEmbedToken(reportId, datasetId) {
	if (!isPowerBIConfigured()) throw new PowerBIServiceError("Power BI 게시 환경 변수가 설정되지 않았습니다.", 503, "PBI_CONFIG_MISSING");
	const accessToken = await fetchPowerBIAccessToken();
	return jsonResponse(await powerBIFetch(powerBIUrl("GenerateToken"), {
		method: "POST",
		headers: {
			Authorization: `Bearer ${accessToken}`,
			"Content-Type": "application/json"
		},
		body: JSON.stringify({
			datasets: [{ id: datasetId }],
			reports: [{ id: reportId }]
		})
	}, "Power BI Embed Token 요청에 실패했습니다.", "PBI_EMBED_TOKEN_REQUEST_FAILED"), "Power BI Embed Token 발급에 실패했습니다.", "PBI_EMBED_TOKEN_FAILED");
}
async function postPbixImport(accessToken, file, datasetDisplayName) {
	const url = new URL(powerBIUrl(`groups/${encodeURIComponent(workspaceId())}/imports`));
	url.searchParams.set("datasetDisplayName", datasetDisplayName);
	url.searchParams.set("nameConflict", "Abort");
	const multipart = await pbixMultipartBody(file, datasetDisplayName);
	return jsonResponse(await powerBIFetch(url, {
		method: "POST",
		headers: {
			Authorization: `Bearer ${accessToken}`,
			"Content-Type": `multipart/form-data; boundary=${multipart.boundary}`
		},
		body: multipart.body
	}, "Power BI PBIX 업로드 요청에 실패했습니다.", "PBI_IMPORT_UPLOAD_REQUEST_FAILED"), "Power BI PBIX 업로드에 실패했습니다.", "PBI_IMPORT_UPLOAD_FAILED");
}
async function pollImportCompletion(accessToken, importId) {
	const pollSeconds = Math.max(Number(private_env.POWERBI_IMPORT_POLL_SECONDS ?? DEFAULT_IMPORT_POLL_SECONDS), 1);
	const deadline = Date.now() + pollSeconds * 1e3;
	let latestPayload = {};
	while (Date.now() <= deadline) {
		latestPayload = await getImport(accessToken, importId);
		const importStatus = normalizeImportStatus(latestPayload);
		if (IMPORT_SUCCEEDED_STATES.has(importStatus) || IMPORT_FAILED_STATES.has(importStatus)) return latestPayload;
		await sleep(1e3);
	}
	return latestPayload;
}
async function getImport(accessToken, importId) {
	return jsonResponse(await powerBIFetch(powerBIUrl(`groups/${encodeURIComponent(workspaceId())}/imports/${encodeURIComponent(importId)}`), { headers: { Authorization: `Bearer ${accessToken}` } }, "Power BI Import 상태 확인 요청에 실패했습니다.", "PBI_IMPORT_STATUS_REQUEST_FAILED"), "Power BI Import 상태 확인에 실패했습니다.", "PBI_IMPORT_STATUS_FAILED");
}
async function getReportMetadata(accessToken, reportId) {
	return jsonResponse(await powerBIFetch(powerBIUrl(`groups/${encodeURIComponent(workspaceId())}/reports/${encodeURIComponent(reportId)}`), { headers: { Authorization: `Bearer ${accessToken}` } }, "Power BI Report 메타데이터 요청에 실패했습니다.", "PBI_REPORT_METADATA_REQUEST_FAILED"), "Power BI Report 메타데이터 조회에 실패했습니다.", "PBI_REPORT_METADATA_FAILED");
}
async function upsertPowerBIReport(projectId, metadata) {
	const serviceClient = getSupabaseServerClient();
	if (!serviceClient) throw new PowerBIServiceError("Supabase 서버 환경 변수가 설정되지 않았습니다.", 503, "PBI_SUPABASE_CONFIG_MISSING");
	const { error } = await serviceClient.from("powerbi_reports").upsert({
		project_id: projectId,
		...metadata
	}, { onConflict: "project_id" });
	if (error) throw new PowerBIServiceError("Power BI Report 메타데이터 저장에 실패했습니다.", 502, "PBI_REPORT_METADATA_SAVE_FAILED");
}
async function markProjectPowerBIPublished(projectId, embedUrl) {
	await updateProjectPowerBIState(projectId, {
		project_type: "powerbi",
		status: "published",
		embed_status: embedUrl ? "supported" : "external_only",
		power_bi_url: embedUrl
	});
}
async function markProjectPowerBIProcessing(projectId, importId, importStatus, message) {
	await updateProjectPowerBIState(projectId, {
		project_type: "powerbi",
		status: "processing",
		embed_status: "external_only"
	});
	await upsertPowerBIReport(projectId, {
		workspace_id: private_env.POWERBI_WORKSPACE_ID,
		import_id: importId,
		import_status: importStatus,
		error_message: message.slice(0, 1e3)
	});
}
async function markProjectPowerBIFailed(projectId, importId, importStatus, message) {
	await updateProjectPowerBIState(projectId, {
		project_type: "powerbi",
		status: "failed",
		embed_status: "failed"
	});
	await upsertPowerBIReport(projectId, {
		workspace_id: private_env.POWERBI_WORKSPACE_ID,
		import_id: importId,
		import_status: importStatus,
		error_message: message.slice(0, 1e3)
	});
}
async function updateProjectPowerBIState(projectId, payload) {
	const serviceClient = getSupabaseServerClient();
	if (!serviceClient) throw new PowerBIServiceError("Supabase 서버 환경 변수가 설정되지 않았습니다.", 503, "PBI_SUPABASE_CONFIG_MISSING");
	const { error } = await serviceClient.from("projects").update(payload).eq("id", projectId);
	if (error) throw new PowerBIServiceError("프로젝트 Power BI 상태 업데이트에 실패했습니다.", 502, "PBI_PROJECT_STATE_SAVE_FAILED");
}
async function fetchPowerBIAccessToken() {
	const tenantId = private_env.POWERBI_TENANT_ID;
	const clientId = private_env.POWERBI_CLIENT_ID;
	const clientSecret = private_env.POWERBI_CLIENT_SECRET;
	if (!tenantId || !clientId || !clientSecret) throw new PowerBIServiceError("Power BI 게시 환경 변수가 설정되지 않았습니다.", 503, "PBI_CONFIG_MISSING");
	const payload = await jsonResponse(await powerBIFetch(`https://login.microsoftonline.com/${encodeURIComponent(tenantId)}/oauth2/v2.0/token`, {
		method: "POST",
		headers: { "Content-Type": "application/x-www-form-urlencoded" },
		body: new URLSearchParams({
			client_id: clientId,
			client_secret: clientSecret,
			grant_type: "client_credentials",
			scope: POWERBI_SCOPE
		})
	}, "Power BI Access Token 요청에 실패했습니다.", "PBI_TOKEN_FAILED"), "Power BI Access Token 발급에 실패했습니다.", "PBI_TOKEN_FAILED");
	if (!payload.access_token) throw new PowerBIServiceError("Power BI Access Token 응답을 확인할 수 없습니다.", 502, "PBI_TOKEN_EMPTY");
	return payload.access_token;
}
async function jsonResponse(response, message, code) {
	let payload = null;
	let rawText = "";
	try {
		rawText = await response.text();
		payload = rawText ? JSON.parse(rawText) : null;
	} catch {
		payload = null;
	}
	if (!response.ok) {
		const upstream = powerBIErrorDetails(payload, rawText);
		const detail = upstream.message ? ` (${upstream.message})` : "";
		const status = response.status >= 500 ? 502 : response.status;
		throw new PowerBIServiceError(`${message}${detail}`, status, code, response.status, upstream.code);
	}
	return payload;
}
async function powerBIFetch(input, init, message, code) {
	try {
		return await fetch(input, init);
	} catch (error) {
		throw new PowerBIServiceError(`${message}${error instanceof Error ? ` (${sanitizePowerBIMessage(error.message)})` : ""}`, 502, code);
	}
}
function powerBIUrl(path) {
	return `${(private_env.POWERBI_API_BASE_URL || DEFAULT_POWERBI_API_BASE_URL).replace(/\/$/, "")}/${path.replace(/^\//, "")}`;
}
function validatePbixUpload(file, originalFilename) {
	const maxUploadMb = Math.max(Number(private_env.PBIX_MAX_UPLOAD_MB ?? DEFAULT_PBIX_MAX_UPLOAD_MB), 1);
	if (!originalFilename.toLowerCase().endsWith(".pbix")) throw new PowerBIServiceError("PBIX 파일만 업로드할 수 있습니다.", 400, "PBI_FILE_INVALID");
	if (file.size <= 0) throw new PowerBIServiceError("PBIX 파일이 비어 있습니다.", 400, "PBI_FILE_EMPTY");
	if (file.size > maxUploadMb * 1024 * 1024) throw new PowerBIServiceError(`PBIX 파일은 최대 ${maxUploadMb}MB까지 업로드할 수 있습니다.`, 400, "PBI_FILE_TOO_LARGE");
}
function datasetDisplayName(projectId, originalFilename) {
	const safeName = originalFilename.replace(/[^a-zA-Z0-9_.-]/g, "_");
	return `${projectId}_${Date.now()}_${safeName}`.slice(0, 120);
}
async function pbixMultipartBody(file, filename) {
	const boundary = `----folio-pbix-${crypto.randomUUID().replaceAll("-", "")}`;
	const encoder = new TextEncoder();
	const header = encoder.encode([
		`--${boundary}`,
		`Content-Disposition: form-data; name="file"; filename="${safeMultipartFilename(filename)}"`,
		"Content-Type: application/octet-stream",
		"",
		""
	].join("\r\n"));
	const fileBytes = new Uint8Array(await file.arrayBuffer());
	const footer = encoder.encode(`\r\n--${boundary}--\r\n`);
	const body = new Uint8Array(header.length + fileBytes.length + footer.length);
	body.set(header, 0);
	body.set(fileBytes, header.length);
	body.set(footer, header.length + fileBytes.length);
	return {
		boundary,
		body
	};
}
function safeMultipartFilename(value) {
	return value.replace(/[\r\n"]/g, "_");
}
function workspaceId() {
	const value = private_env.POWERBI_WORKSPACE_ID?.trim();
	if (!value) throw new PowerBIServiceError("Power BI Workspace 환경 변수가 설정되지 않았습니다.", 503, "PBI_WORKSPACE_MISSING");
	return value;
}
function normalizeImportStatus(payload) {
	return String(payload.importState || payload.state || "").toLowerCase();
}
function firstReportFromImport(payload) {
	const report = payload.reports?.[0];
	if (!report) throw new PowerBIServiceError("Power BI Import 결과를 확인할 수 없습니다.", 502, "PBI_IMPORT_RESULT_INVALID");
	return report;
}
function emptyImportResult(ok, message, errorCode, projectId, importId, importStatus) {
	return {
		ok,
		message,
		error_code: errorCode,
		projectId,
		importId,
		importStatus,
		reportId: null,
		datasetId: null,
		embedUrl: null
	};
}
function sleep(milliseconds) {
	return new Promise((resolve) => setTimeout(resolve, milliseconds));
}
function powerBIErrorDetails(payload, rawText) {
	if (payload && typeof payload === "object") {
		const record = payload;
		const nested = record.error && typeof record.error === "object" ? record.error : null;
		return {
			code: sanitizePowerBIMessage(String(nested?.code || record.code || "")) || null,
			message: sanitizePowerBIMessage(String(nested?.message || record.message || record.error_description || "")) || null
		};
	}
	return {
		code: null,
		message: sanitizePowerBIMessage(rawText) || null
	};
}
function sanitizePowerBIMessage(value) {
	return value.replace(/\s+/g, " ").trim().slice(0, 240);
}
//#endregion
export { getPowerBIEmbedConfig as n, publishPbixForProject as r, PowerBIServiceError as t };
