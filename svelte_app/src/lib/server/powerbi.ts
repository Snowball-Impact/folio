import { env } from '$env/dynamic/private';
import { getSupabaseServerClient } from '$lib/server/supabase';
import { getSupabaseClient } from '$lib/supabase';
import type { PowerBIEmbedConfig } from '$lib/types';

const POWERBI_SCOPE = 'https://analysis.windows.net/powerbi/api/.default';
const DEFAULT_POWERBI_API_BASE_URL = 'https://api.powerbi.com/v1.0/myorg';
const DEFAULT_PBIX_MAX_UPLOAD_MB = 50;
const DEFAULT_IMPORT_POLL_SECONDS = 100;
const IMPORT_SUCCEEDED_STATES = new Set(['succeeded', 'completed']);
const IMPORT_FAILED_STATES = new Set(['failed']);

type PowerBIReportRecord = {
	report_id: string | null;
	dataset_id: string | null;
	embed_url: string | null;
};

type TokenPayload = {
	token?: string;
	expiration?: string;
};

type PowerBIImportPayload = {
	id?: string;
	importState?: string;
	state?: string;
	reports?: Array<{
		id?: string;
		datasetId?: string;
		embedUrl?: string;
		webUrl?: string;
	}>;
	datasets?: Array<{
		id?: string;
	}>;
};

type PowerBIReportMetadata = {
	id?: string;
	datasetId?: string;
	embedUrl?: string;
	webUrl?: string;
};

type PowerBIImportResult = {
	ok: boolean;
	message: string;
	error_code?: PowerBIErrorCode;
	projectId: string;
	importId: string | null;
	importStatus: string | null;
	reportId: string | null;
	datasetId: string | null;
	embedUrl: string | null;
};

type PowerBIErrorCode =
	| 'PBI_CONFIG_MISSING'
	| 'PBI_SUPABASE_CONFIG_MISSING'
	| 'PBI_FILE_INVALID'
	| 'PBI_FILE_EMPTY'
	| 'PBI_FILE_TOO_LARGE'
	| 'PBI_TOKEN_FAILED'
	| 'PBI_TOKEN_EMPTY'
	| 'PBI_IMPORT_UPLOAD_FAILED'
	| 'PBI_IMPORT_UPLOAD_REQUEST_FAILED'
	| 'PBI_IMPORT_RESPONSE_INVALID'
	| 'PBI_IMPORT_STATUS_FAILED'
	| 'PBI_IMPORT_STATUS_REQUEST_FAILED'
	| 'PBI_IMPORT_INCOMPLETE'
	| 'PBI_IMPORT_RESULT_INVALID'
	| 'PBI_REPORT_ID_MISSING'
	| 'PBI_EMBED_TOKEN_FAILED'
	| 'PBI_EMBED_TOKEN_REQUEST_FAILED'
	| 'PBI_EMBED_TOKEN_EMPTY'
	| 'PBI_REPORT_METADATA_FAILED'
	| 'PBI_REPORT_METADATA_REQUEST_FAILED'
	| 'PBI_REPORT_METADATA_SAVE_FAILED'
	| 'PBI_PROJECT_STATE_SAVE_FAILED'
	| 'PBI_WORKSPACE_MISSING';

export class PowerBIServiceError extends Error {
	constructor(
		message: string,
		readonly status = 500,
		readonly code: PowerBIErrorCode = 'PBI_IMPORT_UPLOAD_FAILED',
		readonly upstreamStatus: number | null = null,
		readonly upstreamCode: string | null = null
	) {
		super(message);
		this.name = 'PowerBIServiceError';
	}
}

export function isPowerBIConfigured() {
	return Boolean(env.POWERBI_TENANT_ID && env.POWERBI_CLIENT_ID && env.POWERBI_CLIENT_SECRET && env.POWERBI_WORKSPACE_ID);
}

