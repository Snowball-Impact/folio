import assert from 'node:assert/strict';
import test from 'node:test';
import { clientIpAddress, enforceRateLimit, rateLimitSubjects } from '../../src/lib/server/rate-limit.ts';

const policy = {
	action: 'powerbi-embed',
	maxRequests: 2,
	windowSeconds: 60,
	userId: '6c83b157-1f6c-4db2-9dc3-0f44fe5e403e'
};

test('uses only the Cloudflare client IP and ignores client forwarding headers', () => {
	const headers = new Headers({
		'cf-connecting-ip': '203.0.113.10',
		'x-forwarded-for': '198.51.100.23'
	});
	assert.equal(clientIpAddress(headers), '203.0.113.10');
	assert.deepEqual(rateLimitSubjects(headers, policy.userId), [
		'ip:203.0.113.10',
		'user:6c83b157-1f6c-4db2-9dc3-0f44fe5e403e'
	]);
	assert.equal(clientIpAddress(new Headers({ 'x-forwarded-for': '198.51.100.23' })), 'unknown');
});

test('fails closed when the rate-limit backend is unavailable', async () => {
	const result = await enforceRateLimit(null, new Headers(), policy);
	assert.deepEqual(result, { ok: false, reason: 'unavailable', retryAfterSeconds: 60 });
});

test('rejects when either the IP or user bucket is exhausted', async () => {
	const calls: Array<{ functionName: string; parameters: Record<string, unknown> }> = [];
	const client = {
		async rpc(functionName: string, parameters: Record<string, unknown>) {
			calls.push({ functionName, parameters });
			return { data: calls.length === 1, error: null };
		}
	};
	const result = await enforceRateLimit(client, new Headers({ 'cf-connecting-ip': '2001:db8::1' }), policy);
	assert.deepEqual(result, { ok: false, reason: 'limited', retryAfterSeconds: 60 });
	assert.equal(calls.length, 2);
	assert.equal(calls[0].functionName, 'consume_server_rate_limit');
	assert.match(String(calls[0].parameters.p_rate_key), /^[a-f0-9]{64}$/);
	assert.notEqual(calls[0].parameters.p_rate_key, 'ip:2001:db8::1');
});

test('permits requests only when every bucket accepts them', async () => {
	const client = {
		async rpc() {
			return { data: true, error: null };
		}
	};
	assert.deepEqual(await enforceRateLimit(client, new Headers(), policy), { ok: true });
});
