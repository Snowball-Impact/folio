import { chromium } from '@playwright/test';
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { createClient } from '@supabase/supabase-js';

function loadDotEnv(path) {
	if (!existsSync(path)) return;
	for (const line of readFileSync(path, 'utf8').split(/\r?\n/)) {
		const match = line.match(/^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)\s*$/);
		if (match && !process.env[match[1]]) {
			let value = match[2].trim();
			if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith("'") && value.endsWith("'"))) {
				value = value.slice(1, -1);
			}
			process.env[match[1]] = value;
		}
	}
}

loadDotEnv(resolve(process.cwd(), '.env'));
loadDotEnv(resolve(process.cwd(), '..', '.env'));

const TRUSTED_EMBED_HOSTS = new Set([
	'app.powerbi.com',
	'app.fabric.microsoft.com',
	'public.tableau.com',
	'lookerstudio.google.com',
	'datastudio.google.com',
	'share.streamlit.io'
]);

function isTrustedEmbedHost(hostname) {
	const normalized = (hostname || '').trim().toLowerCase();
	return (
		TRUSTED_EMBED_HOSTS.has(normalized) ||
		normalized.endsWith('.streamlit.app') ||
		normalized.endsWith('.github.io')
	);
}

function parseArgs() {
	const args = process.argv.slice(2);
	const options = {
		baseUrl: process.env.PLAYWRIGHT_BASE_URL || 'http://127.0.0.1:5174',
		timeoutMs: 20000,
		concurrency: 5,
		screenshot: false,
		jsonOutput: null,
		limit: null,
		platform: null,
		projectIds: []
	};

	for (let i = 0; i < args.length; i++) {
		const arg = args[i];
		if (arg === '--base-url' && args[i + 1]) {
			options.baseUrl = args[++i];
		} else if (arg === '--timeout' && args[i + 1]) {
			options.timeoutMs = Number(args[++i]);
		} else if (arg === '--concurrency' && args[i + 1]) {
			options.concurrency = Number(args[++i]);
		} else if (arg === '--limit' && args[i + 1]) {
			options.limit = Number(args[++i]);
		} else if (arg === '--platform' && args[i + 1]) {
			options.platform = args[++i];
		} else if (arg === '--screenshot') {
			options.screenshot = true;
		} else if (arg === '--json' && args[i + 1]) {
			options.jsonOutput = args[++i];
		} else if (!arg.startsWith('--')) {
			options.projectIds.push(arg);
		}
	}
	return options;
}

const options = parseArgs();
const supabaseUrl = process.env.PUBLIC_SUPABASE_URL || process.env.SUPABASE_URL;
const publishableKey =
	process.env.PUBLIC_SUPABASE_PUBLISHABLE_KEY ||
	process.env.SUPABASE_PUBLISHABLE_KEY ||
	process.env.SUPABASE_ANON_KEY;

if (!supabaseUrl || !publishableKey) {
	console.error('❌ Supabase 환경 변수가 설정되지 않았습니다.');
	process.exit(1);
}

const supabase = createClient(supabaseUrl, publishableKey, {
	auth: { autoRefreshToken: false, persistSession: false }
});

console.log('🔍 Power BI 대시보드 임베드 무결성 점검 프로그램');
console.log(`🌐 대상 서버: ${options.baseUrl}`);
console.log('------------------------------------------------------------');

let query = supabase
	.from('projects')
	.select('id, title, platform_key, project_type, power_bi_url, status, embed_status')
	.eq('is_public', true)
	.eq('status', 'published')
	.not('power_bi_url', 'is', null)
	.order('created_at', { ascending: false });

if (options.projectIds.length > 0) {
	query = query.in('id', options.projectIds);
}

if (options.platform) {
	query = query.eq('platform_key', options.platform);
}

if (options.limit && options.limit > 0) {
	query = query.limit(options.limit);
}

const { data: projects, error } = await query;
if (error) {
	console.error('❌ 프로젝트 목록 조회 실패:', error.message);
	process.exit(1);
}

if (!projects || projects.length === 0) {
	console.log('ℹ️ 임베드 URL이 설정된 공개 프로젝트가 없습니다.');
	process.exit(0);
}

console.log(`📋 점검 대상 프로젝트: 총 ${projects.length}개\n`);
const artifactsDir = resolve(process.cwd(), 'artifacts', 'embed-checks');
if (options.screenshot) {
	mkdirSync(artifactsDir, { recursive: true });
}

const browser = await chromium.launch({ headless: true });
const results = [];
let nextIndex = 0;
let completedCount = 0;