export async function publishPbixForProject(
	projectId: string,
	file: File,
	originalFilename = file.name
): Promise<PowerBIImportResult> {
	validatePbixUpload(file, originalFilename);
	if (!isPowerBIConfigured()) {
		throw new PowerBIServiceError('Power BI 게시 환경 변수가 설정되지 않았습니다.', 503, 'PBI_CONFIG_MISSING');
	}

	const serviceClient = getSupabaseServerClient();
	if (!serviceClient) {
		throw new PowerBIServiceError('Supabase 서버 환경 변수가 설정되지 않았습니다.', 503, 'PBI_SUPABASE_CONFIG_MISSING');
	}

	const accessToken = await fetchPowerBIAccessToken();
	const importPayload = await postPbixImport(accessToken, file, datasetDisplayName(projectId, originalFilename));
	const importId = importPayload.id?.trim();
	if (!importId) {
		throw new PowerBIServiceError('Power BI Import 응답을 확인할 수 없습니다.', 502, 'PBI_IMPORT_RESPONSE_INVALID');
	}

	await markProjectPowerBIProcessing(projectId, importId, 'publishing', 'Power BI Import를 시작했습니다.');
	const importState = await pollImportCompletion(accessToken, importId);
	const importStatus = normalizeImportStatus(importState);
	if (!IMPORT_SUCCEEDED_STATES.has(importStatus)) {
		const message = IMPORT_FAILED_STATES.has(importStatus)
			? 'Power BI 게시에 실패했습니다. PBIX 파일과 Workspace 권한을 확인하세요.'
			: 'Power BI 게시가 아직 완료되지 않았습니다. 잠시 후 다시 확인하세요.';
		if (IMPORT_FAILED_STATES.has(importStatus)) {
			await markProjectPowerBIFailed(projectId, importId, importStatus, message);
		} else {
			await markProjectPowerBIProcessing(projectId, importId, importStatus || 'processing', message);
		}
		return emptyImportResult(
			false,
			message,
			IMPORT_FAILED_STATES.has(importStatus) ? 'PBI_IMPORT_STATUS_FAILED' : 'PBI_IMPORT_INCOMPLETE',
			projectId,
			importId,
			importStatus || 'processing'
		);
	}

	const report = firstReportFromImport(importState);
	const reportId = report.id?.trim();
	if (!reportId) {
		throw new PowerBIServiceError('Power BI Report ID를 확인할 수 없습니다.', 502, 'PBI_REPORT_ID_MISSING');
	}

	const reportMetadata = await getReportMetadata(accessToken, reportId);
	const datasetId = reportMetadata.datasetId || report.datasetId || null;
	const embedUrl = reportMetadata.embedUrl || report.embedUrl || null;
	await upsertPowerBIReport(projectId, {
		workspace_id: env.POWERBI_WORKSPACE_ID,
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
		message: 'Power BI 보고서가 게시되었습니다.',
		projectId,
		importId,
		importStatus,
		reportId,
		datasetId,
		embedUrl
	};
}

export async function getPowerBIEmbedConfig(projectId: string): Promise<PowerBIEmbedConfig | null> {
	const report = await getPowerBIReportForProject(projectId);
	if (!report) {
		return null;
	}

	const reportId = report.report_id?.trim();
	const datasetId = report.dataset_id?.trim();
	const embedUrl = report.embed_url?.trim();
	if (!reportId || !datasetId || !embedUrl) {
		return null;
	}

	const tokenPayload = await generateEmbedToken(reportId, datasetId);
	const embedToken = tokenPayload.token;
	if (!embedToken) {
		throw new PowerBIServiceError('Power BI Embed Token 응답을 확인할 수 없습니다.', 502, 'PBI_EMBED_TOKEN_EMPTY');
	}

	return {
		report_id: reportId,
		dataset_id: datasetId,
		embed_url: embedUrl,
		embed_token: embedToken,
		token_expiration: tokenPayload.expiration ?? null
	};
}

async function getPowerBIReportForProject(projectId: string): Promise<PowerBIReportRecord | null> {
	const supabase = getSupabaseClient();
	if (!supabase) {
		throw new PowerBIServiceError('Supabase 환경 변수가 설정되지 않았습니다.', 503, 'PBI_SUPABASE_CONFIG_MISSING');
	}

	const { data, error } = await supabase
		.from('powerbi_reports')
		.select('report_id,dataset_id,embed_url')
		.eq('project_id', projectId)
		.maybeSingle();

	if (error) {
		throw new PowerBIServiceError('Power BI Report 메타데이터 조회에 실패했습니다.', 502, 'PBI_REPORT_METADATA_FAILED');
	}

	return (data as PowerBIReportRecord | null) ?? null;
}

async function generateEmbedToken(reportId: string, datasetId: string): Promise<TokenPayload> {
	if (!isPowerBIConfigured()) {
		throw new PowerBIServiceError('Power BI 게시 환경 변수가 설정되지 않았습니다.', 503, 'PBI_CONFIG_MISSING');
	}

	const accessToken = await fetchPowerBIAccessToken();
	const response = await powerBIFetch(
		powerBIUrl('GenerateToken'),
		{
			method: 'POST',
			headers: {
				Authorization: `Bearer ${accessToken}`,
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				datasets: [{ id: datasetId }],
				reports: [{ id: reportId }]
			})
		},
		'Power BI Embed Token 요청에 실패했습니다.',
		'PBI_EMBED_TOKEN_REQUEST_FAILED'
	);

	return jsonResponse<TokenPayload>(response, 'Power BI Embed Token 발급에 실패했습니다.', 'PBI_EMBED_TOKEN_FAILED');
}

