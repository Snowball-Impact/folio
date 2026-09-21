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

// 외부 플랫폼별 비정상/오류 시그니처 패턴 (정규식)
const ERROR_SIGNATURES = [
	{
		platform: 'Power BI / Fabric',
		hostMatch: /(powerbi\.com|fabric\.microsoft\.com)/i,
		patterns: [
			/this content isn'?t available/i,
			/this content is not available/i,
			/이 콘텐츠는 사용할 수 없습니다/i,
			/learn more about power bi/i,
			/power bi에 대해 자세히 알아보세요/i,
			/you don'?t have access to this report/i,
			/해당 보고서를 볼 수 있는 권한이 없습니다/i,
			/게시자가 이 보고서를 삭제했습니다/i,
			/the report has been deleted/i,
			/report deleted/i
		]
	},
	{
		platform: 'Tableau Public',
		hostMatch: /tableau\.com/i,
		patterns: [
			/the workbook you are looking for is not available/i,
			/해당 통합 문서를 찾을 수 없습니다/i,
			/we could not find the page you were looking for/i,
			/workbook not found/i
		]
	},
	{
		platform: 'Looker Studio',
		hostMatch: /(lookerstudio|datastudio)\.google\.com/i,
		patterns: [
			/액세스 권한이 필요합니다/i,
			/request access/i,
			/you need access/i,
			/보고서가 삭제되었습니다/i,
			/report deleted/i,
			/this report has been deleted/i
		]
	},
	{
		platform: 'Streamlit',
		hostMatch: /streamlit\.(app|io)/i,
		patterns: [
			/this app is in the oven/i,
			/app is sleeping/i,
			/manage app/i,
			/please try again later/i,
			/you do not have access to this app or it does not exist/i,
			/not found · streamlit/i
		]
	},
	{
		platform: 'General',
		hostMatch: /.*/,
		patterns: [
			/\b404 Not Found\b/i,
			/\bPage Not Found\b/i,
			/페이지를 찾을 수 없습니다/i,
			/\b502 Bad Gateway\b/i,
			/\b503 Service Unavailable\b/i
		]
	}
];

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
		projectIds: [],
		includeHidden: false,
		directOnly: false
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
		} else if (arg === '--all' || arg === '--include-hidden') {
			options.includeHidden = true;
		} else if (arg === '--direct' || arg === '--probe-only') {
			options.directOnly = true;
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
// RLS 우회를 위해 SERVICE_ROLE_KEY가 있으면 우선 사용
const secretKey =
	process.env.SUPABASE_SERVICE_ROLE_KEY ||
	process.env.PUBLIC_SUPABASE_PUBLISHABLE_KEY ||
	process.env.SUPABASE_PUBLISHABLE_KEY ||
	process.env.SUPABASE_ANON_KEY;

if (!supabaseUrl || !secretKey) {
	console.error('❌ Supabase 환경 변수가 설정되지 않았습니다.');
	process.exit(1);
}

const supabase = createClient(supabaseUrl, secretKey, {
	auth: { autoRefreshToken: false, persistSession: false }
});

console.log('🔍 외부 링크 및 임베드 무결성 점검 프로그램');
console.log(`🌐 대상 모드: ${options.directOnly ? '외부 링크 직접 검증(Direct)' : `FOLIO 앱 + 외부 링크 검증 (${options.baseUrl})`}`);
if (options.includeHidden) console.log('👁️ 숨김(비공개) 프로젝트 포함 검사 활성화');
console.log('------------------------------------------------------------');

let query = supabase
	.from('projects')
	.select('id, title, platform_key, project_type, power_bi_url, status, embed_status, is_public')
	.not('power_bi_url', 'is', null)
	.order('created_at', { ascending: false });

if (options.projectIds.length > 0) {
	query = query.in('id', options.projectIds);
} else {
	if (!options.includeHidden) {
		query = query.eq('is_public', true);
	}
	query = query.eq('status', 'published');
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
	console.log('ℹ️ 점검 대상 조건에 맞는 프로젝트가 없습니다.');
	process.exit(0);
}

console.log(`📋 점검 대상 프로젝트: 총 ${projects.length}개\n`);
const artifactsDir = resolve(process.cwd(), 'artifacts', 'embed-checks');
if (options.screenshot) {
	mkdirSync(artifactsDir, { recursive: true });
}

// 로컬 서버 가용성 사전 확인 (directOnly가 아닐 때)
let localServerAvailable = false;
if (!options.directOnly) {
	try {
		const res = await fetch(options.baseUrl, { signal: AbortSignal.timeout(3000) });
		localServerAvailable = res.status < 500;
	} catch {
		localServerAvailable = false;
	}
	if (!localServerAvailable) {
		console.warn(`⚠️ 대상 로컬 서버(${options.baseUrl})에 연결할 수 없습니다.`);
		console.warn('   외부 임베드 링크 직접 검증 모드(Direct Probe)로 자동 전환합니다.\n');
	}
}

const browser = await chromium.launch({ headless: true });
const results = [];
let nextIndex = 0;
let completedCount = 0;

/**
 * 외부 임베드 URL의 실제 생사 여부를 브라우저 수준에서 심층 검증합니다.
 */
async function probeExternalUrl(url, page, timeoutMs) {
	try {
		const response = await page.goto(url, {
			waitUntil: 'domcontentloaded',
			timeout: Math.min(timeoutMs, 15000)
		});

		// HTTP 상태 코드 즉시 체크
		const status = response ? response.status() : null;
		if (status && status >= 400) {
			const pageTitle = await page.title().catch(() => '');
			return {
				isAvailable: false,
				status,
				reason: `HTTP ${status} 오류 반환 (${pageTitle || '페이지 없음'})`
			};
		}

		// 최대 5초간 500ms 간격으로 에러 시그니처 또는 성공 시각화 컨테이너 감지
		const maxWaitMs = Math.min(timeoutMs, 5000);
		for (let waited = 0; waited < maxWaitMs; waited += 500) {
			await page.waitForTimeout(500);

			const currentUrl = page.url();
			if (currentUrl.includes('accounts.google.com')) {
				return {
					isAvailable: false,
					status: 302,
					reason: '구글 로그인(비공개) 화면으로 리다이렉트됨'
				};
			}

			const bodyText = await page.evaluate(() => document.body?.innerText || '').catch(() => '');
			const pageTitle = await page.title().catch(() => '');

			// 외부 플랫폼별 에러 시그니처 검색
			for (const sig of ERROR_SIGNATURES) {
				if (sig.hostMatch.test(url) || sig.hostMatch.test(currentUrl)) {
					for (const pattern of sig.patterns) {
						if (pattern.test(bodyText) || pattern.test(pageTitle)) {
							const matched = pattern instanceof RegExp ? pattern.source : String(pattern);
							return {
								isAvailable: false,
								status: 200,
								reason: `외부 플랫폼 콘텐츠 오류 감지: "${matched}"`
							};
						}
					}
				}
			}

			// 정상 시각화 컨테이너가 로드된 경우 조기 성공 판정
			const hasVisuals = await page
				.evaluate(() => {
					return Boolean(
						document.querySelector(
							'.visual-container, .reportContainer, .canvas-container, .tab-viz, .tabZone, .stApp, .lego-reporting-view'
						)
					);
				})
				.catch(() => false);
			if (hasVisuals) {
				return {
					isAvailable: true,
					status: status || 200,
					title: pageTitle
				};
			}
		}

		const finalTitle = await page.title().catch(() => '');
		return {
			isAvailable: true,
			status: status || 200,
			title: finalTitle
		};
	} catch (err) {
		return {
			isAvailable: false,
			status: null,
			reason: `외부 URL 접속 실패 (${err.message})`
		};
	}
}

async function checkProject(project, page, index) {
	const result = {
		index: index + 1,
		id: project.id,
		title: project.title,
		isPublic: project.is_public,
		platform: project.platform_key,
		powerBiUrl: project.power_bi_url,
		trustedHost: false,
		httpProbeStatus: null,
		externalContentActive: null,
		iframeFound: false,
		iframeSrc: null,
		iframeRendered: false,
		cspViolations: [],
		consoleErrors: [],
		status: 'PENDING',
		error: null
	};

	let parsedUrl;
	try {
		parsedUrl = new URL(project.power_bi_url);
		result.trustedHost = isTrustedEmbedHost(parsedUrl.hostname);
		if (parsedUrl.hostname.includes('accounts.google.com')) {
			result.error = '구글 로그인 리다이렉트 URL이 등록됨 (continue 파라미터 확인 필요)';
			result.status = 'FAIL';
			return result;
		}
	} catch (e) {
		result.error = `유효하지 않은 URL: ${e.message}`;
		result.status = 'FAIL';
		return result;
	}

	// 1단계: 외부 임베드 URL 실제 렌더링 및 에러 시그니처 심층 검증
	const externalProbe = await probeExternalUrl(project.power_bi_url, page, options.timeoutMs);
	result.httpProbeStatus = externalProbe.status;
	result.externalContentActive = externalProbe.isAvailable;

	if (!externalProbe.isAvailable) {
		result.status = 'FAIL';
		result.error = externalProbe.reason;

		if (options.screenshot) {
			const shotPath = resolve(artifactsDir, `fail_${project.id}.png`);
			await page.screenshot({ path: shotPath, fullPage: false }).catch(() => {});
			result.screenshotPath = shotPath;
		}
		return result;
	}

	// 2단계: 로컬 서버가 사용 가능하고 directOnly가 아니며, 공개(is_public) 프로젝트인 경우 FOLIO 내 iframe 통합 및 CSP 검증
	if (localServerAvailable && !options.directOnly && project.is_public) {
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
			await page.waitForTimeout(1500);

			const evalResult = await page.evaluate(() => {
				const iframe = document.querySelector('iframe.dashboard-frame');
				const fallback = document.querySelector('.embed-empty.embed-external-state');
				const failed = document.querySelector('.embed-empty.embed-failed-state');
				const powerBIReport = document.querySelector('.powerbi-report');

				return {
					hasIframe: Boolean(iframe),
					iframeSrc: iframe ? iframe.getAttribute('src') : null,
					iframeWidth: iframe ? Math.round(iframe.getBoundingClientRect().width) : 0,
					iframeHeight: iframe ? Math.round(iframe.getBoundingClientRect().height) : 0,
					hasFallback: Boolean(fallback),
					hasFailed: Boolean(failed),
					failedText: failed ? failed.textContent?.trim() : null,
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
				result.error = '외부 사이트 열람 상태로 폴백됨 (신뢰 도메인 외 URL)';
			} else if (evalResult.hasFailed) {
				result.status = 'FAIL';
				result.error = evalResult.failedText || '임베드 게시 실패 상태';
			} else if (cspErrors.length > 0) {
				result.status = 'FAIL';
				result.error = `CSP 차단 발생: ${cspErrors.join(', ')}`;
			} else {
				result.status = 'WARN';
				result.error = 'FOLIO 상세 페이지에서 iframe 요소를 찾을 수 없거나 크기가 0입니다.';
			}

			if (options.screenshot) {
				const shotPath = resolve(artifactsDir, `${project.id}.png`);
				await page.screenshot({ path: shotPath, fullPage: false }).catch(() => {});
				result.screenshotPath = shotPath;
			}
		} catch (navErr) {
			result.status = 'FAIL';
			result.error = `FOLIO 상세 페이지 탐색 오류: ${navErr.message}`;
		} finally {
			page.off('console', consoleHandler);
		}
	} else {
		// 로컬 서버가 없거나 direct 모드이거나 숨김 프로젝트인 경우 외부 링크 직접 검증 결과로 판정
		result.status = 'PASS';
	}

	return result;
}

async function worker(workerId) {
	const context = await browser.newContext({
		viewport: { width: 1440, height: 900 },
		userAgent:
			'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
	});

	while (true) {
		const currentIndex = nextIndex++;
		if (currentIndex >= projects.length) break;
		const project = projects[currentIndex];

		const page = await context.newPage();
		let res;
		try {
			res = await checkProject(project, page, currentIndex);
		} finally {
			await page.close().catch(() => {});
		}
		results.push(res);
		completedCount++;

		const icon = res.status === 'PASS' ? '✅' : res.status === 'FAIL' ? '❌' : res.status === 'FALLBACK' ? 'ℹ️' : '⚠️';
		const titleDisplay = project.title ? project.title.slice(0, 30) : project.id;
		const hiddenTag = !project.is_public ? ' [숨김]' : '';
		console.log(`[${completedCount}/${projects.length}] ${icon}${hiddenTag} ${titleDisplay} (${res.status}${res.error ? `: ${res.error.slice(0, 45)}` : ''})`);
	}

	await context.close();
}

console.log(`🚀 동시 실행(Concurrency): ${options.concurrency}개 워커로 검사 시작...\n`);
const workerCount = Math.min(options.concurrency, projects.length);
await Promise.all(Array.from({ length: workerCount }, (_, id) => worker(id)));

await browser.close();

console.log('\n============================================================');
console.log('📊 외부 링크 및 임베드 무결성 점검 종합 결과');
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
	const hiddenTag = !r.isPublic ? ' [숨김]' : '';
	console.log(`${idx + 1}. [${icon}]${hiddenTag} ${r.title}`);
	console.log(`   - ID: ${r.id}`);
	console.log(`   - URL: ${r.powerBiUrl}`);
	if (r.error) console.log(`   - 사유: ${r.error}`);
});

console.log('------------------------------------------------------------');
console.log(`총 프로젝트: ${results.length} | 정상(PASS): ${passCount} | 실패(FAIL): ${failCount} | 폴백(FALLBACK): ${fallbackCount} | 경고(WARN): ${warnCount}`);

if (options.jsonOutput) {
	const outPath = resolve(process.cwd(), options.jsonOutput);
	writeFileSync(outPath, JSON.stringify(results, null, 2), 'utf8');
	console.log(`📁 JSON 보고서 저장 완료: ${outPath}`);
}

process.exit(failCount > 0 ? 1 : 0);
