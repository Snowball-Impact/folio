<script lang="ts">
	let { data } = $props();
	const meta = $derived(
		[
			data.policy?.version ? `버전 ${data.policy.version}` : '',
			data.policy?.effective_at ? `시행일 ${String(data.policy.effective_at).slice(0, 10)}` : ''
		].filter(Boolean)
	);
</script>

<svelte:head>
	<title>{data.label} | FOLIO</title>
	<meta name="description" content={`FOLIO ${data.label}`} />
</svelte:head>

<section class="policy-page-hero">
	<div class="eyebrow">FOLIO POLICY</div>
	<h1>{data.label}</h1>
	{#if meta.length > 0}
		<p>{meta.join(' · ')}</p>
	{/if}
</section>

<section class="policy-document">
	{#if data.error}
		<div class="notice compact">{data.error}</div>
	{:else if data.policy}
		{#if data.policy.summary}
			<div class="policy-summary">
				<strong>요약</strong>
				<p>{data.policy.summary}</p>
			</div>
		{/if}
		<div class="policy-body">{data.policy.content || '정책 본문이 아직 등록되지 않았습니다.'}</div>
		{#if data.policy.content_url}
			<a class="button-link" href={data.policy.content_url} target="_blank" rel="noreferrer">전문 링크</a>
		{/if}
	{/if}
</section>