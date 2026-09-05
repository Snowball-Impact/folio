<script lang="ts">
	import { onMount } from 'svelte';
	import { signUpWithEmail } from '$lib/auth';
	import { getActivePolicyVersions, type PolicyVersion } from '$lib/onboarding';

	let email = $state('');
	let password = $state('');
	let passwordConfirm = $state('');
	let name = $state('');
	let organization = $state('');
	let policies = $state<PolicyVersion[]>([]);
	let agreedPolicyIds = $state<string[]>([]);
	let policyLoading = $state(true);
	let policyError = $state('');
	let message = $state('');
	let status = $state<'idle' | 'success' | 'error'>('idle');
	let submitting = $state(false);
	const requiredPolicyIds = $derived(policies.map((policy) => policy.id));
	const sharedPolicyEffectiveDate = $derived(sharedEffectiveDate(policies));

	onMount(async () => {
		const result = await getActivePolicyVersions();
		policies = result.policies;
		policyError = result.error;
		policyLoading = false;
	});

	async function submitSignup(event: SubmitEvent) {
		event.preventDefault();
		if (policyError) {
			status = 'error';
			message = policyError;
			return;
		}
		if (policies.length > 0 && !requiredPolicyIds.every((policyId) => agreedPolicyIds.includes(policyId))) {
			status = 'error';
			message = '서비스 이용약관과 개인정보 처리방침에 동의해 주세요.';
			return;
		}
		submitting = true;
		message = '';
		const result = await signUpWithEmail({
			email,
			password,
			passwordConfirm,
			name,
			organization,
			consentedPolicyVersionIds: requiredPolicyIds
		});
		status = result.ok ? 'success' : 'error';
		message = result.message;
		submitting = false;
	}

	function togglePolicy(policyId: string, checked: boolean) {
		agreedPolicyIds = checked
			? [...new Set([...agreedPolicyIds, policyId])]
			: agreedPolicyIds.filter((id) => id !== policyId);
	}

	function policyLabel(policy: PolicyVersion) {
		const base = policy.policy_type === 'terms' ? '서비스 이용약관' : '개인정보 처리방침';
		const title = stripPolicyDate(policy.title || base);
		return `${title} 동의`;
	}

	function policyMeta(policy: PolicyVersion) {
		if (sharedPolicyEffectiveDate) {
			return '';
		}
		const date = policy.effective_at ? `${policy.effective_at.slice(0, 10)} 시행` : '';
		const items = [policy.version, date].filter(Boolean);
		return items.join(' · ');
	}

	function sharedEffectiveDate(values: PolicyVersion[]) {
		const dates = [...new Set(values.map((policy) => policy.effective_at?.slice(0, 10)).filter(Boolean))];
		return dates.length === 1 ? dates[0] : '';
	}

	function stripPolicyDate(value: string) {
		return value.replace(/\s*\(\d{4}-\d{2}-\d{2}\)\s*/g, ' ').replace(/\s+/g, ' ').trim();
	}
</script>

<svelte:head>
	<title>회원가입 | FOLIO</title>
	<meta name="description" content="FOLIO 계정을 만들고 프로젝트를 공유합니다." />
</svelte:head>

<section class="auth-shell">
	<div class="auth-card signup">
		<header class="auth-header">
			<div class="eyebrow">Sign Up</div>
			<h1>회원가입</h1>
			<p>이메일 인증 후 프로젝트를 등록하고 공유할 수 있습니다.</p>
		</header>

		{#if message}
			<div class:success={status === 'success'} class:error={status === 'error'} class="auth-message">
				{message}
			</div>
		{/if}

		<form class="auth-form" onsubmit={submitSignup}>
			<label>
				<span>이메일 *</span>
				<input bind:value={email} type="email" placeholder="name@example.com" autocomplete="email" />
			</label>
			<label>
				<span>비밀번호 *</span>
				<input bind:value={password} type="password" placeholder="8자 이상 입력" autocomplete="new-password" />
			</label>
			<label>
				<span>비밀번호 확인 *</span>
				<input bind:value={passwordConfirm} type="password" autocomplete="new-password" />
			</label>
			<label>
				<span>이름 *</span>
				<input bind:value={name} type="text" placeholder="홍길동" autocomplete="name" />
			</label>
			<label>
				<span>소속 *</span>
				<input
					bind:value={organization}
					type="text"
					placeholder="개인, 학원, 학교, 기관, 회사명을 입력하세요"
					autocomplete="organization"
				/>
			</label>
			<section class="signup-policy-panel" aria-label="필수 정책 동의">
				<div class="signup-policy-heading">
					<div>
						<strong>필수 동의</strong>
						<p>
							서비스 이용을 위해 아래 항목에 동의해 주세요.{#if sharedPolicyEffectiveDate}
								<span>{sharedPolicyEffectiveDate} 시행</span>
							{/if}
						</p>
					</div>
				</div>
				{#if policyLoading}
					<p>정책 정보를 불러오는 중입니다.</p>
				{:else if policyError}
					<p class="error-text">{policyError}</p>
				{:else if policies.length === 0}
					<p>현재 필수 동의 항목이 없습니다.</p>
				{:else}
					{#each policies as policy}
						<label class="signup-policy-check">
							<input
								type="checkbox"
								checked={agreedPolicyIds.includes(policy.id)}
								onchange={(event) => togglePolicy(policy.id, event.currentTarget.checked)}
							/>
							<span>
								<strong>{policyLabel(policy)}</strong>
								{#if policyMeta(policy)}
									<small>{policyMeta(policy)}</small>
								{/if}
							</span>
							<a href={`/policy/${policy.policy_type}`} target="_blank" rel="noreferrer">보기</a>
						</label>
					{/each}
				{/if}
			</section>
			<button type="submit" disabled={submitting || policyLoading || Boolean(policyError)}>
				{submitting ? '가입 처리 중...' : '회원가입'}
			</button>
		</form>

		<div class="auth-links">
			<a href="/login">이미 계정이 있다면 로그인하기</a>
		</div>
	</div>
</section>
