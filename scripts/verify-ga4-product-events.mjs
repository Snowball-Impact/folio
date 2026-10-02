import { chromium } from '@playwright/test';
import { readFileSync } from 'node:fs';

const baseUrl = new URL(process.argv[2] || 'https://folio.it.kr');
const testEnv = loadTestEnv();
const browser = await chromium.launch({ headless: true });

try {
	const firstContext = await browser.newContext({ permissions: ['clipboard-read', 'clipboard-write'] });
	const firstPage = await firstContext.newPage();
	await firstPage.goto(baseUrl.href, { waitUntil: 'domcontentloaded' });
	const projectHref = await firstPage.locator('a[href^="/projects/"]').first().getAttribute('href');
	if (!projectHref) {
		throw new Error('No public project link was found.');
	}

	const projectUrl = new URL(projectHref, baseUrl);
	await firstPage.goto(projectUrl.href, { waitUntil: 'domcontentloaded' });
	await firstPage.locator('.detail-hero').waitFor();
	await waitForAnalyticsEvent(firstPage, 'view_item');
	await firstPage.getByRole('button', { name: '공유 링크 복사' }).click();
	await waitForAnalyticsEvent(firstPage, 'share');
	const relatedCard = firstPage.locator('.project-rail-section .project-card').first();
	await relatedCard.waitFor();
	await relatedCard.click({ modifiers: ['Control'] });
	await waitForAnalyticsEvent(firstPage, 'related_project_click');
	const detailEvents = await analyticsEvents(firstPage);

	const sharedUrl = new URL(projectUrl);
	sharedUrl.searchParams.set('utm_source', 'folio');
	sharedUrl.searchParams.set('utm_medium', 'share');
	sharedUrl.searchParams.set('utm_campaign', 'project_share');
	const sharedContext = await browser.newContext();
	const sharedPage = await sharedContext.newPage();
	await sharedPage.goto(sharedUrl.href, { waitUntil: 'domcontentloaded' });
	await sharedPage.locator('.detail-hero').waitFor();
	await waitForAnalyticsEvent(sharedPage, 'project_share_open');
	const sharedEvents = await analyticsEvents(sharedPage);

	assertEvent(detailEvents, 'view_item');
	assertEvent(detailEvents, 'share');
	assertEvent(detailEvents, 'related_project_click');
	assertEvent(sharedEvents, 'view_item');
	assertEvent(sharedEvents, 'project_share_open');

	let loginEvents = [];
	if (testEnv.email && testEnv.password) {
		const loginContext = await browser.newContext();
		const loginPage = await loginContext.newPage();
		await loginPage.goto(new URL('/login?next=/my', baseUrl).href, { waitUntil: 'domcontentloaded' });
		await waitForAnalyticsEvent(loginPage, 'page_view');
		await loginPage.locator('input[type="email"]').fill(testEnv.email);
		await loginPage.locator('input[type="password"]').fill(testEnv.password);
		await loginPage.getByRole('button', { name: '로그인', exact: true }).click();
		await loginPage.waitForURL((url) => url.pathname === '/my', { timeout: 20_000 });
		await waitForAnalyticsEvent(loginPage, 'login');
		loginEvents = await analyticsEvents(loginPage);
		assertEvent(loginEvents, 'login');
		await loginContext.close();
	}

	console.log(JSON.stringify({
		project: projectUrl.pathname,
		detailEvents,
		sharedEvents,
		loginEvents,
		loginChecked: Boolean(testEnv.email && testEnv.password)
	}, null, 2));

	await firstContext.close();
	await sharedContext.close();
} finally {
	await browser.close();
}

async function analyticsEvents(page) {
	return page.evaluate(() =>
		(window.dataLayer ?? [])
			.map((entry) => Array.from(entry))
			.filter((entry) => entry[0] === 'event')
			.map((entry) => ({ name: entry[1], params: entry[2] ?? {} }))
	);
}

async function waitForAnalyticsEvent(page, name) {
	await page.waitForFunction(
		(expectedName) => (window.dataLayer ?? []).some((entry) => Array.from(entry)[0] === 'event' && Array.from(entry)[1] === expectedName),
		name,
		{ timeout: 15_000 }
	);
}

function assertEvent(events, name) {
	if (!events.some((event) => event.name === name)) {
		throw new Error(`Expected GA4 event was not queued: ${name}`);
	}
}

function loadTestEnv() {
	let values = {};
	try {
		for (const line of readFileSync('.env', 'utf8').split(/\r?\n/)) {
			const match = line.match(/^\s*([^#=]+?)\s*=\s*(.*)\s*$/);
			if (!match) continue;
			values[match[1]] = match[2].replace(/^['"]|['"]$/g, '');
		}
	} catch {
		// Public event checks remain available without a local test account.
	}
	return {
		email: process.env.FOLIO_TEST_ID || process.env.test_id || values.FOLIO_TEST_ID || values.test_id || '',
		password: process.env.FOLIO_TEST_PW || process.env.test_pw || values.FOLIO_TEST_PW || values.test_pw || ''
	};
}
