import { browser } from '$app/environment';
import { afterNavigate } from '$app/navigation';
import { env } from '$env/dynamic/public';
import { normalizeGoogleAnalyticsMeasurementId } from '$lib/googleAnalyticsConfig';

declare global {
	interface Window {
		dataLayer?: unknown[];
		gtag?: (...args: unknown[]) => void;
	}
}

let initialized = false;

export function initGoogleAnalytics() {
	const measurementId = normalizeGoogleAnalyticsMeasurementId(env.PUBLIC_GA_MEASUREMENT_ID);
	if (!browser || initialized || !measurementId) {
		return;
	}

	initialized = true;
	window.dataLayer = window.dataLayer || [];
	window.gtag = (...args: unknown[]) => {
		window.dataLayer?.push(args);
	};
	window.gtag('js', new Date());
	window.gtag('config', measurementId, { send_page_view: false });
	loadGoogleAnalyticsScript(measurementId);

	afterNavigate(({ to }) => {
		const url = to?.url ?? new URL(window.location.href);
		trackGoogleAnalyticsPageView({
			pageTitle: document.title,
			pageLocation: url.href,
			pagePath: `${url.pathname}${url.search}`
		});
	});
}

export function trackGoogleAnalyticsEvent(eventName: string, params: Record<string, unknown> = {}) {
	const name = eventName.trim();
	if (!browser || !name || typeof window.gtag !== 'function') {
		return;
	}
	window.gtag('event', name, params);
}

function trackGoogleAnalyticsPageView(input: { pageTitle: string; pageLocation: string; pagePath: string }) {
	trackGoogleAnalyticsEvent('page_view', {
		page_title: input.pageTitle,
		page_location: input.pageLocation,
		page_path: input.pagePath
	});
}

function loadGoogleAnalyticsScript(measurementId: string) {
	if (document.getElementById('folio-ga-tag')) {
		return;
	}
	const loader = document.createElement('script');
	loader.id = 'folio-ga-tag';
	loader.async = true;
	loader.src = `https://www.googletagmanager.com/gtag/js?id=${encodeURIComponent(measurementId)}`;
	document.head.appendChild(loader);
}
