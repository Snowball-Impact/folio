import { chromium } from '@playwright/test';

const baseUrl = (process.env.PLAYWRIGHT_BASE_URL || 'http://127.0.0.1:5174').replace(/\/$/, '');
const routes = (process.env.MEASURE_ROUTES || '/,/about,/policy/privacy,/powerbi,/references/powerbi,/submit')
	.split(',')
	.map((route) => route.trim())
	.filter(Boolean);
const waitUntil = process.env.MEASURE_WAIT_UNTIL || 'networkidle';
const settleMs = Number(process.env.MEASURE_SETTLE_MS || 0);
const sampleDurationMs = Number(process.env.MEASURE_SAMPLE_MS || 4000);
const sampleIntervalMs = Number(process.env.MEASURE_SAMPLE_INTERVAL_MS || 200);
const includeTransitions = process.env.MEASURE_TRANSITIONS === '1';
const browser = await chromium.launch({ headless: true });

const milestoneSelectors = {
	header: ['.site-header', 'header'],
	hero: ['.hero', '.home-hero-slide', '.powerbi-hero', '.detail-hero', '.auth-card', '.policy-page-hero'],
	browsePanel: ['.home-browse-panel'],
	projectRail: ['.project-rail-section'],
	projectCard: ['.project-card'],
	visualPanel: ['.visual-panel', '.powerbi-shell', '.dashboard-frame'],
	report: ['.report'],
	comments: ['.comments-panel'],
	emptyPanel: ['.empty-panel'],
	form: ['form', '.project-form', '.auth-form']
};

try {
	for (const route of routes) {
		const context = await browser.newContext();
		const page = await context.newPage();
		try {
			await installPerformanceObservers(page);
			const startedAt = Date.now();
			const response = await page.goto(`${baseUrl}${route}`, { waitUntil: 'commit', timeout: 30_000 });
			const loadStatePromise =
				waitUntil === 'commit'
					? Promise.resolve()
					: page.waitForLoadState(waitUntil, { timeout: 30_000 }).catch(() => {});
			const milestones = await collectMilestones(page, startedAt);
			await loadStatePromise;
			if (settleMs > 0) {
				await page.waitForTimeout(settleMs);
			}
			const metrics = await collectRouteMetrics(page);
			const frameMetrics = await collectFrameMetrics(page);
			console.log(JSON.stringify({ route, status: response?.status() ?? null, milestones, ...metrics, frameMetrics }));
		} catch (error) {
			console.error(JSON.stringify({ route, error: error instanceof Error ? error.message : String(error) }));
			process.exitCode = 1;
		} finally {
			await page.close();
			await context.close();
		}
	}

	if (includeTransitions) {
		const transitionContext = await browser.newContext();
		const transitionPage = await transitionContext.newPage();
		try {
			const transitions = await measureTransitions(transitionPage);
			for (const result of transitions) {
				console.log(JSON.stringify(result));
			}
		} catch (error) {
			console.error(JSON.stringify({ kind: 'transition', error: error instanceof Error ? error.message : String(error) }));
			process.exitCode = 1;
		} finally {
			await transitionPage.close();
			await transitionContext.close();
		}
	}
} finally {
	await browser.close();
}

async function installPerformanceObservers(page) {
	await page.addInitScript(() => {
		const webVitals = { lcp: null, cls: 0, inp: null };
		window.__folioWebVitals = webVitals;
		try {
			new PerformanceObserver((list) => {
				const entries = list.getEntries();
				const latest = entries[entries.length - 1];
				webVitals.lcp = latest?.renderTime || latest?.loadTime || latest?.startTime || null;
			}).observe({ type: 'largest-contentful-paint', buffered: true });
		} catch {}
		try {
			new PerformanceObserver((list) => {
				for (const entry of list.getEntries()) {
					if (!entry.hadRecentInput) webVitals.cls += entry.value;
				}
			}).observe({ type: 'layout-shift', buffered: true });
		} catch {}
		try {
			new PerformanceObserver((list) => {
				for (const entry of list.getEntries()) {
					if (entry.interactionId && (!webVitals.inp || entry.duration > webVitals.inp)) {
						webVitals.inp = entry.duration;
					}
				}
			}).observe({ type: 'event', buffered: true, durationThreshold: 40 });
		} catch {}
	});
}

async function collectMilestones(page, startedAt) {
	const milestones = {};
	const deadline = Date.now() + sampleDurationMs;
	while (Date.now() <= deadline) {
		const sample = await page.evaluate((selectors) => {
			function visible(selector) {
				return Array.from(document.querySelectorAll(selector)).some((element) => {
					const rect = element.getBoundingClientRect();
					const style = window.getComputedStyle(element);
					return rect.width > 1 && rect.height > 1 && style.display !== 'none' && style.visibility !== 'hidden';
				});
			}
			return Object.fromEntries(
				Object.entries(selectors).map(([name, candidates]) => [name, candidates.some((selector) => visible(selector))])
			);
		}, milestoneSelectors);
		for (const [name, reached] of Object.entries(sample)) {
			if (reached && milestones[name] === undefined) {
				milestones[name] = Date.now() - startedAt;
			}
		}
		if (Object.keys(milestones).length >= 3 && (await documentReady(page))) {
			break;
		}
		await page.waitForTimeout(sampleIntervalMs);
	}
	return milestones;
}

