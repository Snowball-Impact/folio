import { spawn } from 'node:child_process';
import { existsSync, readFileSync } from 'node:fs';

loadDotEnv();

const host = process.env.SMOKE_HOST || '127.0.0.1';
const port = Number(process.env.PORT || process.env.SMOKE_PORT || 4173);
const baseUrl = `http://${host}:${port}`;
const routes = ['/', '/powerbi', '/references/powerbi', ...optionalProjectRoutes()];
const startupTimeoutMs = Number(process.env.SMOKE_STARTUP_TIMEOUT_MS || 15000);
const requestTimeoutMs = Number(process.env.SMOKE_REQUEST_TIMEOUT_MS || 10000);

let server;

try {
	server = startServer();
	await waitForServer();
	for (const route of routes) {
		await assertRoute(route);
	}
	console.log(`Smoke test passed for ${routes.length} route(s) at ${baseUrl}.`);
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
			console.error(`Smoke server exited with code ${code}${signal ? ` and signal ${signal}` : ''}.`);
		}
	});
	return child;
}

async function waitForServer() {
	const startedAt = Date.now();
	let lastError;
	while (Date.now() - startedAt < startupTimeoutMs) {
		try {
			const response = await fetchWithTimeout(`${baseUrl}/`, requestTimeoutMs);
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

async function assertRoute(route) {
	const response = await fetchWithTimeout(`${baseUrl}${route}`, requestTimeoutMs);
	if (!response.ok) {
		const body = await response.text().catch(() => '');
		throw new Error(`GET ${route} returned ${response.status}. ${body.slice(0, 240)}`);
	}
	console.log(`OK ${response.status} ${route}`);
}

async function fetchWithTimeout(url, timeoutMs) {
	const controller = new AbortController();
	const timeout = setTimeout(() => controller.abort(), timeoutMs);
	try {
		return await fetch(url, { signal: controller.signal });
	} finally {
		clearTimeout(timeout);
	}
}

function optionalProjectRoutes() {
	const projectId = process.env.SMOKE_PROJECT_ID?.trim();
	return projectId ? [`/projects/${encodeURIComponent(projectId)}`] : [];
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
