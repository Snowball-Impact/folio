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
const page = await browser.newPage({
	viewport: { width: 1440, height: 900 }
});

const results = [];

for (const project of projects) {
	const result = {
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

	console.log(`\n▶ [${project.title}] (${project.id})`);
	console.log(`  🔗 임베드 URL: ${project.power_bi_url}`);

	try {
		const parsedUrl = new URL(project.power_bi_url);
		result.trustedHost = isTrustedEmbedHost(parsedUrl.hostname);
		if (!result.trustedHost) {
			console.log(`  ⚠️ 신뢰 호스트 목록에 없음: ${parsedUrl.hostname}`);
		}
	} catch (e) {
		result.error = `유효하지 않은 URL: ${e.message}`;
		result.status = 'FAIL';
		console.log(`  ❌ ${result.error}`);
		results.push(result);
		continue;
	}

	try {
		const probeRes = await fetch(project.power_bi_url, {
			method: 'GET',
			headers: { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36' },
			signal: AbortSignal.timeout(8000)
		});
		result.httpProbeStatus = probeRes.status;
		const xFrame = probeRes.headers.get('x-frame-options');
		if (xFrame && (xFrame.toLowerCase().includes('deny') || xFrame.toLowerCase().includes('sameorigin'))) {
			console.log(`  ⚠️ 외부 원본 서버에서 iframe 차단 헤더 설정됨 (X-Frame-Options: ${xFrame})`);
		}
	} catch (probeErr) {
		result.httpProbeStatus = `Error: ${probeErr.message}`;
		console.log(`  ⚠️ 원본 URL 직접 접근 시도 실패: ${probeErr.message}`);
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
		await page.waitForTimeout(3000);

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
			console.log(`  ✅ iframe 정상 로딩 완료 (${evalResult.iframeWidth}x${evalResult.iframeHeight})`);
		} else if (evalResult.hasFallback) {
			result.status = 'FALLBACK';
			result.error = '외부 사이트 열람 상태로 폴백됨';
			console.log(`  ℹ️ 폴백 상태: 연결된 산출물을 새 탭에서 확인하세요.`);
		} else if (evalResult.hasFailed) {
			result.status = 'FAIL';
			result.error = evalResult.failedText || '임베드 게시 실패 상태';
			console.log(`  ❌ 실패 상태: ${result.error}`);
		} else if (cspErrors.length > 0) {
			result.status = 'FAIL';
			result.error = `CSP 차단 발생: ${cspErrors.join(', ')}`;
			console.log(`  ❌ ${result.error}`);
		} else {
			result.status = 'WARN';
			result.error = 'iframe 요소를 찾을 수 없거나 크기가 0입니다.';
			console.log(`  ⚠️ ${result.error}`);
		}

		if (options.screenshot) {
			const shotPath = resolve(artifactsDir, `${project.id}.png`);
			await page.screenshot({ path: shotPath, fullPage: false });
			result.screenshotPath = shotPath;
		}
	} catch (navErr) {
		result.status = 'FAIL';
		result.error = `페이지 탐색 시간 초과 또는 오류: ${navErr.message}`;
		console.log(`  ❌ ${result.error}`);
	} finally {
		page.off('console', consoleHandler);
	}

	results.push(result);
}

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
