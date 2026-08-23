<script lang="ts">
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import { signInWithEmail } from '$lib/auth';

	let email = $state('');
	let password = $state('');
	let message = $state('');
	let status = $state<'idle' | 'success' | 'error'>('idle');
	let submitting = $state(false);
	const verified = $derived(page.url.searchParams.get('verified') === '1');
	const reset = $derived(page.url.searchParams.get('reset') === '1');

	async function submitLogin(event: SubmitEvent) {
		event.preventDefault();
		submitting = true;
		message = '';
		const result = await signInWithEmail(email, password);
		status = result.ok ? 'success' : 'error';
		message = result.message;
		submitting = false;
		if (result.ok) {
			await goto('/');
		}
	}
</script>

<svelte:head>
	<title>로그인 | FOLIO</title>
	<meta name="description" content="FOLIO 계정으로 로그인합니다." />
</svelte:head>

<section class="auth-shell">
	<div class="auth-card">
		<header class="auth-header">
			<div class="eyebrow">Login</div>
			<h1>로그인</h1>
			<p>등록한 프로젝트와 포트폴리오를 이어서 관리하세요.</p>
		</header>

		{#if verified}
			<div class="notice compact">이메일 인증이 완료되었습니다. 로그인하세요.</div>
		{/if}
		{#if reset}
			<div class="notice compact">비밀번호가 변경되었습니다. 새 비밀번호로 로그인하세요.</div>
		{/if}
		{#if message}
			<div class:success={status === 'success'} class:error={status === 'error'} class="auth-message">
				{message}
			</div>
		{/if}

		<form class="auth-form" onsubmit={submitLogin}>
			<label>
				<span>이메일</span>
				<input bind:value={email} type="email" placeholder="name@example.com" autocomplete="email" />
			</label>
			<label>
				<span>비밀번호</span>
				<input bind:value={password} type="password" autocomplete="current-password" />
			</label>
			<button type="submit" disabled={submitting}>{submitting ? '로그인 중...' : '로그인'}</button>
		</form>

		<div class="auth-links">
			<a href="/reset-password">비밀번호 찾기</a>
			<a href="/signup">회원가입하기</a>
		</div>
	</div>
</section>
