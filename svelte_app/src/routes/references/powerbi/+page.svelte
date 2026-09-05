<script lang="ts">
	import ProjectCard from '$lib/components/ProjectCard.svelte';
	import { formatCount } from '$lib/format';
	import type { ReferenceSort } from '$lib/types';

	const PAGE_SIZE = 24;

	let { data } = $props();
	let visibleCount = $state(PAGE_SIZE);
	const projects = $derived(data.projects);
	const visibleProjects = $derived(projects.slice(0, visibleCount));
	const remainingCount = $derived(Math.max(projects.length - visibleCount, 0));
	const referencePlatforms = [
		{ key: 'powerbi', label: 'Power BI', href: '/references/powerbi' }
	];
	const sortItems: Array<{ key: ReferenceSort; label: string }> = [
		{ key: 'latest', label: '최신순' },
		{ key: 'likes', label: '좋아요순' },
		{ key: 'views', label: '조회수순' }
	];

	function showMore() {
		visibleCount = Math.min(visibleCount + PAGE_SIZE, projects.length);
	}
</script>

<svelte:head>
	<title>{data.platform.label} 레퍼런스 | FOLIO</title>
	<meta name="description" content={data.platform.description} />
</svelte:head>

<section class="reference-hero">
	<div class="reference-hero-copy">
		<div class="eyebrow">Reference Library</div>
		<h1 class="reference-hero-title">
			<span class="reference-hero-count">{projects.length.toLocaleString('ko-KR')}</span><span class="reference-hero-title-text">개의 레퍼런스를 참고해보세요.</span>
		</h1>
		<p>{data.platform.description}</p>
	</div>
	<div class="reference-hero-visual" aria-label={data.platform.label}>
		<div class="reference-hero-logo">
			<img class={`reference-logo-image reference-logo-image-${data.platform.key}`} src={`/reference-${data.platform.key}-logo-cropped.webp`} alt="" />
		</div>
		<nav class="reference-hero-tabs" aria-label="레퍼런스 플랫폼">
			{#each referencePlatforms as platform}
				<a
					class:active={platform.key === data.platform.key}
					href={platform.href}
					aria-current={platform.key === data.platform.key ? 'page' : undefined}
				>
					{platform.label}
				</a>
			{/each}
		</nav>
	</div>
</section>

{#if projects.length > 0}
	<section class="reference-toolbar" aria-label="레퍼런스 정렬">
		<span>정렬</span>
		<nav>
			{#each sortItems as item}
				<a class:active={item.key === data.sort} href={`/references/${data.platform.key}?sort=${item.key}`}>
					{item.label}
				</a>
			{/each}
		</nav>
	</section>
{/if}

{#if data.error}
	<div class="notice">{data.error}</div>
{:else if visibleProjects.length > 0}
	<section class="reference-grid" aria-label="레퍼런스 카드 목록">
		{#each visibleProjects as project}
			<ProjectCard {project} />
		{/each}
	</section>

	{#if remainingCount > 0}
		<div class="load-more">
			<button type="button" onclick={showMore}>
				{Math.min(PAGE_SIZE, remainingCount)}개 더 보기
			</button>
			<span>{remainingCount}개 더 볼 수 있습니다.</span>
		</div>
	{:else}
		<div class="reference-end">모든 레퍼런스를 불러왔습니다.</div>
	{/if}
{:else}
	<div class="empty-panel">아직 표시할 Power BI 레퍼런스가 없습니다. 공개 레퍼런스가 준비되면 이곳에서 바로 살펴볼 수 있습니다.</div>
{/if}
