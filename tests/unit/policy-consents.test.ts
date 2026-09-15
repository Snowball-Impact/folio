import assert from 'node:assert/strict';
import test from 'node:test';
import { latestRequiredPolicyVersions, normalizePolicyVersionIds, policyConsentRows } from '../../src/lib/server/policy-consents.ts';

const TERMS_ID = '11111111-1111-4111-8111-111111111111';
const PRIVACY_ID = '22222222-2222-4222-8222-222222222222';

test('normalizes policy IDs and stores request evidence', () => {
	assert.deepEqual(normalizePolicyVersionIds([TERMS_ID, 'nope', TERMS_ID, PRIVACY_ID]), [TERMS_ID, PRIVACY_ID]);
	assert.deepEqual(policyConsentRows('user-1', [TERMS_ID], new Headers({ 'cf-connecting-ip': '203.0.113.10' })), [{ user_id: 'user-1', policy_version_id: TERMS_ID, ip_address: '203.0.113.10', user_agent: null }]);
	assert.deepEqual(latestRequiredPolicyVersions([{ id: TERMS_ID, policy_type: 'terms' }, { id: PRIVACY_ID, policy_type: 'privacy' }]), [{ id: TERMS_ID, policy_type: 'terms' }, { id: PRIVACY_ID, policy_type: 'privacy' }]);
});
