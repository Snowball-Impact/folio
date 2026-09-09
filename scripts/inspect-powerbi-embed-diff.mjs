import { existsSync, readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { createClient } from '@supabase/supabase-js';

function loadDotEnv(path) {
	if (!existsSync(path)) {
		return;
	}
	for (const line of readFileSync(path, 'utf8').split(/\r?\n/)) {
		const match = line.match(/^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)\s*$/);
		if (!match || process.env[match[1]]) {
			continue;
		}
		let value = match[2].trim();
		if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith("'") && value.endsWith("'"))) {
			value = value.slice(1, -1);
		}
		process.env[match[1]] = value;
	}
}

function safeUrl(value) {
	if (!value) {
		return null;
	}
	const raw = String(value);
	const src = raw.match(/src=["']([^"']+)/i)?.[1] ?? raw;
	try {
		const url = new URL(src);
		return {
			host: url.host,
			path: url.pathname,
			params: [...url.searchParams.keys()].sort(),
			hasReportId: url.searchParams.has('reportId') || url.pathname.includes('/reports/'),
			hasGroupId: url.searchParams.has('groupId') || url.pathname.includes('/groups/'),
			hasConfig: url.searchParams.has('config'),
			hasPageName: url.searchParams.has('pageName'),
			length: src.length
		};
	} catch {
		return { rawStart: src.slice(0, 80), length: src.length };
	}
}

loadDotEnv(resolve(process.cwd(), '.env'));
loadDotEnv(resolve(process.cwd(), '..', '.env'));

const supabaseUrl = process.env.PUBLIC_SUPABASE_URL ?? process.env.SUPABASE_URL;
const publishableKey =
	process.env.PUBLIC_SUPABASE_PUBLISHABLE_KEY ??
	process.env.SUPABASE_PUBLISHABLE_KEY ??
	process.env.SUPABASE_ANON_KEY;

if (!supabaseUrl || !publishableKey) {
	throw new Error('Supabase env is missing.');
}

const supabase = createClient(supabaseUrl, publishableKey, {
	auth: { persistSession: false, autoRefreshToken: false }
});

const { data: reportRows, error: allReportsError } = await supabase
	.from('powerbi_reports')
	.select('project_id,workspace_id,report_id,dataset_id,embed_url,web_url,import_status,error_message,created_at,updated_at')
	.order('created_at', { ascending: false })
	.limit(50);

if (allReportsError) {
	throw new Error(allReportsError.message);
}

const reportBackedProjectIds = [...new Set((reportRows ?? []).map((report) => report.project_id))];

const { data: visibleProjects, error } = await supabase
	.from('projects')
	.select('id,title,created_at,project_type,platform_key,status,embed_status,power_bi_url,report_url,github_url')
	.eq('status', 'published')
	.eq('is_public', true)
	.or('project_type.eq.powerbi,platform_key.eq.powerbi,embed_status.eq.supported,power_bi_url.ilike.%powerbi%')
	.order('created_at', { ascending: false })
	.limit(30);

if (error) {
	throw new Error(error.message);
}

const { data: reportBackedProjects, error: reportBackedProjectsError } = reportBackedProjectIds.length
	? await supabase
			.from('projects')
			.select('id,title,created_at,project_type,platform_key,status,embed_status,power_bi_url,report_url,github_url')
			.in('id', reportBackedProjectIds)
	: { data: [], error: null };

if (reportBackedProjectsError) {
	throw new Error(reportBackedProjectsError.message);
}

const projectsById = new Map(
	[...(visibleProjects ?? []), ...(reportBackedProjects ?? [])].map((project) => [project.id, project])
);
const projects = [...projectsById.values()].sort(
	(a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
);

const projectIds = projects.map((project) => project.id);
const { data: reports, error: reportsError } = projectIds.length
	? await supabase
			.from('powerbi_reports')
			.select('project_id,workspace_id,report_id,dataset_id,embed_url,web_url,import_status,error_message,created_at,updated_at')
			.in('project_id', projectIds)
	: { data: [], error: null };

if (reportsError) {
	throw new Error(reportsError.message);
}

const reportsByProject = new Map((reports ?? []).map((report) => [report.project_id, report]));
const output = (projects ?? []).map((project) => {
	const report = reportsByProject.get(project.id);
	return {
		id: project.id,
		title: project.title,
		created_at: project.created_at,
		project_type: project.project_type,
		platform_key: project.platform_key,
		embed_status: project.embed_status,
		has_power_bi_url: Boolean(project.power_bi_url),
		power_bi_url: safeUrl(project.power_bi_url),
		has_report_url: Boolean(project.report_url),
		report_url: safeUrl(project.report_url),
		has_github_url: Boolean(project.github_url),
		has_powerbi_report_row: Boolean(report),
		powerbi_report: report
			? {
					import_status: report.import_status,
					has_error: Boolean(report.error_message),
					same_embed_as_project_url: project.power_bi_url === report.embed_url,
					embed_url: safeUrl(report.embed_url),
					web_url: safeUrl(report.web_url),
					created_at: report.created_at,
					updated_at: report.updated_at
				}
			: null
	};
});

console.log(JSON.stringify(output, null, 2));
