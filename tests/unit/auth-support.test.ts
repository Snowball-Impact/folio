import assert from 'node:assert/strict';
import test from 'node:test';
import { authRetryAfterSeconds, friendlyAuthError, parseRecoveryParams } from '../../src/lib/authSupport.ts';

test('parses the canonical recovery token hash callback', () => {
	const result = parseRecoveryParams('?token_hash=abc123&type=recovery', '');
	assert.equal(result.tokenHash, 'abc123');
	assert.equal(result.hasRecovery, true);
	assert.equal(result.errorMessage, '');
});

test('shows a useful message for expired recovery callbacks', () => {
	const result = parseRecoveryParams('?error=access_denied&error_code=otp_expired&error_description=expired', '');
	assert.equal(result.hasRecovery, false);
	assert.match(result.errorMessage, /만료/);
});

test('parses Supabase security cooldown messages', () => {
	const message = 'For security purposes, you can only request this after 47 seconds.';
	assert.equal(authRetryAfterSeconds(message), 47);
	assert.equal(friendlyAuthError('인증 메일 재발송', message), '인증 메일은 47초 후 다시 요청할 수 있습니다.');
});