async function postPbixImport(accessToken: string, file: File, datasetDisplayName: string): Promise<PowerBIImportPayload> {
	const url = new URL(powerBIUrl(`groups/${encodeURIComponent(workspaceId())}/imports`));
	url.searchParams.set('datasetDisplayName', datasetDisplayName);
	url.searchParams.set('nameConflict', 'Abort');
	const multipart = await pbixMultipartBody(file, datasetDisplayName);
	const response = await powerBIFetch(
		url,
		{
			method: 'POST',
			headers: {
				Authorization: `Bearer ${accessToken}`,
				'Content-Type': `multipart/form-data; boundary=${multipart.boundary}`
			},
			body: multipart.body
		},
		'Power BI PBIX 업로드 요청에 실패했습니다.',
		'PBI_IMPORT_UPLOAD_REQUEST_FAILED'
	);

	return jsonResponse<PowerBIImportPayload>(response, 'Power BI PBIX 업로드에 실패했습니다.', 'PBI_IMPORT_UPLOAD_FAILED');
}

async function pollImportCompletion(accessToken: string, importId: string): Promise<PowerBIImportPayload> {
	const pollSeconds = Math.max(Number(env.POWERBI_IMPORT_POLL_SECONDS ?? DEFAULT_IMPORT_POLL_SECONDS), 1);
	const deadline = Date.now() + pollSeconds * 1000;
	let latestPayload: PowerBIImportPayload = {};

	while (Date.now() <= deadline) {
		latestPayload = await getImport(accessToken, importId);
		const importStatus = normalizeImportStatus(latestPayload);
		if (IMPORT_SUCCEEDED_STATES.has(importStatus) || IMPORT_FAILED_STATES.has(importStatus)) {
			return latestPayload;
		}
		await sleep(1000);
	}

	return latestPayload;
}

async function getImport(accessToken: string, importId: string): Promise<PowerBIImportPayload> {
	const response = await powerBIFetch(
		powerBIUrl(`groups/${encodeURIComponent(workspaceId())}/imports/${encodeURIComponent(importId)}`),
		{
			headers: {
				Authorization: `Bearer ${accessToken}`
			}
		},
		'Power BI Import 상태 확인 요청에 실패했습니다.',
		'PBI_IMPORT_STATUS_REQUEST_FAILED'
	);
	return jsonResponse<PowerBIImportPayload>(response, 'Power BI Import 상태 확인에 실패했습니다.', 'PBI_IMPORT_STATUS_FAILED');
}

async function getReportMetadata(accessToken: string, reportId: string): Promise<PowerBIReportMetadata> {
	const response = await powerBIFetch(
		powerBIUrl(`groups/${encodeURIComponent(workspaceId())}/reports/${encodeURIComponent(reportId)}`),
		{
			headers: {
				Authorization: `Bearer ${accessToken}`
			}
		},
		'Power BI Report 메타데이터 요청에 실패했습니다.',
		'PBI_REPORT_METADATA_REQUEST_FAILED'
	);
	return jsonResponse<PowerBIReportMetadata>(response, 'Power BI Report 메타데이터 조회에 실패했습니다.', 'PBI_REPORT_METADATA_FAILED');
}

async function upsertPowerBIReport(projectId: string, metadata: Record<string, string | null | undefined>) {
	const serviceClient = getSupabaseServerClient();
	if (!serviceClient) {
		throw new PowerBIServiceError('Supabase 서버 환경 변수가 설정되지 않았습니다.', 503, 'PBI_SUPABASE_CONFIG_MISSING');
	}
	const { error } = await serviceClient.from('powerbi_reports').upsert({ project_id: projectId, ...metadata }, { onConflict: 'project_id' });
	if (error) {
		throw new PowerBIServiceError('Power BI Report 메타데이터 저장에 실패했습니다.', 502, 'PBI_REPORT_METADATA_SAVE_FAILED');
	}
}

