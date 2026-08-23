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
	<div>
		<div class="eyebrow">Reference Library</div>
		<h1>
			<span>{formatCount(projects.length)}</span>
			개의 레퍼런스를 참고해보세요.
		</h1>
		<p>{data.platform.description}</p>
	</div>
	<div class="reference-visual" aria-label="Power BI">
		<img src="/reference-powerbi-logo-cropped.webp" alt="" />
		<span>Reports</span>
		<span>Dashboards</span>
	</div>
</section>

<section class="reference-toolbar" aria-label="레퍼런스 정렬">
	<span>정렬</span>
	<nav>
		{#each sortItems as item}
			<a class:active={item.key === data.sort} href={`/references/powerbi?sort=${item.key}`}>
				{item.label}
			</a>
		{/each}
	</nav>
</section>

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
	<div class="empty-panel">아직 표시할 레퍼런스가 없습니다.</div>
{/if}
