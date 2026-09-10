import assert from 'node:assert/strict';
import test from 'node:test';
import {
	consentEvidenceFromHeaders,
	latestRequiredPolicyVersions,
	normalizePolicyVersionIds,
	policyConsentRows
} from '../../src/lib/server/policy-consents.ts';

const TERMS_ID = '11111111-1111-4111-8111-111111111111';
const PRIVACY_ID = '22222222-2222-4222-8222-222222222222';

test('normalizes unique uuid policy version ids only', () => {
	assert.deepEqual(normalizePolicyVersionIds([TERMS_ID, 'nope', TERMS_ID, PRIVACY_ID, '', null]), [TERMS_ID, PRIVACY_ID]);
	assert.deepEqual(normalizePolicyVersionIds('not-array'), []);
});

test('extracts consent evidence from Cloudflare-oriented headers', () => {
	const headers = new Headers({
		'cf-connecting-ip': '203.0.113.10',
		'user-agent': 'FOLIO Test Browser'
	});
	assert.deepEqual(consentEvidenceFromHeaders(headers), {
		ipAddress: '203.0.113.10',
		userAgent: 'FOLIO Test Browser'
	});
});

test('builds consent rows with the authenticated user and evidence', () => {
	const rows = policyConsentRows('user-1', [TERMS_ID], new Headers({ 'x-forwarded-for': '2001:db8::1, 198.51.100.1' }));
	assert.deepEqual(rows, [
		{
			user_id: 'user-1',
			policy_version_id: TERMS_ID,
			ip_address: '2001:db8::1',
			user_agent: null
		}
	]);
});

test('keeps only the latest required active policy rows by sorted input order', () => {
	assert.deepEqual(
		latestRequiredPolicyVersions([
			{ id: TERMS_ID, policy_type: 'terms' },
			{ id: 'ignored-notice', policy_type: 'notice' },
			{ id: 'ignored-older-terms', policy_type: 'terms' },
			{ id: PRIVACY_ID, policy_type: 'privacy' }
		]),
		[
			{ id: TERMS_ID, policy_type: 'terms' },
			{ id: PRIVACY_ID, policy_type: 'privacy' }
		]
	);
});
