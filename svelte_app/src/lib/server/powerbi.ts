import { env } from '$env/dynamic/private';
import { getSupabaseClient } from '$lib/supabase';
import type { PowerBIEmbedConfig } from '$lib/types';

const POWERBI_SCOPE = 'https://analysis.windows.net/powerbi/api/.default';
const DEFAULT_POWERBI_API_BASE_URL = 'https://api.powerbi.com/v1.0/myorg';

type PowerBIReportRecord = {
	report_id: string | null;
	dataset_id: string | null;
	embed_url: string | null;
};

type TokenPayload = {
	token?: string;
	expiration?: string;
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
	return Boolean(env.POWERBI_TENANT_ID && env.POWERBI_CLIENT_ID && env.POWERBI_CLIENT_SECRET);
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
