import { env } from '$env/dynamic/public';

type WebVitals = {
	lcp: number | null;
	cls: number;
	inp: number | null;
};

type PowerBIMetric = {
	status: 'ready' | 'error';
	durationMs: number;
};

let initialized = false;

export function initRum() {
	const endpoint = env.PUBLIC_RUM_ENDPOINT?.trim() || null;
	if (initialized || !endpoint || typeof window === 'undefined') return;
	initialized = true;
	const rumEndpoint = String(endpoint);

	const vitals: WebVitals = { lcp: null, cls: 0, inp: null };
	let flushed = false;
	let powerBIMetricEventObserved = false;

	try {
		new PerformanceObserver((list) => {
			const latest = list.getEntries().at(-1);
			vitals.lcp = latest?.startTime ?? vitals.lcp;
		}).observe({ type: 'largest-contentful-paint', buffered: true });
	} catch {}

	try {
		new PerformanceObserver((list) => {
			for (const entry of list.getEntries() as PerformanceEntry[] & { hadRecentInput?: boolean; value?: number }[]) {
				if (!entry.hadRecentInput) vitals.cls += entry.value ?? 0;
			}
		}).observe({ type: 'layout-shift', buffered: true });
	} catch {}

	try {
		new PerformanceObserver((list) => {
			for (const entry of list.getEntries() as PerformanceEntry[] & { duration: number; interactionId?: number }[]) {
				if (entry.interactionId && (!vitals.inp || entry.duration > vitals.inp)) {
					vitals.inp = entry.duration;
				}
			}
		}).observe({ type: 'event', buffered: true, durationThreshold: 40 } as unknown as PerformanceObserverInit);
	} catch {}

	function send(payload: Record<string, unknown>) {
		const body = JSON.stringify({
			source: 'folio-svelte',
			path: window.location.pathname,
			timestamp: new Date().toISOString(),
			...payload
		});
		const blob = new Blob([body], { type: 'text/plain;charset=UTF-8' });
		if (navigator.sendBeacon?.(rumEndpoint, blob)) return;
		void fetch(rumEndpoint, {
			method: 'POST',
			body,
			keepalive: true,
			headers: { 'content-type': 'application/json' }
		}).catch(() => undefined);
	}

	function flushVitals() {
		if (flushed) return;
		flushed = true;
		if (!powerBIMetricEventObserved) {
			const shell = document.querySelector<HTMLElement>('.powerbi-shell');
			const measure = performance
				.getEntriesByType('measure')
				.filter((entry) => entry.name.startsWith('folio-powerbi-'))
				.at(-1);
			if (measure && (shell?.dataset.powerbiStatus === 'ready' || shell?.dataset.powerbiStatus === 'error')) {
				send({
					type: 'powerbi',
					status: shell.dataset.powerbiStatus,
					durationMs: Math.round(measure.duration)
				});
			}
		}
		send({
			type: 'web-vitals',
			lcp: vitals.lcp ? Math.round(vitals.lcp) : null,
			cls: Number(vitals.cls.toFixed(4)),
			inp: vitals.inp ? Math.round(vitals.inp) : null
		});
	}

	window.addEventListener('folio:powerbi-metric', (event) => {
		const detail = (event as CustomEvent<PowerBIMetric>).detail;
		if (detail?.status === 'ready' || detail?.status === 'error') {
			powerBIMetricEventObserved = true;
			send({ type: 'powerbi', status: detail.status, durationMs: detail.durationMs });
		}
	});
	window.addEventListener('pagehide', flushVitals, { once: true });
	window.addEventListener('visibilitychange', () => {
		if (document.visibilityState === 'hidden') flushVitals();
	});
}
