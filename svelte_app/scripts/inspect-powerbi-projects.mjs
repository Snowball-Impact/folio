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

function describeUrl(value) {
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
			hasPageName: url.searchParams.has('pageName'),
			hasChromeless: url.searchParams.has('chromeless'),
			length: src.length
		};
	} catch {
		return {
			rawStart: src.slice(0, 80),
			length: src.length
		};
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
	throw new Error('PUBLIC_SUPABASE_URL or PUBLIC_SUPABASE_PUBLISHABLE_KEY is missing.');
}

const supabase = createClient(supabaseUrl, publishableKey, {
	auth: {
		autoRefreshToken: false,
		persistSession: false
	}
});

const terms = process.argv.slice(2);
const searchTerms = terms.length ? terms : ['test', 'smartHRD', '국비'];
const titleFilter = searchTerms.map((term) => `title.ilike.%${term}%`).join(',');

const { data: projects, error } = await supabase
	.from('projects')
	.select('id,title,created_at,project_type,platform_key,status,embed_status,power_bi_url,report_url,github_url')
	.eq('is_public', true)
	.eq('status', 'published')
	.or(titleFilter)
	.order('created_at', { ascending: false })
	.limit(20);

if (error) {
	throw new Error(error.message);
}

const projectIds = (projects ?? []).map((project) => project.id);
let reports = [];
if (projectIds.length) {
	const result = await supabase
		.from('powerbi_reports')
		.select('project_id,embed_url,web_url,import_status,error_message')
		.in('project_id', projectIds);
	if (result.error) {
		console.warn(`powerbi_reports query failed: ${result.error.message}`);
	} else {
		reports = result.data ?? [];
	}
}

const reportsByProject = new Map(reports.map((report) => [report.project_id, report]));
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
		power_bi_url: describeUrl(project.power_bi_url),
		has_report_url: Boolean(project.report_url),
		report_url: describeUrl(project.report_url),
		has_github_url: Boolean(project.github_url),
		powerbi_report: report
			? {
					import_status: report.import_status,
					has_error: Boolean(report.error_message),
					embed_url: describeUrl(report.embed_url),
					web_url: describeUrl(report.web_url)
				}
			: null
	};
});

console.log(JSON.stringify(output, null, 2));
