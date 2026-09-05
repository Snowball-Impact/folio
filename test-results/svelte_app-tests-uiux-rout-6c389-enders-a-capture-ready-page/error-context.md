# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: svelte_app\tests\uiux\routes.spec.ts >> notifications renders a capture-ready page
- Location: svelte_app\tests\uiux\routes.spec.ts:15:2

# Error details

```
Error: page.goto: Protocol error (Page.navigate): Cannot navigate to invalid URL
Call log:
  - navigating to "/notifications", waiting until "domcontentloaded"

```

# Test source

```ts
  1  | import { writeFile } from 'node:fs/promises';
  2  | import { expect, test } from '@playwright/test';
  3  | import { testEnv } from './test-env';
  4  | 
  5  | const focusRoutes = [
  6  | 	{ name: 'home', path: '/' },
  7  | 	{ name: 'my-page', path: '/my' },
  8  | 	{ name: 'notifications', path: '/notifications' },
  9  | 	{ name: 'submit', path: '/submit' }
  10 | ];
  11 | 
  12 | const publicDetailProjectId = testEnv('PLAYWRIGHT_PUBLIC_DETAIL_PROJECT_ID', 'PLAYWRIGHT_PROJECT_ID');
  13 | 
  14 | for (const route of focusRoutes) {
  15 | 	test(`${route.name} renders a capture-ready page`, async ({ page }, testInfo) => {
> 16 | 		const response = await page.goto(route.path, { waitUntil: 'domcontentloaded' });
     |                               ^ Error: page.goto: Protocol error (Page.navigate): Cannot navigate to invalid URL
  17 | 
  18 | 		expect(response, `${route.path} did not return a document`).not.toBeNull();
  19 | 		expect(response?.status(), `${route.path} returned a server error`).toBeLessThan(500);
  20 | 		await expect(page.locator('body')).toBeVisible();
  21 | 		await page.waitForTimeout(250);
  22 | 
  23 | 		const metrics = await page.evaluate(() => {
  24 | 			const body = document.body;
  25 | 			const documentElement = document.documentElement;
  26 | 			const selectors = {
  27 | 				header: '.site-header',
  28 | 				hero: '.hero, .home-hero-shell, .page-image-hero, .my-hero, .notification-hero, .submit-hero',
  29 | 				projectCard: '.project-card',
  30 | 				form: 'form',
  31 | 				iframe: 'iframe',
  32 | 				buttons: 'button',
  33 | 				links: 'a',
  34 | 				inputs: 'input, textarea, [contenteditable="true"]',
  35 | 				alerts: '[role="alert"]'
  36 | 			} as const;
  37 | 
  38 | 			return {
  39 | 				title: document.title,
  40 | 				h1: [...document.querySelectorAll('h1')].map((node) => node.textContent?.trim()).filter(Boolean),
  41 | 				scroll: {
  42 | 					width: documentElement.scrollWidth,
  43 | 					clientWidth: documentElement.clientWidth,
  44 | 					height: Math.max(documentElement.scrollHeight, body.scrollHeight),
  45 | 					viewportWidth: window.innerWidth,
  46 | 					viewportHeight: window.innerHeight
  47 | 				},
  48 | 				counts: Object.fromEntries(
  49 | 					Object.entries(selectors).map(([name, selector]) => [name, document.querySelectorAll(selector).length])
  50 | 				),
  51 | 				iframeSources: [...document.querySelectorAll('iframe')]
  52 | 					.map((frame) => frame.getAttribute('src'))
  53 | 					.filter(Boolean)
  54 | 			};
  55 | 		});
  56 | 
  57 | 		expect(metrics.scroll.width - metrics.scroll.clientWidth).toBeLessThanOrEqual(3);
  58 | 		expect(metrics.h1.length, `${route.path} should expose a page heading`).toBeGreaterThan(0);
  59 | 
  60 | 		const metricsPath = testInfo.outputPath('page-metrics.json');
  61 | 		await writeFile(metricsPath, JSON.stringify({ route: route.path, ...metrics }, null, 2), 'utf8');
  62 | 		await testInfo.attach('page-metrics.json', {
  63 | 			path: metricsPath,
  64 | 			contentType: 'application/json'
  65 | 		});
  66 | 		await page.screenshot({ path: testInfo.outputPath(`${route.name}.png`), fullPage: true });
  67 | 	});
  68 | }
  69 | 
  70 | test('public detail fixture renders anonymous state', async ({ page }, testInfo) => {
  71 | 	test.skip(!publicDetailProjectId, 'PLAYWRIGHT_PUBLIC_DETAIL_PROJECT_ID 또는 PLAYWRIGHT_PROJECT_ID가 필요합니다.');
  72 | 	const response = await page.goto(`/projects/${publicDetailProjectId}`, { waitUntil: 'domcontentloaded' });
  73 | 	expect(response, 'public detail did not return a document').not.toBeNull();
  74 | 	expect(response?.status(), 'public detail returned a server error').toBeLessThan(500);
  75 | 	await expect(page.locator('.detail-hero')).toBeVisible({ timeout: 15_000 });
  76 | 	await expect(page.locator('#project-output')).toBeVisible({ timeout: 15_000 });
  77 | 	await expect(page.locator('#project-comments')).toBeVisible({ timeout: 15_000 });
  78 | 	const metrics = await page.evaluate(() => ({
  79 | 		title: document.title,
  80 | 		h1: [...document.querySelectorAll('h1')].map((node) => node.textContent?.trim()).filter(Boolean),
  81 | 		iframes: document.querySelectorAll('iframe').length,
  82 | 		comments: document.querySelectorAll('.comment-card').length,
  83 | 		scrollWidth: document.documentElement.scrollWidth,
  84 | 		clientWidth: document.documentElement.clientWidth
  85 | 	}));
  86 | 	expect(metrics.scrollWidth - metrics.clientWidth).toBeLessThanOrEqual(3);
  87 | 	const metricsPath = testInfo.outputPath('public-detail-metrics.json');
  88 | 	await writeFile(metricsPath, JSON.stringify({ projectId: publicDetailProjectId, ...metrics }, null, 2), 'utf8');
  89 | 	await testInfo.attach('public-detail-metrics.json', { path: metricsPath, contentType: 'application/json' });
  90 | 	await page.screenshot({ path: testInfo.outputPath('public-detail.png'), fullPage: true });
  91 | });
  92 | 
```