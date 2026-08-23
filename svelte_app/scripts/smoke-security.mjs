import { spawn } from 'node:child_process';
import { existsSync, readdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';

loadDotEnv();

const host = process.env.SECURITY_SMOKE_HOST || process.env.SMOKE_HOST || '127.0.0.1';
const port = Number(process.env.SECURITY_SMOKE_PORT || 4174);
const baseUrl = `http://${host}:${port}`;
const startupTimeoutMs = Number(process.env.SMOKE_STARTUP_TIMEOUT_MS || 15000);
const requestTimeoutMs = Number(process.env.SMOKE_REQUEST_TIMEOUT_MS || 10000);
const projectId = process.env.SMOKE_PROJECT_ID?.trim() || '00000000-0000-0000-0000-000000000000';
const commentId = process.env.SMOKE_COMMENT_ID?.trim() || '00000000-0000-0000-0000-000000000000';

const anonymousPostChecks = [
	{ path: `/api/projects/${encodeURIComponent(projectId)}/thumbnail`, body: new FormData() },
	{ path: `/api/projects/${encodeURIComponent(projectId)}/thumbnail-capture`, body: new FormData() },
	{ path: `/api/projects/${encodeURIComponent(projectId)}/powerbi-publish`, body: new FormData() },
	{ path: `/api/comments/${encodeURIComponent(commentId)}/email-notification` }
];

let server;

try {
	assertSecretNamesAreServerOnly();
	assertClientBundleDoesNotContainPrivateEnvValues();
	server = startServer();
	await waitForServer();
	for (const check of anonymousPostChecks) {
		await assertAnonymousPostRejected(check);
	}
	console.log(`Security smoke passed for ${anonymousPostChecks.length} anonymous endpoint check(s).`);
} finally {
	if (server) {
		server.kill();
	}
}

function startServer() {
	const child = spawn(process.execPath, ['build'], {
		env: {
			...process.env,
			HOST: host,
			PORT: String(port)
		},
		stdio: ['ignore', 'pipe', 'pipe']
	});
	child.stdout.on('data', (chunk) => process.stdout.write(`[server] ${chunk}`));
	child.stderr.on('data', (chunk) => process.stderr.write(`[server] ${chunk}`));
	child.on('exit', (code, signal) => {
		if (code && code !== 0) {
			console.error(`Security smoke server exited with code ${code}${signal ? ` and signal ${signal}` : ''}.`);
		}
	});
	return child;
}

async function waitForServer() {
	const startedAt = Date.now();
	let lastError;
	while (Date.now() - startedAt < startupTimeoutMs) {
		try {
			const response = await fetchWithTimeout(`${baseUrl}/`, { method: 'GET' }, requestTimeoutMs);
			if (response.status < 500) {
				return;
			}
			lastError = new Error(`Server returned ${response.status}.`);
		} catch (error) {
			lastError = error;
		}
		await sleep(250);
	}
	throw new Error(`Server did not become ready within ${startupTimeoutMs}ms. ${lastError?.message || ''}`);
}

async function assertAnonymousPostRejected(check) {
	const response = await fetchWithTimeout(
		`${baseUrl}${check.path}`,
		{
			method: 'POST',
			headers: { origin: baseUrl }
		},
		requestTimeoutMs
	);
	if (response.status !== 401) {
		const body = await response.text().catch(() => '');
		throw new Error(`POST ${check.path} expected 401 for anonymous request, got ${response.status}. ${body.slice(0, 240)}`);
	}
	console.log(`OK ${response.status} anonymous POST ${check.path}`);
}

function assertSecretNamesAreServerOnly() {
	const clientFiles = listFiles('src', (path) => path.endsWith('.svelte') || path.endsWith('.ts'));
	const forbiddenNames = ['SUPABASE_SERVICE_ROLE_KEY', 'POWERBI_CLIENT_SECRET', 'SMTP_PASSWORD'];
	const offenders = [];
	for (const file of clientFiles) {
		if (file.includes(join('src', 'lib', 'server')) || file.endsWith('+server.ts')) {
			continue;
		}
		const text = readFileSync(file, 'utf8');
		for (const name of forbiddenNames) {
			if (text.includes(name)) {
				offenders.push(`${file}: ${name}`);
			}
		}
	}
	if (offenders.length > 0) {
		throw new Error(`Private env name referenced outside server-only code:\n${offenders.join('\n')}`);
	}
	console.log('OK private env names are server-only in source.');
}

function assertClientBundleDoesNotContainPrivateEnvValues() {
	const candidates = [
		process.env.SUPABASE_SERVICE_ROLE_KEY,
		process.env.POWERBI_CLIENT_SECRET,
		process.env.SMTP_PASSWORD
	]
		.map((value) => value?.trim())
		.filter((value) => value && value.length >= 8);
	if (candidates.length === 0) {
		console.log('OK no private env values available for client bundle scan.');
		return;
	}
	const clientFiles = listFiles('build/client', (path) => path.endsWith('.js') || path.endsWith('.css') || path.endsWith('.html'));
	const leaks = [];
	for (const file of clientFiles) {
		const text = readFileSync(file, 'utf8');
		for (const value of candidates) {
			if (text.includes(value)) {
				leaks.push(file);
			}
		}
	}
	if (leaks.length > 0) {
		throw new Error(`Private env value found in client bundle:\n${[...new Set(leaks)].join('\n')}`);
	}
	console.log(`OK scanned ${clientFiles.length} client bundle file(s) for private env values.`);
}

function listFiles(root, predicate) {
	if (!existsSync(root)) {
		return [];
	}
	const files = [];
	const stack = [root];
	while (stack.length > 0) {
		const current = stack.pop();
		for (const entry of readdirSync(current, { withFileTypes: true })) {
			const path = join(current, entry.name);
			if (entry.isDirectory()) {
				stack.push(path);
			} else if (predicate(path)) {
				files.push(path);
			}
		}
	}
	return files;
}

async function fetchWithTimeout(url, options, timeoutMs) {
	const controller = new AbortController();
	const timeout = setTimeout(() => controller.abort(), timeoutMs);
	try {
		return await fetch(url, { ...options, signal: controller.signal });
	} finally {
		clearTimeout(timeout);
	}
}

function sleep(milliseconds) {
	return new Promise((resolve) => setTimeout(resolve, milliseconds));
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
