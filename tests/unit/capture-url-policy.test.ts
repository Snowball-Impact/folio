import assert from 'node:assert/strict';
import test from 'node:test';
import { normalizeCaptureUrl } from '../../src/lib/server/capture-url-policy.ts';

const cloudflarePolicy = {
	allowedHosts: 'app.powerbi.com,app.fabric.microsoft.com',
	appUrl: 'https://folio.example.com',
	provider: 'cloudflare',
	requestOrigin: 'https://preview.folio.pages.dev'
};

test('allows first-party, APP_URL, and explicitly allowed HTTPS capture URLs', () => {
	assert.equal(normalizeCaptureUrl('https://preview.folio.pages.dev/projects/demo', cloudflarePolicy), 'https://preview.folio.pages.dev/projects/demo');
	assert.equal(normalizeCaptureUrl('https://folio.example.com/projects/demo', cloudflarePolicy), 'https://folio.example.com/projects/demo');
	assert.equal(normalizeCaptureUrl('https://app.powerbi.com/view?r=example', cloudflarePolicy), 'https://app.powerbi.com/view?r=example');
	assert.equal(normalizeCaptureUrl('<iframe src="https://app.fabric.microsoft.com/report"></iframe>', cloudflarePolicy), 'https://app.fabric.microsoft.com/report');
});

test('rejects credentials, HTTP external URLs, unlisted hosts, and private networks', () => {
	assert.equal(normalizeCaptureUrl('https://user:pass@app.powerbi.com/report', cloudflarePolicy), null);
	assert.equal(normalizeCaptureUrl('http://app.powerbi.com/report', cloudflarePolicy), null);
	assert.equal(normalizeCaptureUrl('https://snowball-impact.github.io/report', cloudflarePolicy), null);
	assert.equal(normalizeCaptureUrl('https://127.0.0.1:8080/admin', cloudflarePolicy), null);
	assert.equal(normalizeCaptureUrl('https://169.254.169.254/latest/meta-data', cloudflarePolicy), null);
});

test('allows a localhost first-party URL only for local Playwright capture', () => {
	const localPolicy = {
		...cloudflarePolicy,
		provider: 'local',
		requestOrigin: 'http://localhost:5173',
		appUrl: 'http://localhost:5173'
	};
	assert.equal(normalizeCaptureUrl('http://localhost:5173/projects/demo', localPolicy), 'http://localhost:5173/projects/demo');
	assert.equal(normalizeCaptureUrl('http://localhost:5173/projects/demo', cloudflarePolicy), null);
});
