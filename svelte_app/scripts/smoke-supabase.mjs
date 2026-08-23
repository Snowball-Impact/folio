import { existsSync, readFileSync } from 'node:fs';
import { createClient } from '@supabase/supabase-js';
process.on('unhandledRejection', handleFatalError);
process.on('uncaughtException', handleFatalError);


loadDotEnv();

const required = process.env.SMOKE_SUPABASE_REQUIRED === 'true';
const supabaseUrl = firstEnv('PUBLIC_SUPABASE_URL', 'SUPABASE_URL');
const publishableKey = firstEnv('PUBLIC_SUPABASE_PUBLISHABLE_KEY', 'SUPABASE_PUBLISHABLE_KEY', 'SUPABASE_ANON_KEY');
const projectIdOverride = process.env.SMOKE_PROJECT_ID?.trim();
const thumbnailModes = new Set(['auto_cover', 'manual_url', 'capture', 'upload']);

if (!supabaseUrl || !publishableKey) {
	const message = 'SKIP Supabase smoke: PUBLIC_SUPABASE_URL or PUBLIC_SUPABASE_PUBLISHABLE_KEY is missing.';
	if (required) {
		throw new Error(message);
	}
	console.warn(message);
	process.exit(0);
}

const supabase = createClient(supabaseUrl, publishableKey, {
	auth: {
		autoRefreshToken: false,
		persistSession: false
	}
});

const home = await callHomeSnapshot();
const projectCards = collectProjectCards(home);
validateProjectCards(projectCards, 'home_project_snapshot');

const sampleProject = await findSampleProject(projectCards);
if (sampleProject) {
	await callProjectDetailSnapshot(sampleProject.id);
} else {
	console.warn('SKIP project_detail_snapshot: no public published project sample found.');
}

await checkPowerBIReportsContract();
console.log('Supabase contract smoke passed.');

async function callHomeSnapshot() {
	const { data, error } = await supabase.rpc('home_project_snapshot', {
		p_limit: 3,
		p_tag_limit: 10,
		p_like_sample_limit: 30,
		p_platform_key: 'powerbi'
	});
	if (error) {
		throw new Error(`home_project_snapshot failed: ${error.message}`);
	}
	const record = asRecord(data);
	for (const key of ['recent_projects', 'viewed_projects', 'liked_projects']) {
		if (!Array.isArray(record[key])) {
			throw new Error(`home_project_snapshot missing array field: ${key}`);
		}
	}
	console.log('OK home_project_snapshot');
	return record;
}

async function findSampleProject(projectCards) {
	const cardProject = projectIdOverride
		? null
		: projectCards.find((project) => typeof project.id === 'string' && project.id.trim());
	if (projectIdOverride || cardProject?.id) {
		return { id: projectIdOverride || cardProject.id };
	}

	const { data, error } = await supabase
		.from('projects')
		.select('id,title,thumbnail_mode,platform_key')
		.eq('is_public', true)
		.eq('status', 'published')
		.limit(1)
		.maybeSingle();
	if (error) {
		throw new Error(`projects sample query failed: ${error.message}`);
	}
	if (!data) {
		return null;
	}
	validateProjectCard(asRecord(data), 'projects sample');
	console.log(`OK projects sample ${data.id}`);
	return data;
}

async function callProjectDetailSnapshot(projectId) {
	const { data, error } = await supabase.rpc('project_detail_snapshot', {
		p_project_id: projectId
	});
	if (error) {
		throw new Error(`project_detail_snapshot failed: ${error.message}`);
	}
	if (!data) {
		throw new Error(`project_detail_snapshot returned no project for ${projectId}`);
	}
	validateProjectCard(asRecord(data), 'project_detail_snapshot');
	console.log(`OK project_detail_snapshot ${projectId}`);
}

async function checkPowerBIReportsContract() {
	const { error } = await supabase
		.from('powerbi_reports')
		.select('project_id,workspace_id,report_id,dataset_id,embed_url,web_url,import_id,import_status,error_message')
		.limit(1);
	if (error) {
		throw new Error(`powerbi_reports contract query failed: ${error.message}`);
	}
	console.log('OK powerbi_reports contract');
}

function collectProjectCards(home) {
	return ['recent_projects', 'viewed_projects', 'liked_projects'].flatMap((key) =>
		Array.isArray(home[key]) ? home[key].map(asRecord) : []
	);
}

function validateProjectCards(projects, sourceName) {
	if (projects.length === 0) {
		console.warn(`SKIP ${sourceName} card field checks: no project cards returned.`);
		return;
	}
	for (const project of projects) {
		validateProjectCard(project, sourceName);
	}
	console.log(`OK ${sourceName} project card fields`);
}

function validateProjectCard(project, sourceName) {
	for (const field of ['id', 'title', 'thumbnail_mode', 'platform_key']) {
		if (!(field in project)) {
			throw new Error(`${sourceName} missing field: ${field}`);
		}
	}
	if (!thumbnailModes.has(String(project.thumbnail_mode))) {
		throw new Error(`${sourceName} has invalid thumbnail_mode: ${project.thumbnail_mode}`);
	}
}

function asRecord(value) {
	return value && typeof value === 'object' ? value : {};
}

function firstEnv(...names) {
	for (const name of names) {
		const value = process.env[name]?.trim();
		if (value) {
			return value;
		}
	}
	return '';
}

function loadDotEnv() {
	if (!existsSync('.env')) {
		return;
	}
	const lines = readFileSync('.env', 'utf8').split(/\r?\n/);
	for (const line of lines) {
		const trimmed = line.trim();
		if (!trimmed || trimmed.startsWith('#')) {
			continue;
		}
		const match = trimmed.match(/^([A-Za-z_][A-Za-z0-9_]*)=(.*)$/);
		if (!match || process.env[match[1]] !== undefined) {
			continue;
		}
		process.env[match[1]] = unquoteEnvValue(match[2].trim());
	}
}

function unquoteEnvValue(value) {
	if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith("'") && value.endsWith("'"))) {
		return value.slice(1, -1);
	}
	return value;
}

function handleFatalError(error) {
	const message = error instanceof Error ? error.message : String(error);
	console.error('FAIL Supabase smoke: ' + message);
	process.exitCode = 1;
}
