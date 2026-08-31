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
	projectId: string;
	importId: string | null;
	importStatus: string | null;
	reportId: string | null;
	datasetId: string | null;
	embedUrl: string | null;
};

export class PowerBIServiceError extends Error {
	constructor(
		message: string,
		readonly status = 500
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
		throw new PowerBIServiceError('Power BI 게시 환경 변수가 설정되지 않았습니다.', 503);
	}

	const serviceClient = getSupabaseServerClient();
	if (!serviceClient) {
		throw new PowerBIServiceError('Supabase 서버 환경 변수가 설정되지 않았습니다.', 503);
	}

	const accessToken = await fetchPowerBIAccessToken();
	const importPayload = await postPbixImport(accessToken, file, datasetDisplayName(projectId, originalFilename));
	const importId = importPayload.id?.trim();
	if (!importId) {
		throw new PowerBIServiceError('Power BI Import 응답을 확인할 수 없습니다.', 502);
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
		return emptyImportResult(false, message, projectId, importId, importStatus || 'processing');
	}

	const report = firstReportFromImport(importState);
	const reportId = report.id?.trim();
	if (!reportId) {
		throw new PowerBIServiceError('Power BI Report ID를 확인할 수 없습니다.', 502);
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
		throw new PowerBIServiceError('Power BI Embed Token 응답을 확인할 수 없습니다.', 502);
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
		throw new PowerBIServiceError('Supabase 환경 변수가 설정되지 않았습니다.', 503);
	}

	const { data, error } = await supabase
		.from('powerbi_reports')
		.select('report_id,dataset_id,embed_url')
		.eq('project_id', projectId)
		.maybeSingle();

	if (error) {
		throw new PowerBIServiceError('Power BI Report 메타데이터 조회에 실패했습니다.', 502);
	}

	return (data as PowerBIReportRecord | null) ?? null;
}

async function generateEmbedToken(reportId: string, datasetId: string): Promise<TokenPayload> {
	if (!isPowerBIConfigured()) {
		throw new PowerBIServiceError('Power BI 게시 환경 변수가 설정되지 않았습니다.', 503);
	}

	const accessToken = await fetchPowerBIAccessToken();
	const response = await fetch(powerBIUrl('GenerateToken'), {
		method: 'POST',
		headers: {
			Authorization: `Bearer ${accessToken}`,
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({
			datasets: [{ id: datasetId }],
			reports: [{ id: reportId }]
		})
	});

	return jsonResponse<TokenPayload>(response, 'Power BI Embed Token 발급에 실패했습니다.');
}

async function postPbixImport(accessToken: string, file: File, datasetDisplayName: string): Promise<PowerBIImportPayload> {
	const formData = new FormData();
	formData.set('file', file, datasetDisplayName);
	const url = new URL(powerBIUrl(`groups/${encodeURIComponent(workspaceId())}/imports`));
	url.searchParams.set('datasetDisplayName', datasetDisplayName);
	url.searchParams.set('nameConflict', 'Abort');
	const response = await fetch(url, {
		method: 'POST',
		headers: {
			Authorization: `Bearer ${accessToken}`
		},
		body: formData,
		duplex: 'half'
	} as RequestInit);

	return jsonResponse<PowerBIImportPayload>(response, 'Power BI PBIX 업로드에 실패했습니다.');
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
	const response = await fetch(powerBIUrl(`groups/${encodeURIComponent(workspaceId())}/imports/${encodeURIComponent(importId)}`), {
		headers: {
			Authorization: `Bearer ${accessToken}`
		}
	});
	return jsonResponse<PowerBIImportPayload>(response, 'Power BI Import 상태 확인에 실패했습니다.');
}

async function getReportMetadata(accessToken: string, reportId: string): Promise<PowerBIReportMetadata> {
	const response = await fetch(powerBIUrl(`groups/${encodeURIComponent(workspaceId())}/reports/${encodeURIComponent(reportId)}`), {
		headers: {
			Authorization: `Bearer ${accessToken}`
		}
	});
	return jsonResponse<PowerBIReportMetadata>(response, 'Power BI Report 메타데이터 조회에 실패했습니다.');
}

async function upsertPowerBIReport(projectId: string, metadata: Record<string, string | null | undefined>) {
	const serviceClient = getSupabaseServerClient();
	if (!serviceClient) {
		throw new PowerBIServiceError('Supabase 서버 환경 변수가 설정되지 않았습니다.', 503);
	}
	const { error } = await serviceClient.from('powerbi_reports').upsert({ project_id: projectId, ...metadata }, { onConflict: 'project_id' });
	if (error) {
		throw new PowerBIServiceError('Power BI Report 메타데이터 저장에 실패했습니다.', 502);
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
		throw new PowerBIServiceError('Supabase 서버 환경 변수가 설정되지 않았습니다.', 503);
	}
	const { error } = await serviceClient.from('projects').update(payload).eq('id', projectId);
	if (error) {
		throw new PowerBIServiceError('프로젝트 Power BI 상태 업데이트에 실패했습니다.', 502);
	}
}

async function fetchPowerBIAccessToken() {
	const tenantId = env.POWERBI_TENANT_ID;
	const clientId = env.POWERBI_CLIENT_ID;
	const clientSecret = env.POWERBI_CLIENT_SECRET;
	if (!tenantId || !clientId || !clientSecret) {
		throw new PowerBIServiceError('Power BI 게시 환경 변수가 설정되지 않았습니다.', 503);
	}

	const response = await fetch(
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
		}
	);
	const payload = await jsonResponse<{ access_token?: string }>(
		response,
		'Power BI Access Token 발급에 실패했습니다.'
	);
	if (!payload.access_token) {
		throw new PowerBIServiceError('Power BI Access Token 응답을 확인할 수 없습니다.', 502);
	}
	return payload.access_token;
}

