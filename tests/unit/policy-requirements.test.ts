import assert from 'node:assert/strict';
import test from 'node:test';
import { missingRequiredPolicyTypes, requiredPolicyAvailabilityMessage } from '../../src/lib/policyRequirements.ts';

test('requires active terms and privacy policy records', () => {
	assert.deepEqual(missingRequiredPolicyTypes([{ id: 'terms', policy_type: 'terms' }, { id: 'privacy', policy_type: 'privacy' }]), []);
	assert.deepEqual(missingRequiredPolicyTypes([{ id: 'terms', policy_type: 'terms' }]), ['privacy']);
	assert.match(requiredPolicyAvailabilityMessage([]), /약관 정보를 확인하지 못했습니다/);
});