async function markProjectPowerBIPublished(projectId: string, embedUrl: string | null) {
	await updateProjectPowerBIState(projectId, {
		project_type: 'powerbi',
		status: 'published',
		embed_status: embedUrl ? 'supported' : 'external_only',
		power_bi_url: embedUrl
	});
}

async function markProjectPowerBIProcessing(projectId: string, importId: string, importStatus: string, message: string) {
	await updateProjectPowerBIState(projectId, {
		project_type: 'powerbi',
		status: 'processing',
		embed_status: 'external_only'
	});
	await upsertPowerBIReport(projectId, {
		workspace_id: env.POWERBI_WORKSPACE_ID,
		import_id: importId,
		import_status: importStatus,
		error_message: message.slice(0, 1000)
	});
}

async function markProjectPowerBIFailed(projectId: string, importId: string, importStatus: string, message: string) {
	await updateProjectPowerBIState(projectId, {
		project_type: 'powerbi',
		status: 'failed',
		embed_status: 'failed'
	});
	await upsertPowerBIReport(projectId, {
		workspace_id: env.POWERBI_WORKSPACE_ID,
		import_id: importId,
		import_status: importStatus,
		error_message: message.slice(0, 1000)
	});
}

async function updateProjectPowerBIState(projectId: string, payload: Record<string, string | null>) {
	const serviceClient = getSupabaseServerClient();
	if (!serviceClient) {
		throw new PowerBIServiceError('Supabase 서버 환경 변수가 설정되지 않았습니다.', 503, 'PBI_SUPABASE_CONFIG_MISSING');
	}
	const { error } = await serviceClient.from('projects').update(payload).eq('id', projectId);
	if (error) {
		throw new PowerBIServiceError('프로젝트 Power BI 상태 업데이트에 실패했습니다.', 502, 'PBI_PROJECT_STATE_SAVE_FAILED');
	}
}

async function fetchPowerBIAccessToken() {
	const tenantId = env.POWERBI_TENANT_ID;
	const clientId = env.POWERBI_CLIENT_ID;
	const clientSecret = env.POWERBI_CLIENT_SECRET;
	if (!tenantId || !clientId || !clientSecret) {
		throw new PowerBIServiceError('Power BI 게시 환경 변수가 설정되지 않았습니다.', 503, 'PBI_CONFIG_MISSING');
	}

	const response = await powerBIFetch(
		`https://login.microsoftonline.com/${encodeURIComponent(tenantId)}/oauth2/v2.0/token`,
		{
			method: 'POST',
			headers: {
				'Content-Type': 'application/x-www-form-urlencoded'
			},
			body: new URLSearchParams({
				client_id: clientId,
				client_secret: clientSecret,
				grant_type: 'client_credentials',
				scope: POWERBI_SCOPE
			})
		},
		'Power BI Access Token 요청에 실패했습니다.',
		'PBI_TOKEN_FAILED'
	);
	const payload = await jsonResponse<{ access_token?: string }>(
		response,
		'Power BI Access Token 발급에 실패했습니다.',
		'PBI_TOKEN_FAILED'
	);
	if (!payload.access_token) {
		throw new PowerBIServiceError('Power BI Access Token 응답을 확인할 수 없습니다.', 502, 'PBI_TOKEN_EMPTY');
	}
	return payload.access_token;
}

async function jsonResponse<T>(response: Response, message: string, code: PowerBIErrorCode): Promise<T> {
	let payload: unknown = null;
	let rawText = '';
	try {
		rawText = await response.text();
		payload = rawText ? JSON.parse(rawText) : null;
	} catch {
		payload = null;
	}

	if (!response.ok) {
		const upstream = powerBIErrorDetails(payload, rawText);
		const detail = upstream.message ? ` (${upstream.message})` : '';
		const status = response.status >= 500 ? 502 : response.status;
		throw new PowerBIServiceError(`${message}${detail}`, status, code, response.status, upstream.code);
	}

	return payload as T;
}

