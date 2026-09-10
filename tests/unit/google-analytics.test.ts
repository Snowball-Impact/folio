import assert from 'node:assert/strict';
import test from 'node:test';
import { normalizeGoogleAnalyticsMeasurementId } from '../../src/lib/googleAnalyticsConfig.ts';

test('normalizes GA4 measurement ids', () => {
	assert.equal(normalizeGoogleAnalyticsMeasurementId(' g-3vb889g8vk '), 'G-3VB889G8VK');
	assert.equal(normalizeGoogleAnalyticsMeasurementId('UA-123'), '');
	assert.equal(normalizeGoogleAnalyticsMeasurementId(''), '');
});
