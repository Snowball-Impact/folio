import assert from 'node:assert/strict';
import test from 'node:test';
import { securityHeaders } from '../../src/lib/server/security-headers.ts';

test('builds baseline security headers', () => {
	const headers = securityHeaders();
	assert.equal(headers['X-Content-Type-Options'], 'nosniff');
	assert.equal(headers['X-Frame-Options'], 'DENY');
	assert.match(headers['Content-Security-Policy'], /default-src 'self'/);
	assert.match(headers['Content-Security-Policy'], /frame-ancestors 'none'/);
	assert.match(headers['Content-Security-Policy'], /object-src 'none'/);
});

test('allows required Supabase, RUM, and Power BI origins in CSP', () => {
	const headers = securityHeaders({
		supabaseUrl: 'https://abc.supabase.co/rest/v1',
		rumEndpoint: 'https://rum.example.com/v1/events'
	});
	const csp = headers['Content-Security-Policy'];
	assert.match(csp, /connect-src .*https:\/\/abc\.supabase\.co/);
	assert.match(csp, /connect-src .*wss:\/\/abc\.supabase\.co/);
	assert.match(csp, /connect-src .*https:\/\/rum\.example\.com/);
	assert.match(csp, /frame-src .*https:\/\/app\.powerbi\.com/);
	assert.match(csp, /style-src 'self' 'unsafe-inline'/);
});

test('allows nonce-based SvelteKit inline scripts without enabling all inline scripts', () => {
	const headers = securityHeaders({ scriptNonce: 'test-nonce' });
	const csp = headers['Content-Security-Policy'];
	assert.match(csp, /script-src 'self' 'nonce-test-nonce'/);
	assert.doesNotMatch(csp, /script-src[^;]*'unsafe-inline'/);
});

test('allows Google Analytics origins only when GA is configured', () => {
	const disabledCsp = securityHeaders()['Content-Security-Policy'];
	assert.doesNotMatch(disabledCsp, /googletagmanager/);
	assert.doesNotMatch(disabledCsp, /google-analytics/);

	const enabledCsp = securityHeaders({ googleAnalyticsMeasurementId: 'G-3VB889G8VK' })['Content-Security-Policy'];
	assert.match(enabledCsp, /script-src .*https:\/\/www\.googletagmanager\.com/);
	assert.match(enabledCsp, /connect-src .*https:\/\/www\.google-analytics\.com/);
	assert.match(enabledCsp, /connect-src .*https:\/\/\*\.google-analytics\.com/);
});
