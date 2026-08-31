import { spawn } from 'node:child_process';
import { mkdirSync } from 'node:fs';
import { join, resolve } from 'node:path';

const host = process.env.CLOUDFLARE_SMOKE_HOST || '127.0.0.1';
const port = Number(process.env.CLOUDFLARE_SMOKE_PORT || 8788);
const baseUrl = `http://${host}:${port}`;
const compatibilityDate = process.env.CLOUDFLARE_COMPATIBILITY_DATE || '2025-12-01';
const compatibilityFlag = process.env.CLOUDFLARE_COMPATIBILITY_FLAG || 'nodejs_compat';
const startupTimeoutMs = Number(process.env.SMOKE_STARTUP_TIMEOUT_MS || 30000);
const requestTimeoutMs = Number(process.env.SMOKE_REQUEST_TIMEOUT_MS || 10000);
const routeRetryCount = Number(process.env.SMOKE_ROUTE_RETRIES || 1);
const cleanupTimeoutMs = Number(process.env.SMOKE_CLEANUP_TIMEOUT_MS || 5000);
const projectId = process.env.SMOKE_PROJECT_ID?.trim() || '00000000-0000-0000-0000-000000000000';
const commentId = process.env.SMOKE_COMMENT_ID?.trim() || '00000000-0000-0000-0000-000000000000';

const publicRoutes = [
	'/',
	'/?page=Home',
	'/?page=About',
	'/?page=Policy&type=privacy',
	'/?page=Power%20BI&topic=cert',
	'/about',
	'/policy/privacy',
	'/policy/terms',
	'/policy?type=privacy',
	'/powerbi',
	'/powerbi?topic=cert',
	'/references/powerbi',
	...optionalProjectRoutes()
];
const anonymousPostChecks = [
	`/api/projects/${encodeURIComponent(projectId)}/thumbnail`,
	`/api/projects/${encodeURIComponent(projectId)}/thumbnail-capture`,
	`/api/projects/${encodeURIComponent(projectId)}/powerbi-publish`,
	`/api/comments/${encodeURIComponent(commentId)}/email-notification`
];

let server;
let output = '';

try {
	server = startWrangler();
	await waitForServer();
	for (const route of publicRoutes) {
		await assertPublicRoute(route);
	}
	for (const path of anonymousPostChecks) {
		await assertAnonymousPostRejected(path);
	}
	console.log(`Cloudflare smoke passed for ${publicRoutes.length} route(s) and ${anonymousPostChecks.length} anonymous endpoint check(s) at ${baseUrl}.`);
} finally {
	if (server) {
		await stopServer(server);
	}
}

function startWrangler() {
	const isWindows = process.platform === 'win32';
	const command = isWindows ? 'cmd.exe' : 'wrangler';
	const args = [
		'pages',
		'dev',
		'.svelte-kit/cloudflare',
		`--compatibility-date=${compatibilityDate}`,
		`--compatibility-flag=${compatibilityFlag}`,
		`--ip=${host}`,
		`--port=${port}`
	];
	const child = spawn(command, isWindows ? ['/c', 'wrangler', ...args] : args, {
		env: sanitizedEnv(),
		stdio: ['ignore', 'pipe', 'pipe']
	});
	child.stdout.on('data', captureOutput);
	child.stderr.on('data', captureOutput);
	child.on('exit', (code, signal) => {
		if (code && code !== 0 && !server) {
			console.error(`Wrangler exited with code ${code}${signal ? ` and signal ${signal}` : ''}.`);
		}
	});
	return child;
}



