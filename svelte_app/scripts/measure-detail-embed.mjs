import { chromium } from '@playwright/test';
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';

const baseUrl = process.env.PLAYWRIGHT_BASE_URL ?? 'http://127.0.0.1:5174';
const outDir = resolve(process.cwd(), '..', 'artifacts', 'playwright', 'embed-comparison');
const projects = process.argv.slice(2);

function loadDotEnv(path) {
	if (!existsSync(path)) {
		return;
	}
	for (const line of readFileSync(path, 'utf8').split(/\r?\n/)) {
		const match = line.match(/^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)\s*$/);
		if (!match || process.env[match[1]]) {
			continue;
		}
		let value = match[2].trim();
		if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith("'") && value.endsWith("'"))) {
			value = value.slice(1, -1);
		}
		process.env[match[1]] = value;
	}
}

if (projects.length === 0) {
	throw new Error('Pass one or more project ids.');
}

mkdirSync(outDir, { recursive: true });
loadDotEnv(resolve(process.cwd(), '.env'));
loadDotEnv(resolve(process.cwd(), '..', '.env'));

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1280, height: 900 }, deviceScaleFactor: 1 });
const results = [];
const email = process.env.test_id ?? process.env.FOLIO_TEST_ID;
const password = process.env.test_pw ?? process.env.FOLIO_TEST_PW;

try {
	if (email && password) {
		await page.goto(new URL('/login', baseUrl).toString(), { waitUntil: 'networkidle' });
		await page.locator('input[type="email"]').fill(email);
		await page.locator('input[type="password"]').fill(password);
		await page.getByRole('button', { name: '로그인' }).click();
		await page.waitForURL((url) => !url.pathname.startsWith('/login'), { timeout: 15_000 }).catch(() => {});
	}

	for (const projectId of projects) {
		await page.goto(new URL(`/projects/${projectId}`, baseUrl).toString(), { waitUntil: 'domcontentloaded' });
		await page.waitForTimeout(5000);
		const metrics = await page.evaluate(() => {
			function box(selector) {
				const element = document.querySelector(selector);
				if (!element) {
					return null;
				}
				const rect = element.getBoundingClientRect();
				const style = getComputedStyle(element);
				return {
					width: Math.round(rect.width),
					height: Math.round(rect.height),
					top: Math.round(rect.top),
					left: Math.round(rect.left),
					display: style.display,
					minHeight: style.minHeight,
					aspectRatio: style.aspectRatio,
					overflow: style.overflow
				};
			}
			return {
				title: document.querySelector('h1')?.textContent?.trim() ?? '',
				powerBIStatus: document.querySelector('.powerbi-shell')?.getAttribute('data-powerbi-status') ?? null,
				visualPanel: box('#project-output'),
				powerBIShell: box('.powerbi-shell'),
				powerBIReport: box('.powerbi-report'),
				dashboardFrame: box('.dashboard-frame'),
				iframes: [...document.querySelectorAll('iframe')].map((frame) => {
					const rect = frame.getBoundingClientRect();
					return {
						title: frame.title,
						srcHost: (() => {
							try {
								return new URL(frame.src).host;
							} catch {
								return '';
							}
						})(),
						width: Math.round(rect.width),
						height: Math.round(rect.height),
						top: Math.round(rect.top),
						left: Math.round(rect.left)
					};
				}),
				resourceActions: [...document.querySelectorAll('.visual-panel > .actions .button-link')].map((node) => ({
					text: node.textContent?.replace(/\s+/g, ' ').trim() ?? '',
					tag: node.tagName.toLowerCase(),
					disabled: node.hasAttribute('disabled') || node.getAttribute('aria-disabled') === 'true'
				}))
			};
		});
		await page.screenshot({ path: resolve(outDir, `${projectId}.png`), fullPage: true });
		results.push({ projectId, ...metrics });
	}
} finally {
	await browser.close();
}

writeFileSync(resolve(outDir, 'metrics.json'), JSON.stringify(results, null, 2), 'utf8');
console.log(JSON.stringify(results, null, 2));
