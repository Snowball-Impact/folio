import { writeFile } from 'node:fs/promises';
import { expect, test } from '@playwright/test';
import { testEnv } from './test-env';

const focusRoutes = [
	{ name: 'home', path: '/' },
	{ name: 'my-page', path: '/my' },
	{ name: 'notifications', path: '/notifications' },
	{ name: 'submit', path: '/submit' }
];

const publicDetailProjectId = testEnv('PLAYWRIGHT_PUBLIC_DETAIL_PROJECT_ID', 'PLAYWRIGHT_PROJECT_ID');

for (const route of focusRoutes) {
	test(`${route.name} renders a capture-ready page`, async ({ page }, testInfo) => {
		const response = await page.goto(route.path, { waitUntil: 'domcontentloaded' });

		expect(response, `${route.path} did not return a document`).not.toBeNull();
		expect(response?.status(), `${route.path} returned a server error`).toBeLessThan(500);
		await expect(page.locator('body')).toBeVisible();
		await page.waitForTimeout(250);

		const metrics = await page.evaluate(() => {
			const body = document.body;
			const documentElement = document.documentElement;
			const selectors = {
				header: '.site-header',
				hero: '.hero, .home-hero-shell, .page-image-hero, .my-hero, .notification-hero, .submit-hero',
				projectCard: '.project-card',
				form: 'form',
				iframe: 'iframe',
				buttons: 'button',
				links: 'a',
				inputs: 'input, textarea, [contenteditable="true"]',
				alerts: '[role="alert"]'
			} as const;

			return {
				title: document.title,
				h1: [...document.querySelectorAll('h1')].map((node) => node.textContent?.trim()).filter(Boolean),
				scroll: {
					width: documentElement.scrollWidth,
					clientWidth: documentElement.clientWidth,
					height: Math.max(documentElement.scrollHeight, body.scrollHeight),
					viewportWidth: window.innerWidth,
					viewportHeight: window.innerHeight
				},
				counts: Object.fromEntries(
					Object.entries(selectors).map(([name, selector]) => [name, document.querySelectorAll(selector).length])
				),
				iframeSources: [...document.querySelectorAll('iframe')]
					.map((frame) => frame.getAttribute('src'))
					.filter(Boolean)
			};
		});

		expect(metrics.scroll.width - metrics.scroll.clientWidth).toBeLessThanOrEqual(3);
		expect(metrics.h1.length, `${route.path} should expose a page heading`).toBeGreaterThan(0);

		const metricsPath = testInfo.outputPath('page-metrics.json');
		await writeFile(metricsPath, JSON.stringify({ route: route.path, ...metrics }, null, 2), 'utf8');
		await testInfo.attach('page-metrics.json', {
			path: metricsPath,
			contentType: 'application/json'
		});
		await page.screenshot({ path: testInfo.outputPath(`${route.name}.png`), fullPage: true });
	});
}

test('public detail fixture renders anonymous state', async ({ page }, testInfo) => {
	test.skip(!publicDetailProjectId, 'PLAYWRIGHT_PUBLIC_DETAIL_PROJECT_ID 또는 PLAYWRIGHT_PROJECT_ID가 필요합니다.');
	const response = await page.goto(`/projects/${publicDetailProjectId}`, { waitUntil: 'domcontentloaded' });
	expect(response, 'public detail did not return a document').not.toBeNull();
	expect(response?.status(), 'public detail returned a server error').toBeLessThan(500);
	await expect(page.locator('.detail-hero')).toBeVisible({ timeout: 15_000 });
	await expect(page.locator('#project-output')).toBeVisible({ timeout: 15_000 });
	await expect(page.locator('#project-comments')).toBeVisible({ timeout: 15_000 });
	const metrics = await page.evaluate(() => ({
		title: document.title,
		h1: [...document.querySelectorAll('h1')].map((node) => node.textContent?.trim()).filter(Boolean),
		iframes: document.querySelectorAll('iframe').length,
		comments: document.querySelectorAll('.comment-card').length,
		scrollWidth: document.documentElement.scrollWidth,
		clientWidth: document.documentElement.clientWidth
	}));
	expect(metrics.scrollWidth - metrics.clientWidth).toBeLessThanOrEqual(3);
	const metricsPath = testInfo.outputPath('public-detail-metrics.json');
	await writeFile(metricsPath, JSON.stringify({ projectId: publicDetailProjectId, ...metrics }, null, 2), 'utf8');
	await testInfo.attach('public-detail-metrics.json', { path: metricsPath, contentType: 'application/json' });
	await page.screenshot({ path: testInfo.outputPath('public-detail.png'), fullPage: true });
});
