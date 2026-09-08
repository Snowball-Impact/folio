<script lang="ts">
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import { completePasswordReset, requestPasswordReset } from '$lib/auth';

	type RecoveryParams = {
		code: string;
		tokenHash: string;
		accessToken: string;
		refreshToken: string;
		hasRecovery: boolean;
	};

	let email = $state(page.url.searchParams.get('email') ?? '');
	let password = $state('');
	let passwordConfirm = $state('');
	let recovery = $state<RecoveryParams>({
		code: '',
		tokenHash: '',
		accessToken: '',
		refreshToken: '',
		hasRecovery: false
	});
	let message = $state('');
	let status = $state<'idle' | 'success' | 'error'>('idle');
	let submitting = $state(false);

	$effect(() => {
		if (typeof window !== 'undefined') {
			recovery = readRecoveryParams();
		}
	});

	async function submitRequest(event: SubmitEvent) {
		event.preventDefault();
		submitting = true;
		message = '';
		const result = await requestPasswordReset(email);
		status = result.ok ? 'success' : 'error';
		message = result.message;
		submitting = false;
	}

	async function submitUpdate(event: SubmitEvent) {
		event.preventDefault();
		submitting = true;
		message = '';
		const result = await completePasswordReset({
			password,
			passwordConfirm,
			code: recovery.code,
			tokenHash: recovery.tokenHash,
			accessToken: recovery.accessToken,
			refreshToken: recovery.refreshToken
		});
		status = result.ok ? 'success' : 'error';
		message = result.message;
		submitting = false;
		if (result.ok) {
			await goto('/login?reset=1');
		}
	}

	function readRecoveryParams(): RecoveryParams {
		const query = new URLSearchParams(window.location.search);
		const hash = new URLSearchParams(window.location.hash.replace(/^#/, ''));
		const recoveryType = query.get('type') || hash.get('type') || '';
		const tokenHash = query.get('token_hash') || query.get('token') || hash.get('token_hash') || hash.get('token') || '';
		const code = query.get('code') || hash.get('code') || '';
		const accessToken = query.get('access_token') || hash.get('access_token') || '';
		const refreshToken = query.get('refresh_token') || hash.get('refresh_token') || '';
		const validTokenHash = !recoveryType || recoveryType === 'recovery' ? tokenHash : '';

		return {
			code,
			tokenHash: validTokenHash,
			accessToken,
			refreshToken,
			hasRecovery: Boolean(code || validTokenHash || (accessToken && refreshToken))
		};
	}
</script>

<svelte:head>
	<title>비밀번호 재설정 | FOLIO</title>
	<meta name="description" content="FOLIO 계정 비밀번호를 재설정합니다." />
</svelte:head>

<section class="auth-shell">
	<div class="auth-card">
		<header class="auth-header">
			<div class="eyebrow">Password Reset</div>
			<h1>비밀번호 재설정</h1>
			<p>{recovery.hasRecovery ? '새 비밀번호를 입력하세요.' : '가입한 이메일로 재설정 링크를 보내드립니다.'}</p>
		</header>

		{#if message}
			<div class:success={status === 'success'} class:error={status === 'error'} class="auth-message">
				{message}
			</div>
		{/if}

		{#if recovery.hasRecovery}
			<form class="auth-form" onsubmit={submitUpdate}>
				<label>
					<span>새 비밀번호</span>
					<input bind:value={password} type="password" placeholder="8자 이상 입력" autocomplete="new-password" />
				</label>
				<label>
					<span>새 비밀번호 확인</span>
					<input bind:value={passwordConfirm} type="password" autocomplete="new-password" />
				</label>
				<button type="submit" disabled={submitting}>{submitting ? '변경 중...' : '비밀번호 변경'}</button>
			</form>
		{:else}
			<form class="auth-form" onsubmit={submitRequest}>
				<label>
					<span>이메일</span>
					<input bind:value={email} type="email" placeholder="name@example.com" autocomplete="email" />
				</label>
				<button type="submit" disabled={submitting}>{submitting ? '요청 중...' : '재설정 메일 받기'}</button>
			</form>
		{/if}

		<div class="auth-links">
			<a href="/login">로그인으로 돌아가기</a>
		</div>
	</div>
</section>
