import { existsSync, readdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';

loadDotEnv('../.env');
loadDotEnv('.env');

assertSecretNamesAreServerOnly();
assertClientBundleDoesNotContainPrivateEnvValues();
console.log('Security smoke passed for source and Cloudflare client bundle checks.');

function assertSecretNamesAreServerOnly() {
	const clientFiles = listFiles('src', (path) => path.endsWith('.svelte') || path.endsWith('.ts'));
	const forbiddenNames = [
		'SUPABASE_SERVICE_ROLE_KEY',
		'POWERBI_CLIENT_SECRET',
		'SMTP_PASSWORD',
		'CLOUDFLARE_BROWSER_RENDERING_API_TOKEN'
	];
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
		process.env.SMTP_PASSWORD,
		process.env.CLOUDFLARE_BROWSER_RENDERING_API_TOKEN
	]
		.map((value) => value?.trim())
		.filter((value) => value && value.length >= 8);
	if (candidates.length === 0) {
		console.log('OK no private env values available for client bundle scan.');
		return;
	}
	const roots = ['.svelte-kit/cloudflare/_app', 'build/client'];
	const clientFiles = roots.flatMap((root) =>
		listFiles(root, (path) => path.endsWith('.js') || path.endsWith('.css') || path.endsWith('.html') || path.endsWith('.json'))
	);
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

function loadDotEnv(path) {
	if (!existsSync(path)) {
		return;
	}
	const lines = readFileSync(path, 'utf8').split(/\r?\n/);
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
