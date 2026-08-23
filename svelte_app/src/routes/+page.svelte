<script lang="ts">
	import ProjectRail from '$lib/components/ProjectRail.svelte';
	import { formatCount } from '$lib/format';

	let { data } = $props();
	const snapshot = $derived(data.snapshot);
</script>

<svelte:head>
	<title>FOLIO</title>
	<meta
		name="description"
		content="좋은 데이터 시각화 프로젝트를 발견하고 직접 경험하는 FOLIO 공개 갤러리"
	/>
</svelte:head>

<section class="hero">
	<div>
		<div class="eyebrow">Project Portfolio Platform</div>
		<h1>좋은 시각화를 발견하고,<br />직접 경험하세요.</h1>
		<p>FOLIO는 Power BI 프로젝트와 데이터 시각화 레퍼런스를 빠르게 살펴보는 공개 갤러리입니다.</p>
	</div>
	<div class="hero-panel" aria-label="홈 프로젝트 요약">
		<div class="hero-metric">
			<span>Power BI 프로젝트</span>
			<strong>{formatCount(snapshot.total_project_count)}</strong>
		</div>
		<div class="hero-metric">
			<span>인기 태그</span>
			<strong>{snapshot.popular_tags.length}</strong>
		</div>
	</div>
</section>

{#if data.error}
	<div class="notice">{data.error}</div>
{/if}

<ProjectRail
	title="새로 공개된 프로젝트"
	description="최근 등록된 Power BI 프로젝트를 먼저 살펴보세요."
	projects={snapshot.recent_projects}
/>

<ProjectRail
	title="조회수가 높은 프로젝트"
	description="많이 열린 프로젝트를 빠르게 훑어보세요."
	projects={snapshot.viewed_projects}
/>

<ProjectRail
	title="좋아요를 받은 프로젝트"
	description="반응이 쌓인 프로젝트를 이어서 확인해보세요."
	projects={snapshot.liked_projects}
/>
