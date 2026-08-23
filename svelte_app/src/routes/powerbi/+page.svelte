<script lang="ts">
	import { formatDate } from '$lib/format';
	import type { PowerBIContentLink, PowerBIHubTopic } from '$lib/types';

	let { data } = $props();

	const topics: Array<{ key: PowerBIHubTopic; label: string }> = [
		{ key: 'news', label: '소식' },
		{ key: 'learning', label: '학습 콘텐츠' },
		{ key: 'community', label: '커뮤니티' },
		{ key: 'certifications', label: '자격증' }
	];

	function topicHref(topic: PowerBIHubTopic) {
		return topic === 'news' ? '/powerbi' : `/powerbi?topic=${topic}`;
	}
</script>

<svelte:head>
	<title>Power BI 콘텐츠 허브 | FOLIO</title>
	<meta name="description" content="Power BI 업데이트, 학습 콘텐츠, 커뮤니티 소식과 자격증 링크를 모아 봅니다." />
</svelte:head>

<section class="powerbi-hero">
	<div>
		<div class="eyebrow">Power BI Hub</div>
		<h1>Power BI 소식</h1>
		<p>업데이트, 공식 학습, 커뮤니티 글, 자격증 경로를 한곳에서 확인합니다.</p>
		{#if data.desktop}
			<a class="hero-cta" href={data.desktop.url} target="_blank" rel="noreferrer">
				최신 Desktop 다운로드 · {data.desktop.topic}
			</a>
		{/if}
	</div>
	<img src="/reference-powerbi-logo-cropped.webp" alt="" />
</section>

<section class="content-tabs" aria-label="Power BI 콘텐츠 메뉴">
	{#each topics as item}
		<a class:active={item.key === data.topic} href={topicHref(item.key)}>
			{item.label}
			<span>{data.counts[item.key]}</span>
		</a>
	{/each}
</section>

{#if data.topic === 'learning'}
	{#each data.learning as group}
		<section class="content-section">
			<div class="section-header">
				<h2>{group.category}</h2>
				<p>{group.programs.length + group.videos.length}개 콘텐츠</p>
			</div>
			<div class="content-grid">
				{#each group.programs as item}
					{@render ContentCard(item, 'program')}
				{/each}
				{#each group.videos as item}
					{@render ContentCard(item, 'video')}
				{/each}
			</div>
		</section>
	{/each}
{:else if data.topic === 'community'}
	<section class="content-list">
		{#each data.community as item}
			{@render ContentRow(item)}
		{:else}
			<div class="empty-panel">아직 수집된 커뮤니티 소식이 없습니다.</div>
		{/each}
	</section>
{:else if data.topic === 'certifications'}
	<section class="cert-grid">
		{#each data.certifications as item}
			<a class="cert-card" href={item.url} target="_blank" rel="noreferrer">
				<span>{item.topic}</span>
				<strong>{item.title}</strong>
				<em>{item.summary}</em>
			</a>
		{/each}
	</section>
{:else}
	<section class="news-board">
		{#each data.news as item}
			<article class="news-item">
				<div class="news-meta">
					<span>{item.label}</span>
					<span>{formatDate(item.date)}</span>
				</div>
				<h2>{item.title}</h2>
				<ul>
					{#each item.bullets as bullet}
						<li>{bullet}</li>
					{/each}
				</ul>
				<div class="news-actions">
					<a href={item.source_url} target="_blank" rel="noreferrer">원문 보기</a>
					{#if item.video}
						<a href={item.video.url} target="_blank" rel="noreferrer">공식 영상</a>
					{/if}
				</div>
			</article>
		{:else}
			<div class="empty-panel">아직 수집된 Power BI 소식이 없습니다.</div>
		{/each}
	</section>
{/if}

{#snippet ContentCard(item: PowerBIContentLink, variant: 'program' | 'video')}
	<a class="content-card" class:program={variant === 'program'} href={item.url} target="_blank" rel="noreferrer">
		{#if item.image_url}
			<img src={item.image_url} alt="" loading="lazy" />
		{/if}
		<span>{item.source} · {item.topic}</span>
		<strong>{item.title}</strong>
		<em>{item.summary}</em>
	</a>
{/snippet}

{#snippet ContentRow(item: PowerBIContentLink)}
	<a class="content-row" href={item.url} target="_blank" rel="noreferrer">
		<div>
			<span>{item.source} · {formatDate(item.date)}</span>
			<strong>{item.title}</strong>
			<p>{item.summary}</p>
		</div>
		<em>{item.topic}</em>
	</a>
{/snippet}
