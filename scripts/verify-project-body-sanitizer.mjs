import fs from 'node:fs';
import path from 'node:path';
import { chromium, expect } from '@playwright/test';
import { createClient } from '@supabase/supabase-js';

const projectId = process.env.PLAYWRIGHT_SANITIZER_PROJECT_ID?.trim();
const baseUrl = process.env.PLAYWRIGHT_BASE_URL?.trim() || 'http://127.0.0.1:5174';
const evidenceDir = path.resolve(process.cwd(), '..', 'artifacts', 'uiux-project-body-sanitizer-20260828');

if (!projectId) {
	throw new Error('PLAYWRIGHT_SANITIZER_PROJECT_ID가 필요합니다.');
}

function readEnvFile(filePath) {
	if (!fs.existsSync(filePath)) {
		return {};
	}
	return Object.fromEntries(
		fs
			.readFileSync(filePath, 'utf8')
			.split(/\r?\n/)
			.map((line) => line.match(/^\s*([^#=\s]+)\s*=\s*(.*)\s*$/))
			.filter(Boolean)
			.map(([, key, value]) => [key, value.trim().replace(/^['"]|['"]$/g, '')])
	);
}

const env = {
	...readEnvFile('../.env'),
	...readEnvFile('.env')
};
const admin = createClient(env.SUPABASE_URL, env.SUPABASE_SERVICE_ROLE_KEY);
const contentColumns = 'problem,dataset,process,insights';
const snapshotResult = await admin.from('projects').select(contentColumns).eq('id', projectId).single();

if (snapshotResult.error || !snapshotResult.data) {
	throw new Error(`본문 snapshot 실패: ${snapshotResult.error?.message || '프로젝트 없음'}`);
}

const original = snapshotResult.data;
const safeHref = 'https://example.com/safe';
const safeImage = 'https://example.com/safe-chart.png';
const maliciousBody = `<p><a href="javascript:alert(1)">위험 링크</a> <a href="${safeHref}">정상 링크</a> <span style="color:#1459c8">안전 색상</span> <span style="color:expression(alert(1));background-image:url(javascript:bad)">위험 style</span><img src="javascript:alert(1)" alt="위험 이미지"><img src="${safeImage}" alt="정상 이미지"><span data-type="inline-math" data-latex="x^2 + y^2 = z^2"></span></p><script>window.__sanitizerShouldNotRun = true;</script>`;
const injected = { ...original, problem: maliciousBody };
const detailPath = `/projects/${projectId}`;

async function verifyViewport(name, width, height) {
	const browser = await chromium.launch({ headless: true });
	const page = await browser.newPage({
		viewport: { width, height },
		isMobile: name === 'mobile',
		locale: 'ko-KR'
	});

	try {
		await page.goto(`${baseUrl}${detailPath}`, { waitUntil: 'domcontentloaded' });
		await page.locator('#project-report').waitFor({ state: 'visible', timeout: 15_000 });
		const report = page.locator('#project-report');
		const metrics = await report.evaluate((element) => ({
			anchors: [...element.querySelectorAll('a')].map((node) => ({
				text: node.textContent?.trim(),
				href: node.getAttribute('href'),
				target: node.getAttribute('target'),
				rel: node.getAttribute('rel')
			})),
			colorStyle: element.querySelector('span')?.getAttribute('style') ?? null,
			unsafeStyleCount: [...element.querySelectorAll('[style]')].filter((node) => /expression|javascript:|background-image/i.test(node.getAttribute('style') ?? '')).length,
			images: [...element.querySelectorAll('img')].map((node) => ({ src: node.getAttribute('src'), alt: node.getAttribute('alt') })),
			math: [...element.querySelectorAll('[data-type="inline-math"], [data-type="block-math"]')].map((node) => ({ type: node.getAttribute('data-type'), latex: node.getAttribute('data-latex') })),
			scriptCount: element.querySelectorAll('script').length,
			sanitizerFlag: Boolean(window.__sanitizerShouldNotRun),
			bodyText: element.textContent?.trim() ?? ''
		}));

		const dangerousAnchor = metrics.anchors.find((anchor) => anchor.text === '위험 링크');
		const safeAnchor = metrics.anchors.find((anchor) => anchor.text === '정상 링크');
		const passed =
			dangerousAnchor?.href === null &&
			safeAnchor?.href === safeHref &&
			safeAnchor.target === '_blank' &&
			safeAnchor.rel === 'noreferrer' &&
			metrics.colorStyle === 'color: #1459c8' &&
			metrics.unsafeStyleCount === 0 &&
			metrics.images.length === 1 &&
			metrics.images[0].src === safeImage &&
			metrics.images[0].alt === '정상 이미지' &&
			metrics.math.length === 1 &&
			metrics.math[0].latex === 'x^2 + y^2 = z^2' &&
			metrics.scriptCount === 0 &&
			!metrics.sanitizerFlag;
		const evidence = { viewport: name, passed, ...metrics };

		if (!passed) {
			throw new Error(`sanitizer 검증 실패: ${JSON.stringify(evidence)}`);
		}

		fs.mkdirSync(evidenceDir, { recursive: true });
		await page.screenshot({ path: path.join(evidenceDir, `${name}-sanitizer.png`), fullPage: true });
		fs.writeFileSync(path.join(evidenceDir, `${name}-metrics.json`), JSON.stringify(evidence, null, 2), 'utf8');
		return evidence;
	} finally {
		await browser.close();
	}
}

try {
	const updateResult = await admin.from('projects').update(injected).eq('id', projectId);
	if (updateResult.error) {
		throw new Error(`악성 HTML 주입 실패: ${updateResult.error.message}`);
	}

	const results = [];
	for (const [name, width, height] of [
		['desktop', 1440, 1000],
		['mobile', 390, 844]
	]) {
		results.push(await verifyViewport(name, width, height));
	}
	console.log(JSON.stringify(results));
} finally {
	const restoreResult = await admin.from('projects').update(original).eq('id', projectId);
	if (restoreResult.error) {
		throw new Error(`본문 최종 원복 실패: ${restoreResult.error.message}`);
	}
}
