export const REQUIRED_POLICY_TYPES = ['terms', 'privacy'] as const;

export type RequiredPolicyType = (typeof REQUIRED_POLICY_TYPES)[number];

export type PolicyRequirementCandidate = {
	policy_type?: string | null;
	id?: string | null;
};

export function missingRequiredPolicyTypes(policies: PolicyRequirementCandidate[]) {
	const activeTypes = new Set(
		policies
			.filter((policy) => policy.id)
			.map((policy) => policy.policy_type)
			.filter((policyType): policyType is RequiredPolicyType => isRequiredPolicyType(policyType))
	);
	return REQUIRED_POLICY_TYPES.filter((policyType) => !activeTypes.has(policyType));
}

export function hasRequiredPolicyTypes(policies: PolicyRequirementCandidate[]) {
	return missingRequiredPolicyTypes(policies).length === 0;
}

export function requiredPolicyAvailabilityMessage(policies: PolicyRequirementCandidate[]) {
	return hasRequiredPolicyTypes(policies)
		? ''
		: '서비스 이용에 필요한 약관 정보를 확인하지 못했습니다. 잠시 후 다시 시도하거나 문의해 주세요.';
}

function isRequiredPolicyType(value: string | null | undefined): value is RequiredPolicyType {
	return value === 'terms' || value === 'privacy';
}
