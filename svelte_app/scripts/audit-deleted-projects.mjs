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

loadDotEnv(resolve(process.cwd(), '..', '.env'));
loadDotEnv(resolve(process.cwd(), '.env'));

const supabaseUrl = process.env.PUBLIC_SUPABASE_URL ?? process.env.SUPABASE_URL;
const serviceRoleKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

if (!supabaseUrl || !serviceRoleKey) {
	throw new Error('Supabase service env is missing.');
}

const supabase = createClient(supabaseUrl, serviceRoleKey, {
	auth: { persistSession: false, autoRefreshToken: false }
});

const recentDays = Math.max(Number(process.env.AUDIT_DELETED_PROJECT_DAYS ?? 7), 1);
const recentCutoff = new Date(Date.now() - recentDays * 24 * 60 * 60 * 1000).toISOString();

const counts = {
	total: await projectCount('total', (query) => query),
	published_public: await projectCount('published_public', (query) => query.eq('status', 'published').eq('is_public', true)),
	deleted: await projectCount('deleted', (query) => query.eq('status', 'deleted')),
	deleted_public: await projectCount('deleted_public', (query) => query.eq('status', 'deleted').eq('is_public', true)),
	deleted_missing_deleted_at: await projectCount(
		'deleted_missing_deleted_at',
		(query) => query.eq('status', 'deleted').is('deleted_at', null)
	),
	recent_deleted: await projectCount('recent_deleted', (query) => query.eq('status', 'deleted').gte('deleted_at', recentCutoff))
};

const { data: recentDeleted, error: recentDeletedError } = await supabase
	.from('projects')
	.select('id,title,created_at,deleted_at,is_public,thumbnail_mode,thumbnail_url,project_type,embed_status,power_bi_url,problem,dataset,process,insights')
	.eq('status', 'deleted')
	.gte('deleted_at', recentCutoff)
	.order('deleted_at', { ascending: false })
	.limit(30);

if (recentDeletedError) {
	throw new Error(`recent_deleted: ${recentDeletedError.message}`);
}

const deletedIds = (recentDeleted ?? []).map((project) => project.id).filter(Boolean);
const powerbiReports = deletedIds.length ? await powerbiReportsFor(deletedIds) : [];
const thumbnailStorage = await thumbnailStorageFor((recentDeleted ?? []).filter((project) => project.thumbnail_url));
const bodyStorage = await bodyStorageFor(recentDeleted ?? []);

const reportProjectIds = new Set(powerbiReports.map((report) => report.project_id));
const storageByProjectId = new Map(thumbnailStorage.map((entry) => [entry.project_id, entry]));
const bodyStorageByProjectId = new Map(bodyStorage.map((entry) => [entry.project_id, entry]));

const output = {
	window_days: recentDays,
	counts,
	recent_deleted_projects: (recentDeleted ?? []).map((project) => ({
		id: project.id,
		title: project.title,
		created_at: project.created_at,
		deleted_at: project.deleted_at,
		is_public: project.is_public,
		thumbnail_mode: project.thumbnail_mode,
		has_thumbnail_url: Boolean(project.thumbnail_url),
		project_type: project.project_type,
		embed_status: project.embed_status,
		has_power_bi_url: Boolean(project.power_bi_url),
		has_powerbi_report: reportProjectIds.has(project.id),
		storage_file_count: storageByProjectId.get(project.id)?.file_count ?? 0,
		storage_list_error: storageByProjectId.get(project.id)?.error ?? '',
		has_body_storage_url: hasBodyStorageUrl(project),
		body_storage_file_count: bodyStorageByProjectId.get(project.id)?.file_count ?? 0,
		body_storage_list_error: bodyStorageByProjectId.get(project.id)?.error ?? ''
	})),
	recent_deleted_powerbi_report_count: powerbiReports.length,
	recent_deleted_thumbnail_file_count: thumbnailStorage.reduce((sum, entry) => sum + entry.file_count, 0),
	recent_deleted_body_storage_file_count: bodyStorage.reduce((sum, entry) => sum + entry.file_count, 0)
};

console.log(JSON.stringify(output, null, 2));

async function projectCount(name, applyFilter) {
	const { count, error } = await applyFilter(supabase.from('projects').select('id', { count: 'exact', head: true }));
	if (error) {
		throw new Error(`${name}: ${error.message}`);
	}
	return count ?? 0;
}

async function powerbiReportsFor(projectIds) {
	const { data, error } = await supabase
		.from('powerbi_reports')
		.select('project_id,report_id,dataset_id,updated_at')
		.in('project_id', projectIds);
	if (error) {
		throw new Error(`powerbi_reports: ${error.message}`);
	}
	return data ?? [];
}

async function thumbnailStorageFor(projects) {
	const bucketName = process.env.THUMBNAIL_STORAGE_BUCKET || 'project-thumbnails';
	return storageFor(projects, bucketName);
}

async function bodyStorageFor(projects) {
	const bucketName = process.env.BODY_IMAGE_STORAGE_BUCKET || 'project-body-assets';
	return storageFor(projects.filter(hasBodyStorageUrl), bucketName);
}

async function storageFor(projects, bucketName) {
	const bucket = supabase.storage.from(bucketName);
	const results = [];
	for (const project of projects) {
		const directory = `projects/${safeStorageName(project.id)}`;
		const { data, error } = await bucket.list(directory, { limit: 100 });
		results.push({
			project_id: project.id,
			file_count: data?.length ?? 0,
			error: error?.message ?? ''
		});
	}
	return results;
}

function hasBodyStorageUrl(project) {
	return [project.problem, project.dataset, project.process, project.insights].some((value) =>
		String(value ?? '').includes('/storage/v1/object/public/project-body-assets/')
	);
}

function safeStorageName(value) {
	return String(value).replace(/[^a-zA-Z0-9_-]/g, '_');
}