async function jsonResponse<T>(response: Response, message: string): Promise<T> {
	let payload: unknown = null;
	try {
		payload = await response.json();
	} catch {
		payload = null;
	}

	if (!response.ok) {
		throw new PowerBIServiceError(message, 502);
	}

	return payload as T;
}

function powerBIUrl(path: string) {
	const baseUrl = env.POWERBI_API_BASE_URL || DEFAULT_POWERBI_API_BASE_URL;
	return `${baseUrl.replace(/\/$/, '')}/${path.replace(/^\//, '')}`;
}

function validatePbixUpload(file: File, originalFilename: string) {
	const maxUploadMb = Math.max(Number(env.PBIX_MAX_UPLOAD_MB ?? DEFAULT_PBIX_MAX_UPLOAD_MB), 1);
	if (!originalFilename.toLowerCase().endsWith('.pbix')) {
		throw new PowerBIServiceError('PBIX 파일만 업로드할 수 있습니다.', 400);
	}
	if (file.size <= 0) {
		throw new PowerBIServiceError('PBIX 파일이 비어 있습니다.', 400);
	}
	if (file.size > maxUploadMb * 1024 * 1024) {
		throw new PowerBIServiceError(`PBIX 파일은 최대 ${maxUploadMb}MB까지 업로드할 수 있습니다.`, 400);
	}
}

function datasetDisplayName(projectId: string, originalFilename: string) {
	const safeName = originalFilename.replace(/[^a-zA-Z0-9_.-]/g, '_');
	return `${projectId}_${Date.now()}_${safeName}`.slice(0, 120);
}

function workspaceId() {
	const value = env.POWERBI_WORKSPACE_ID?.trim();
	if (!value) {
		throw new PowerBIServiceError('Power BI Workspace 환경 변수가 설정되지 않았습니다.', 503);
	}
	return value;
}

function normalizeImportStatus(payload: PowerBIImportPayload) {
	return String(payload.importState || payload.state || '').toLowerCase();
}

function firstReportFromImport(payload: PowerBIImportPayload) {
	const report = payload.reports?.[0];
	if (!report) {
		throw new PowerBIServiceError('Power BI Import 결과를 확인할 수 없습니다.', 502);
	}
	return report;
}

function emptyImportResult(ok: boolean, message: string, projectId: string, importId: string | null, importStatus: string | null) {
	return {
		ok,
		message,
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
