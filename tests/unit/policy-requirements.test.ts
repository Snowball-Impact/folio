import assert from 'node:assert/strict';
import test from 'node:test';
import {
	hasRequiredPolicyTypes,
	missingRequiredPolicyTypes,
	requiredPolicyAvailabilityMessage
} from '../../src/lib/policyRequirements.ts';

test('requires active terms and privacy policy records for signup', () => {
	assert.equal(
		hasRequiredPolicyTypes([
			{ id: 'terms-v1', policy_type: 'terms' },
			{ id: 'privacy-v1', policy_type: 'privacy' }
		]),
		true
	);
	assert.deepEqual(
		missingRequiredPolicyTypes([
			{ id: 'terms-v1', policy_type: 'terms' },
			{ id: 'notice-v1', policy_type: 'notice' }
		]),
		['privacy']
	);
	assert.equal(hasRequiredPolicyTypes([{ id: 'terms-v1', policy_type: 'terms' }]), false);
	assert.equal(hasRequiredPolicyTypes([]), false);
});

test('returns a blocking message when required policy data is unavailable', () => {
	assert.equal(
		requiredPolicyAvailabilityMessage([
			{ id: 'terms-v1', policy_type: 'terms' },
			{ id: 'privacy-v1', policy_type: 'privacy' }
		]),
		''
	);
	assert.match(requiredPolicyAvailabilityMessage([]), /약관 정보를 확인하지 못했습니다/);
});
