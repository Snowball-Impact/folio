import { readdir, stat } from 'node:fs/promises';
import { join, relative } from 'node:path';

const clientRoot = join(process.cwd(), '.svelte-kit', 'output', 'client');
const immutableRoot = join(clientRoot, '_app', 'immutable');
const maxClientChunkBytes = Number(process.env.MAX_CLIENT_CHUNK_KB || 300) * 1024;
const maxGlobalCssBytes = Number(process.env.MAX_GLOBAL_CSS_KB || 105) * 1024;
const maxKatexCssBytes = Number(process.env.MAX_KATEX_CSS_KB || 35) * 1024;

async function collectFiles(directory, extension, files = []) {
	for (const entry of await readdir(directory, { withFileTypes: true })) {
		const path = join(directory, entry.name);
		if (entry.isDirectory()) {
			await collectFiles(path, extension, files);
		} else if (entry.name.endsWith(extension)) {
			files.push(path);
		}
	}
	return files;
}

function formatBytes(bytes) {
	return `${(bytes / 1024).toFixed(2)}KB`;
}

function findLargest(files, sizes) {
	return files.reduce((largest, file) => (sizes.get(file) > sizes.get(largest) ? file : largest));
}

try {
	const jsFiles = await collectFiles(immutableRoot, '.js');
	const cssFiles = await collectFiles(immutableRoot, '.css');
	const allFiles = [...jsFiles, ...cssFiles];
	const sizes = new Map(
		await Promise.all(allFiles.map(async (file) => [file, (await stat(file)).size]))
	);

	if (jsFiles.length === 0 || cssFiles.length === 0) {
		throw new Error('빌드 산출물이 없습니다. 먼저 npm.cmd run build를 실행하세요.');
	}

	const largestClientChunk = findLargest(jsFiles, sizes);
	const globalCssCandidates = cssFiles.filter(
		(file) => !file.includes('katex.') && !file.includes('projectBody.')
	);
	const globalCss = findLargest(globalCssCandidates.length > 0 ? globalCssCandidates : cssFiles, sizes);
	const katexCss = cssFiles.find((file) => file.includes('katex.'));
	const checks = [
		{
			name: 'largest client chunk',
			file: relative(clientRoot, largestClientChunk),
			actual: sizes.get(largestClientChunk),
			limit: maxClientChunkBytes
		},
		{
			name: 'global CSS',
			file: relative(clientRoot, globalCss),
			actual: sizes.get(globalCss),
			limit: maxGlobalCssBytes
		},
		{
			name: 'KaTeX CSS',
			file: katexCss ? relative(clientRoot, katexCss) : null,
			actual: katexCss ? sizes.get(katexCss) : 0,
			limit: maxKatexCssBytes
		}
	];

	let failed = false;
	for (const check of checks) {
		const passed = check.actual <= check.limit;
		failed ||= !passed;
		console.log(
			`${passed ? 'PASS' : 'FAIL'} ${check.name}: ${formatBytes(check.actual)} / ${formatBytes(check.limit)}${
				check.file ? ` (${check.file})` : ''
			}`
		);
	}

	if (failed) process.exitCode = 1;
} catch (error) {
	console.error(error instanceof Error ? error.message : String(error));
	process.exitCode = 1;
}
