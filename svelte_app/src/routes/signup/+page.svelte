<script lang="ts">
	import { signUpWithEmail } from '$lib/auth';

	let email = $state('');
	let password = $state('');
	let passwordConfirm = $state('');
	let name = $state('');
	let organization = $state('');
	let message = $state('');
	let status = $state<'idle' | 'success' | 'error'>('idle');
	let submitting = $state(false);

	async function submitSignup(event: SubmitEvent) {
		event.preventDefault();
		submitting = true;
		message = '';
		const result = await signUpWithEmail({
			email,
			password,
			passwordConfirm,
			name,
			organization
		});
		status = result.ok ? 'success' : 'error';
		message = result.message;
		submitting = false;
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
			<button type="submit" disabled={submitting}>{submitting ? '가입 처리 중...' : '회원가입'}</button>
		</form>

		<div class="auth-links">
			<a href="/login">이미 계정이 있다면 로그인하기</a>
		</div>
	</div>
</section>