async function checkProject(project, page, index) {
	const result = {
		index: index + 1,
		id: project.id,
		title: project.title,
		platform: project.platform_key,
		powerBiUrl: project.power_bi_url,
		trustedHost: false,
		httpProbeStatus: null,
		iframeFound: false,
		iframeSrc: null,
		iframeRendered: false,
		cspViolations: [],
		consoleErrors: [],
		status: 'PENDING',
		error: null
	};

	try {
		const parsedUrl = new URL(project.power_bi_url);
		result.trustedHost = isTrustedEmbedHost(parsedUrl.hostname);
		if (parsedUrl.hostname.includes('accounts.google.com')) {
			result.error = '구글 로그인 리다이렉트 URL이 등록됨 (continue 파라미터 확인 필요)';
		}
	} catch (e) {
		result.error = `유효하지 않은 URL: ${e.message}`;
		result.status = 'FAIL';
		return result;
	}

	try {
		const probeRes = await fetch(project.power_bi_url, {
			method: 'GET',
			headers: { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36' },
			signal: AbortSignal.timeout(6000)
		});
		result.httpProbeStatus = probeRes.status;
	} catch (probeErr) {
		result.httpProbeStatus = `Error: ${probeErr.message}`;
	}

	const detailUrl = `${options.baseUrl}/projects/${project.id}`;
	const cspErrors = [];
	const pageErrors = [];

	const consoleHandler = (msg) => {
		if (msg.type() === 'error') {
			if (/Content Security Policy|violates.+frame-src/i.test(msg.text())) {
				cspErrors.push(msg.text());
			} else {
				pageErrors.push(msg.text());
			}
		}
	};
	page.on('console', consoleHandler);

	try {
		await page.goto(detailUrl, { waitUntil: 'domcontentloaded', timeout: options.timeoutMs });
		await page.waitForTimeout(2000);

		const evalResult = await page.evaluate(() => {
			const iframe = document.querySelector('iframe.dashboard-frame');
			const fallback = document.querySelector('.embed-empty.embed-external-state');
			const failed = document.querySelector('.embed-empty.embed-failed-state');
			const loading = document.querySelector('.embed-empty.embed-loading-state');
			const powerBIReport = document.querySelector('.powerbi-report');

			return {
				hasIframe: Boolean(iframe),
				iframeSrc: iframe ? iframe.getAttribute('src') : null,
				iframeWidth: iframe ? Math.round(iframe.getBoundingClientRect().width) : 0,
				iframeHeight: iframe ? Math.round(iframe.getBoundingClientRect().height) : 0,
				hasFallback: Boolean(fallback),
				hasFailed: Boolean(failed),
				failedText: failed ? failed.textContent?.trim() : null,
				hasLoading: Boolean(loading),
				hasPowerBIReport: Boolean(powerBIReport)
			};
		});

		result.iframeFound = evalResult.hasIframe;
		result.iframeSrc = evalResult.iframeSrc;
		result.iframeRendered = evalResult.hasIframe && evalResult.iframeWidth > 0 && evalResult.iframeHeight > 0;
		result.cspViolations = cspErrors;
		result.consoleErrors = pageErrors;

		if (evalResult.hasIframe && result.iframeRendered && cspErrors.length === 0) {
			result.status = 'PASS';
		} else if (evalResult.hasFallback) {
			result.status = 'FALLBACK';
			if (!result.error) result.error = '외부 사이트 열람 상태로 폴백됨 (화이트리스트 외 도메인)';
		} else if (evalResult.hasFailed) {
			result.status = 'FAIL';
			result.error = evalResult.failedText || '임베드 게시 실패 상태';
		} else if (cspErrors.length > 0) {
			result.status = 'FAIL';
			result.error = `CSP 차단 발생: ${cspErrors.join(', ')}`;
		} else {
			result.status = 'WARN';
			if (!result.error) result.error = 'iframe 요소를 찾을 수 없거나 크기가 0입니다.';
		}

		if (options.screenshot) {
			const shotPath = resolve(artifactsDir, `${project.id}.png`);
			await page.screenshot({ path: shotPath, fullPage: false });
			result.screenshotPath = shotPath;
		}
	} catch (navErr) {
		result.status = 'FAIL';
		result.error = `페이지 탐색 시간 초과 또는 오류: ${navErr.message}`;
	} finally {
		page.off('console', consoleHandler);
	}

	return result;
}

async function worker(workerId) {
	const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
	const page = await context.newPage();

	while (true) {
		const currentIndex = nextIndex++;
		if (currentIndex >= projects.length) break;
		const project = projects[currentIndex];

		const res = await checkProject(project, page, currentIndex);
		results.push(res);
		completedCount++;

		const icon = res.status === 'PASS' ? '✅' : res.status === 'FAIL' ? '❌' : res.status === 'FALLBACK' ? 'ℹ️' : '⚠️';
		console.log(`[${completedCount}/${projects.length}] ${icon} ${project.title.slice(0, 35)} (${res.status}${res.error ? `: ${res.error.slice(0, 40)}` : ''})`);
	}

	await context.close();
}

console.log(`🚀 동시 실행(Concurrency): ${options.concurrency}개 워커로 검사 시작...\n`);
const workerCount = Math.min(options.concurrency, projects.length);
await Promise.all(Array.from({ length: workerCount }, (_, id) => worker(id)));

await browser.close();

console.log('\n============================================================');
console.log('📊 임베드 무결성 점검 종합 결과');
console.log('============================================================');

const passCount = results.filter((r) => r.status === 'PASS').length;
const failCount = results.filter((r) => r.status === 'FAIL').length;
const fallbackCount = results.filter((r) => r.status === 'FALLBACK').length;
const warnCount = results.filter((r) => r.status === 'WARN').length;

results.forEach((r, idx) => {
	const icon =
		r.status === 'PASS'
			? '✅ PASS'
			: r.status === 'FAIL'
				? '❌ FAIL'
				: r.status === 'FALLBACK'
					? 'ℹ️ FALLBACK'
					: '⚠️ WARN';
	console.log(`${idx + 1}. [${icon}] ${r.title}`);
	console.log(`   - ID: ${r.id}`);
	console.log(`   - URL: ${r.powerBiUrl}`);
	if (r.error) console.log(`   - 상세: ${r.error}`);
});

console.log('------------------------------------------------------------');
console.log(`총 프로젝트: ${results.length} | 정상(PASS): ${passCount} | 실패(FAIL): ${failCount} | 폴백(FALLBACK): ${fallbackCount} | 경고(WARN): ${warnCount}`);

if (options.jsonOutput) {
	const outPath = resolve(process.cwd(), options.jsonOutput);
	writeFileSync(outPath, JSON.stringify(results, null, 2), 'utf8');
	console.log(`📁 JSON 보고서 저장 완료: ${outPath}`);
}

process.exit(failCount > 0 ? 1 : 0);
