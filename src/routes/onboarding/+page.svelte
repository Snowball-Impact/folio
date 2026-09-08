<script lang="ts">
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import { onMount } from 'svelte';
	import { currentSession } from '$lib/auth';
	import { completeOnboarding, getOnboardingStatus, type OnboardingStatus, type PolicyVersion } from '$lib/onboarding';

	const policyLabels: Record<string, string> = {
		terms: '서비스 이용약관',
		privacy: '개인정보 처리방침'
	};

	let status = $state<OnboardingStatus | null>(null);
	let agreedPolicyIds = $state<string[]>([]);
	let loading = $state(true);
	let submitting = $state(false);
	let message = $state('');
	let error = $state('');
	const nextPath = $derived(page.url.searchParams.get('next') || '/');
	const isPolicyUpdate = $derived(Boolean(status?.consentedPolicyIds.length));
	const effectiveDate = $derived(status?.policies.find((policy) => policy.effective_at)?.effective_at.slice(0, 10) ?? '');

	onMount(async () => {
		await refreshStatus();
	});

	async function refreshStatus() {
		loading = true;
		const session = await currentSession();
		if (!session) {
			await goto(`/login?next=${encodeURIComponent(nextPath)}`);
			return;
		}
		status = await getOnboardingStatus();
		agreedPolicyIds = [...(status.consentedPolicyIds ?? [])];
		loading = false;
		if (status.required && status.isComplete) {
			await goto(nextPath);
		}
	}

	async function submitOnboarding(event: SubmitEvent) {
		event.preventDefault();
		message = '';
		error = '';
		submitting = true;
		const result = await completeOnboarding(agreedPolicyIds);
		submitting = false;
		if (!result.ok) {
			error = result.message;
			return;
		}
		message = result.message;
		await goto(nextPath);
	}

	function togglePolicy(policyId: string, checked: boolean) {
		agreedPolicyIds = checked
			? [...new Set([...agreedPolicyIds, policyId])]
			: agreedPolicyIds.filter((id) => id !== policyId);
	}

	function policyLabel(policy: PolicyVersion) {
		const base = policy.title || policyLabels[policy.policy_type] || '정책 안내';
		return policy.version ? `[필수] ${base} (${policy.version})에 동의합니다.` : `[필수] ${base}에 동의합니다.`;
	}
</script>

<svelte:head>
	<title>정책 동의 | FOLIO</title>
	<meta name="description" content="FOLIO 서비스 이용을 위한 필수 정책 동의 화면입니다." />
</svelte:head>

<section class="onboarding-hero">
	<span>{isPolicyUpdate ? '정책 업데이트' : '서비스 시작'}</span>
	<h1>{isPolicyUpdate ? '이용약관이 새롭게 개정되었어요' : '서비스 이용을 시작하기 전'}</h1>
	<p>
		{isPolicyUpdate
			? '서비스를 계속 이용하시려면 변경된 정책을 확인하고 다시 동의해 주세요.'
			: '서비스 이용약관과 개인정보 처리방침을 확인하고 동의해 주세요.'}
	</p>
	{#if isPolicyUpdate && effectiveDate}
		<em>{effectiveDate}부터 적용되는 내용입니다.</em>
	{/if}
</section>

<section class="onboarding-card">
	{#if loading}
		<div class="comments-empty">온보딩 정보를 불러오는 중입니다.</div>
	{:else if status?.error}
		<div class="auth-message error">{status.error}</div>
		<button class="button-link primary" type="button" onclick={refreshStatus}>다시 시도</button>
	{:else if status}
		{#if message}
			<div class="auth-message success">{message}</div>
		{/if}
		{#if error}
			<div class="auth-message error">{error}</div>
		{/if}
		<form class="policy-form" onsubmit={submitOnboarding}>
			<h2>필수 동의</h2>
			{#each status.policies as policy}
				<article class="policy-panel">
					<details>
						<summary>{policyLabels[policy.policy_type] ?? policy.title} 보기</summary>
						{#if policy.summary}
							<strong>요약</strong>
							<p>{policy.summary}</p>
						{/if}
						<div class="policy-content">{policy.content || '정책 본문이 아직 등록되지 않았습니다.'}</div>
						{#if policy.content_url}
							<a href={policy.content_url} target="_blank" rel="noreferrer">전문 링크</a>
						{/if}
					</details>
					<label class="policy-check">
						<input
							type="checkbox"
							checked={agreedPolicyIds.includes(policy.id)}
							onchange={(event) => togglePolicy(policy.id, event.currentTarget.checked)}
						/>
						<span>{policyLabel(policy)}</span>
					</label>
				</article>
			{/each}
			<button type="submit" disabled={submitting}>{submitting ? '저장 중...' : '동의하고 시작하기'}</button>
		</form>
	{/if}
</section>