async function documentReady(page) {
	try {
		return await page.evaluate(() => document.readyState === 'complete');
	} catch {
		return false;
	}
}

async function collectRouteMetrics(page) {
	return page.evaluate(() => {
		const navigation = performance.getEntriesByType('navigation')[0];
		const resources = performance.getEntriesByType('resource');
		const resourceSummary = resources.reduce(
			(summary, resource) => {
				const size = resource.transferSize || resource.encodedBodySize || 0;
				const pathname = new URL(resource.name).pathname;
				const isJavaScript = resource.initiatorType === 'script' || pathname.endsWith('.js');
				const isStylesheet = resource.initiatorType === 'link' || pathname.endsWith('.css');
				if (isJavaScript) summary.jsBytes += size;
				if (isStylesheet) summary.cssBytes += size;
				summary.totalBytes += size;
				summary.count += 1;
				return summary;
			},
			{ count: 0, totalBytes: 0, jsBytes: 0, cssBytes: 0 }
		);
		const main = document.querySelector('main') || document.body;
		const mainRect = main.getBoundingClientRect();
		const bodyWidth = document.body.scrollWidth;
		const viewportWidth = window.innerWidth;
		return {
			url: window.location.pathname,
			title: document.title,
			resourceSummary,
			navigation: navigation
				? {
						domContentLoaded: Math.round(navigation.domContentLoadedEventEnd),
						load: Math.round(navigation.loadEventEnd),
						responseEnd: Math.round(navigation.responseEnd),
						transferSize: navigation.transferSize || navigation.encodedBodySize || 0
					}
				: null,
			webVitals: {
				lcp: window.__folioWebVitals?.lcp ? Math.round(window.__folioWebVitals.lcp) : null,
				cls: Number((window.__folioWebVitals?.cls || 0).toFixed(4)),
				inp: window.__folioWebVitals?.inp ? Math.round(window.__folioWebVitals.inp) : null
			},
			layout: {
				viewportWidth,
				bodyWidth,
				horizontalOverflow: Math.max(0, bodyWidth - viewportWidth),
				documentHeight: Math.max(document.body.scrollHeight, document.documentElement.scrollHeight),
				mainHeight: Math.round(mainRect.height)
			},
			elements: Object.fromEntries(
				Object.entries({
					forms: 'form',
					iframes: 'iframe',
					projectCards: '.project-card',
					emptyPanels: '.empty-panel',
					buttons: 'button',
					inputs: 'input, select, textarea'
				}).map(([name, selector]) => [name, document.querySelectorAll(selector).length])
			),
			performanceMeasures: performance
				.getEntriesByType('measure')
				.filter((entry) => entry.name.startsWith('folio-powerbi-'))
				.map((entry) => ({ name: entry.name, duration: Math.round(entry.duration) })),
			longTasks: performance.getEntriesByType('longtask').length,
			iframes: [...document.querySelectorAll('iframe')].map((iframe) => ({
				src: iframe.src,
				title: iframe.title,
				width: iframe.clientWidth,
				height: iframe.clientHeight
			}))
		};
	});
}

async function collectFrameMetrics(page) {
	const frameMetrics = [];
	for (const frame of page.frames()) {
		if (frame === page.mainFrame()) continue;
		try {
			const frameMetric = await frame.evaluate(() => {
				const resources = performance.getEntriesByType('resource');
				return {
					resourceCount: resources.length,
					resourceBytes: resources.reduce(
						(total, resource) => total + (resource.transferSize || resource.encodedBodySize || 0),
						0
					),
					title: document.title
				};
			});
			frameMetrics.push({ url: frame.url(), ...frameMetric });
		} catch (error) {
			frameMetrics.push({ url: frame.url(), error: error instanceof Error ? error.message : String(error) });
		}
	}
	return frameMetrics;
}

async function measureTransitions(page) {
	await installPerformanceObservers(page);
	await page.goto(`${baseUrl}/`, { waitUntil: 'commit', timeout: 30_000 });
	if (waitUntil !== 'commit') {
		await page.waitForLoadState(waitUntil, { timeout: 30_000 }).catch(() => {});
	}
	return [
		await measureTransition(page, 'home-search-submit', async () => {
			const search = page.locator("input[type='search']").first();
			if ((await search.count()) === 0) return false;
			await search.fill('powerbi');
			await page.locator('.home-search-row button').first().click();
			return true;
		}),
		await measureTransition(page, 'home-to-login', async () => {
			const login = page.locator('a[href="/login"]').first();
			if ((await login.count()) === 0) return false;
			await login.click();
			return true;
		})
	];
}

async function measureTransition(page, name, action) {
	await page.evaluate(() => {
		window.__folioWebVitals ??= { lcp: null, cls: 0, inp: null };
		window.__folioWebVitals.lcp = null;
		window.__folioWebVitals.cls = 0;
		window.__folioWebVitals.inp = null;
	});
	const clicked = await action();
	await page.waitForTimeout(Math.max(1000, Math.min(sampleDurationMs, 3000)));
	const metrics = await collectRouteMetrics(page);
	return {
		kind: 'transition',
		name,
		clicked,
		url: metrics.url,
		webVitals: metrics.webVitals,
		layout: metrics.layout
	};
}
