import { chromium } from '@playwright/test';

const baseUrl = (process.env.PLAYWRIGHT_BASE_URL || 'http://127.0.0.1:5174').replace(/\/$/, '');
const routes = (process.env.MEASURE_ROUTES || '/,/about,/policy/privacy,/powerbi,/references/powerbi,/submit')
	.split(',')
	.map((route) => route.trim())
	.filter(Boolean);
const waitUntil = process.env.MEASURE_WAIT_UNTIL || 'networkidle';
const settleMs = Number(process.env.MEASURE_SETTLE_MS || 0);
const browser = await chromium.launch({ headless: true });

try {
	for (const route of routes) {
		const context = await browser.newContext();
		const page = await context.newPage();
		try {
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
			const response = await page.goto(`${baseUrl}${route}`, { waitUntil, timeout: 30_000 });
			if (settleMs > 0) {
				await page.waitForTimeout(settleMs);
			}
			const metrics = await page.evaluate(() => {
				const navigation = performance.getEntriesByType('navigation')[0];
				const resources = performance.getEntriesByType('resource');
				const resourceSummary = resources.reduce(
					(summary, resource) => {
						const entry = resource;
						const size = entry.transferSize || entry.encodedBodySize || 0;
						const pathname = new URL(entry.name).pathname;
						const isJavaScript = entry.initiatorType === 'script' || pathname.endsWith('.js');
						const isStylesheet =
							entry.initiatorType === 'link' || pathname.endsWith('.css');
						if (isJavaScript) {
							summary.jsBytes += size;
						}
						if (isStylesheet) {
							summary.cssBytes += size;
						}
						summary.totalBytes += size;
						summary.count += 1;
						return summary;
					},
					{ count: 0, totalBytes: 0, jsBytes: 0, cssBytes: 0 }
				);
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
					performanceMeasures: performance
						.getEntriesByType('measure')
						.filter((entry) => entry.name.startsWith('folio-powerbi-'))
						.map((entry) => ({ name: entry.name, duration: Math.round(entry.duration) })),
					longTasks: performance.getEntriesByType('longtask').length,
					forms: document.querySelectorAll('form').length,
					iframes: [...document.querySelectorAll('iframe')].map((iframe) => ({
						src: iframe.src,
						title: iframe.title,
						width: iframe.clientWidth,
						height: iframe.clientHeight
					}))
				};
			});
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
					frameMetrics.push({
						url: frame.url(),
						error: error instanceof Error ? error.message : String(error)
					});
				}
			}
			console.log(JSON.stringify({ route, status: response?.status() ?? null, ...metrics, frameMetrics }));
		} catch (error) {
			console.error(JSON.stringify({ route, error: error instanceof Error ? error.message : String(error) }));
			process.exitCode = 1;
		} finally {
			await page.close();
			await context.close();
		}
	}
} finally {
	await browser.close();
}
