<script lang="ts">
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import { onMount } from 'svelte';
	import { completePolicyConsent, getPolicyConsentStatus, type PolicyConsentStatus, type PolicyVersion } from '$lib/onboarding';
	import { currentSession } from '$lib/auth';
	import { safeInternalNextPath } from '$lib/navigation';

	const policyLabels: Record<PolicyVersion['policy_type'], string> = { terms: '서비스 이용약관', privacy: '개인정보 처리방침' };
	let status = $state<PolicyConsentStatus | null>(null);
	let agreed = $state<string[]>([]);
	let loading = $state(true);
	let submitting = $state(false);
	let message = $state('');
	let error = $state('');
	const nextPath = $derived(safeInternalNextPath(page.url.searchParams.get('next')));
	const canSubmit = $derived(Boolean(status?.policies.length && status.policies.every((policy) => agreed.includes(policy.id))));

	onMount(() => void refresh());
	async function refresh() {
		loading = true; message = ''; error = '';
		const session = await currentSession();
		if (!session) { await goto(`/login?next=${encodeURIComponent(safeInternalNextPath(`${page.url.pathname}${page.url.search}`))}`); return; }
		status = await getPolicyConsentStatus(session);
		agreed = [...status.consentedPolicyIds];
		loading = false;
		if (status.required && status.isComplete) await goto(nextPath);
	}
	async function submit(event: SubmitEvent) {
		event.preventDefault();
		if (submitting) return;
		submitting = true; message = ''; error = '';
		const result = await completePolicyConsent(agreed);
		submitting = false;
		if (!result.ok) { error = result.message; return; }
		message = result.message;
		await goto(nextPath);
	}
	function toggle(id: string, checked: boolean) { agreed = checked ? [...new Set([...agreed, id])] : agreed.filter((value) => value !== id); }
</script>

<svelte:head>
	<title>정책 재동의 | FOLIO</title>
	<meta name="description" content="FOLIO 서비스를 계속 이용하기 위한 필수 정책 재동의 화면입니다." />
</svelte:head>

<section class="auth-shell"><div class="auth-card signup">
	<header class="auth-header"><div class="eyebrow">POLICY UPDATE</div><h1>정책 재동의</h1><p>서비스를 계속 이용하시려면 변경된 정책을 확인하고 다시 동의해 주세요.</p></header>
	{#if loading}<p>정책 동의 정보를 불러오는 중입니다.</p>
	{:else if status?.error}<div class="auth-message error">{status.error}</div><button type="button" onclick={refresh}>다시 시도</button>
	{:else if status}<form class="auth-form" onsubmit={submit}>
		{#each status.policies as policy}<section class="signup-policy-panel">
			<strong>{policyLabels[policy.policy_type]} · {policy.version}</strong>
			{#if policy.summary}<p>{policy.summary}</p>{/if}
			<details><summary>{policyLabels[policy.policy_type]} 전문 보기</summary><p>{policy.content || '정책 본문은 전문 링크에서 확인할 수 있습니다.'}</p></details>
			{#if policy.content_url}<a href={policy.content_url} target="_blank" rel="noreferrer">전문 링크</a>{/if}
			<label class="signup-policy-check"><input type="checkbox" checked={agreed.includes(policy.id)} onchange={(event) => toggle(policy.id, event.currentTarget.checked)} /><span><strong>{policyLabels[policy.policy_type]}에 동의합니다.</strong><small>{policy.effective_at.slice(0, 10)} 시행</small></span></label>
		</section>{/each}
		{#if error}<div class="auth-message error">{error}</div>{/if}{#if message}<div class="auth-message success">{message}</div>{/if}
		<button type="submit" disabled={!canSubmit || submitting}>{submitting ? '저장 중...' : '동의하고 계속하기'}</button>
	</form>{/if}
</div></section>