function stopServer(child) {
	if (process.platform !== 'win32') {
		child.kill();
		return Promise.resolve();
	}
	return new Promise((resolve) => {
		let settled = false;
		let timeout;
		const finish = () => {
			if (settled) return;
			settled = true;
			clearTimeout(timeout);
			resolve();
		};
		const killer = spawn('taskkill', ['/pid', String(child.pid), '/t', '/f'], {
			stdio: ['ignore', 'ignore', 'ignore']
		});
		timeout = setTimeout(() => {
			try {
				child.kill();
			} finally {
				finish();
			}
		}, cleanupTimeoutMs);
		killer.on('exit', finish);
		killer.on('error', finish);
	});
}
function sanitizedEnv() {
	const runtimeEnv = Object.fromEntries(
		Object.entries(process.env).filter(([key, value]) => key && !key.startsWith('=') && value !== undefined)
	);
	const runtimeRoot = resolve(process.cwd(), '..', '.runtime');
	const xdgConfigHome = join(runtimeRoot, 'xdg-config');
	const miniflareRegistryPath = join(runtimeRoot, 'miniflare-registry');
	mkdirSync(xdgConfigHome, { recursive: true });
	mkdirSync(miniflareRegistryPath, { recursive: true });
	return {
		...runtimeEnv,
		XDG_CONFIG_HOME: xdgConfigHome,
		MINIFLARE_REGISTRY_PATH: miniflareRegistryPath
	};
}
function captureOutput(chunk) {
	output += chunk.toString();
	if (output.length > 12000) {
		output = output.slice(-12000);
	}
}

async function waitForServer() {
	const startedAt = Date.now();
	let lastError;
	while (Date.now() - startedAt < startupTimeoutMs) {
		if (server.exitCode !== null) {
			throw new Error(`Wrangler exited before becoming ready.\n${output}`);
		}
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
	throw new Error(`Cloudflare preview did not become ready within ${startupTimeoutMs}ms. ${lastError?.message || ''}\n${output}`);
}

async function assertPublicRoute(route) {
	const response = await fetchWithTimeout(
		`${baseUrl}${route}`,
		{ method: 'GET' },
		requestTimeoutMs,
		routeRetryCount
	);
	if (!response.ok) {
		const body = await response.text().catch(() => '');
		throw new Error(`GET ${route} returned ${response.status}. ${body.slice(0, 240)}`);
	}
	console.log(`OK ${response.status} ${route}`);
}

async function assertAnonymousPostRejected(path) {
	const response = await fetchWithTimeout(
		`${baseUrl}${path}`,
		{
			method: 'POST',
			headers: { origin: baseUrl }
		},
		requestTimeoutMs
	);
	if (response.status !== 401) {
		const body = await response.text().catch(() => '');
		throw new Error(`POST ${path} expected 401 for anonymous request, got ${response.status}. ${body.slice(0, 240)}`);
	}
	console.log(`OK ${response.status} anonymous POST ${path}`);
}


async function fetchWithTimeout(url, options, timeoutMs, retries = 0) {
	let lastError;
	for (let attempt = 0; attempt <= retries; attempt += 1) {
		const controller = new AbortController();
		const timeout = setTimeout(() => controller.abort(), timeoutMs);
		try {
			return await fetch(url, { ...options, signal: controller.signal });
		} catch (error) {
			lastError = error;
			if (attempt >= retries || options.method !== 'GET') {
				throw error;
			}
			console.warn(`Retrying GET ${url} after attempt ${attempt + 1}: ${error instanceof Error ? error.message : String(error)}`);
			await sleep(250 * (attempt + 1));
		} finally {
			clearTimeout(timeout);
		}
	}
	throw lastError;
}

function optionalProjectRoutes() {
	const id = process.env.SMOKE_PROJECT_ID?.trim();
	if (!id) {
		return [];
	}
	const encoded = encodeURIComponent(id);
	return [
		`/projects/${encoded}`,
		`/?page=Home&project_id=${encoded}`,
		`/?page=Reference&project_id=${encoded}&platform=powerbi`,
		`/?page=My%20Page&edit_project=${encoded}`
	];
}

function sleep(milliseconds) {
	return new Promise((resolve) => setTimeout(resolve, milliseconds));
}
