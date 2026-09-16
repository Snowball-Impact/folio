import assert from 'node:assert/strict';
import test from 'node:test';
import { createGoogleAnalyticsQueue, normalizeGoogleAnalyticsMeasurementId } from '../../src/lib/googleAnalyticsConfig.ts';

test('normalizes GA4 measurement ids', () => {
	assert.equal(normalizeGoogleAnalyticsMeasurementId(' g-3vb889g8vk '), 'G-3VB889G8VK');
	assert.equal(normalizeGoogleAnalyticsMeasurementId('UA-123'), '');
	assert.equal(normalizeGoogleAnalyticsMeasurementId(''), '');
});

test('queues GA commands as standard arguments objects', () => {
	const dataLayer: unknown[] = [];
	const gtag = createGoogleAnalyticsQueue(dataLayer);

	gtag('event', 'page_view', { page_path: '/' });

	assert.equal(Object.prototype.toString.call(dataLayer[0]), '[object Arguments]');
	assert.deepEqual(Array.from(dataLayer[0] as IArguments), ['event', 'page_view', { page_path: '/' }]);
});