async function powerBIFetch(
	input: string | URL,
	init: RequestInit,
	message: string,
	code: PowerBIErrorCode
) {
	try {
		return await fetch(input, init);
	} catch (error) {
		const detail = error instanceof Error ? ` (${sanitizePowerBIMessage(error.message)})` : '';
		throw new PowerBIServiceError(`${message}${detail}`, 502, code);
	}
}

function powerBIUrl(path: string) {
	const baseUrl = env.POWERBI_API_BASE_URL || DEFAULT_POWERBI_API_BASE_URL;
	return `${baseUrl.replace(/\/$/, '')}/${path.replace(/^\//, '')}`;
}

function validatePbixUpload(file: File, originalFilename: string) {
	const maxUploadMb = Math.max(Number(env.PBIX_MAX_UPLOAD_MB ?? DEFAULT_PBIX_MAX_UPLOAD_MB), 1);
	if (!originalFilename.toLowerCase().endsWith('.pbix')) {
		throw new PowerBIServiceError('PBIX 파일만 업로드할 수 있습니다.', 400, 'PBI_FILE_INVALID');
	}
	if (file.size <= 0) {
		throw new PowerBIServiceError('PBIX 파일이 비어 있습니다.', 400, 'PBI_FILE_EMPTY');
	}
	if (file.size > maxUploadMb * 1024 * 1024) {
		throw new PowerBIServiceError(`PBIX 파일은 최대 ${maxUploadMb}MB까지 업로드할 수 있습니다.`, 400, 'PBI_FILE_TOO_LARGE');
	}
}

function datasetDisplayName(projectId: string, originalFilename: string) {
	const safeName = originalFilename.replace(/[^a-zA-Z0-9_.-]/g, '_');
	return `${projectId}_${Date.now()}_${safeName}`.slice(0, 120);
}

async function pbixMultipartBody(file: File, filename: string) {
	const boundary = `----folio-pbix-${crypto.randomUUID().replaceAll('-', '')}`;
	const encoder = new TextEncoder();
	const header = encoder.encode(
		[
			`--${boundary}`,
			`Content-Disposition: form-data; name="file"; filename="${safeMultipartFilename(filename)}"`,
			'Content-Type: application/octet-stream',
			'',
			''
		].join('\r\n')
	);
	const fileBytes = new Uint8Array(await file.arrayBuffer());
	const footer = encoder.encode(`\r\n--${boundary}--\r\n`);
	const body = new Uint8Array(header.length + fileBytes.length + footer.length);
	body.set(header, 0);
	body.set(fileBytes, header.length);
	body.set(footer, header.length + fileBytes.length);
	return { boundary, body };
}

function safeMultipartFilename(value: string) {
	return value.replace(/[\r\n"]/g, '_');
}

function workspaceId() {
	const value = env.POWERBI_WORKSPACE_ID?.trim();
	if (!value) {
		throw new PowerBIServiceError('Power BI Workspace 환경 변수가 설정되지 않았습니다.', 503, 'PBI_WORKSPACE_MISSING');
	}
	return value;
}

function normalizeImportStatus(payload: PowerBIImportPayload) {
	return String(payload.importState || payload.state || '').toLowerCase();
}

function firstReportFromImport(payload: PowerBIImportPayload) {
	const report = payload.reports?.[0];
	if (!report) {
		throw new PowerBIServiceError('Power BI Import 결과를 확인할 수 없습니다.', 502, 'PBI_IMPORT_RESULT_INVALID');
	}
	return report;
}

function emptyImportResult(
	ok: boolean,
	message: string,
	errorCode: PowerBIErrorCode,
	projectId: string,
	importId: string | null,
	importStatus: string | null
) {
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

function sleep(milliseconds: number) {
	return new Promise((resolve) => setTimeout(resolve, milliseconds));
}

function powerBIErrorDetails(payload: unknown, rawText: string) {
	if (payload && typeof payload === 'object') {
		const record = payload as Record<string, unknown>;
		const nested = record.error && typeof record.error === 'object' ? (record.error as Record<string, unknown>) : null;
		const code = sanitizePowerBIMessage(String(nested?.code || record.code || '')) || null;
		const message = sanitizePowerBIMessage(String(nested?.message || record.message || record.error_description || '')) || null;
		return { code, message };
	}
	return { code: null, message: sanitizePowerBIMessage(rawText) || null };
}

function sanitizePowerBIMessage(value: string) {
	return value.replace(/\s+/g, ' ').trim().slice(0, 240);
}
