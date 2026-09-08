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
	try {
		const url = new URL(value);
		return {
			host: url.host,
			path: url.pathname,
			hasCacheBuster: url.searchParams.has('v')
		};
	} catch {
		return { invalid: true };
	}
}

loadDotEnv(resolve(process.cwd(), '..', '.env'));
loadDotEnv(resolve(process.cwd(), '.env'));

const supabaseUrl = process.env.PUBLIC_SUPABASE_URL ?? process.env.SUPABASE_URL;
const publishableKey =
	process.env.PUBLIC_SUPABASE_PUBLISHABLE_KEY ??
	process.env.SUPABASE_PUBLISHABLE_KEY ??
	process.env.SUPABASE_ANON_KEY;
const serviceRoleKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

if (!supabaseUrl || !publishableKey) {
	throw new Error('Supabase env is missing.');
}

const supabase = createClient(supabaseUrl, publishableKey, {
	auth: { persistSession: false, autoRefreshToken: false }
});

const { data, error } = await supabase
	.from('projects')
	.select('id,title,created_at,status,is_public,thumbnail_mode,thumbnail_url,project_type,platform_key')
	.order('created_at', { ascending: false })
	.limit(12);

if (error) {
	throw new Error(error.message);
}

const projects = data ?? [];

const output = {
	projects: projects.map((project) => ({
		id: project.id,
		title: project.title,
		created_at: project.created_at,
		status: project.status,
		is_public: project.is_public,
		thumbnail_mode: project.thumbnail_mode,
		has_thumbnail_url: Boolean(project.thumbnail_url),
		thumbnail_url: safeUrl(project.thumbnail_url),
		project_type: project.project_type,
		platform_key: project.platform_key
	}))
};

if (serviceRoleKey) {
	const admin = createClient(supabaseUrl, serviceRoleKey, {
		auth: { persistSession: false, autoRefreshToken: false }
	});
	const bucketName = process.env.THUMBNAIL_STORAGE_BUCKET || 'project-thumbnails';
	const { data: buckets, error: bucketError } = await admin.storage.listBuckets();
	const bucket = buckets?.find((item) => item.name === bucketName);
	const latestProject = projects[0];
	output.storage = {
		bucket: bucketName,
		bucket_error: bucketError?.message ?? '',
		bucket_exists: Boolean(bucket),
		bucket_public: bucket?.public ?? null,
		latest_project_files: []
	};
	if (bucket && latestProject?.id) {
		const directory = `projects/${String(latestProject.id).replace(/[^a-zA-Z0-9_-]/g, '_')}`;
		const { data: files, error: listError } = await admin.storage.from(bucketName).list(directory, { limit: 20 });
		output.storage.latest_project_directory = directory;
		output.storage.latest_project_list_error = listError?.message ?? '';
		output.storage.latest_project_files = (files ?? []).map((file) => ({
			name: file.name,
			size: file.metadata?.size ?? null,
			mimetype: file.metadata?.mimetype ?? null
		}));
	}
}

console.log(
	JSON.stringify(
		output,
		null,
		2
	)
);
