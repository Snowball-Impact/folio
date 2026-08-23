<script lang="ts">
	import { onMount } from 'svelte';
	import ProjectCard from '$lib/components/ProjectCard.svelte';
	import { formatCount, formatDate, plainTextFromHtml } from '$lib/format';
	import { recordProjectView } from '$lib/projects';
	import { getOrCreateVisitorId } from '$lib/visitor';

	let { data } = $props();
	const project = $derived(data.project);

	const reportSections = $derived(
		[
			['문제 정의', project.problem],
			['사용 데이터', project.dataset],
			['분석 및 시각화', project.process],
			['주요 관찰 포인트', project.insights]
		].filter((section): section is [string, string] => Boolean(section[1]))
	);

	const resourceLinks = $derived(
		[
			project.power_bi_url ? ['대시보드 열기', project.power_bi_url] : null,
			project.report_url ? ['보고서 보기', project.report_url] : null,
			project.github_url ? ['GitHub 보기', project.github_url] : null
		].filter((item): item is [string, string] => Boolean(item))
	);

	onMount(() => {
		const visitorId = getOrCreateVisitorId();
		recordProjectView(project.id, visitorId);
	});
</script>

<svelte:head>
	<title>{project.title} | FOLIO</title>
	<meta name="description" content={project.one_liner ?? project.title} />
</svelte:head>

<section class="detail-hero">
	<div>
		<div class="eyebrow">Project Detail</div>
		<h1>{project.title}</h1>
		<p>{project.one_liner ?? '프로젝트 소개가 없습니다.'}</p>
		<div class="detail-meta" aria-label="프로젝트 메타 정보">
			<span class="pill">작성자 {project.author.name ?? '작성자'}</span>
			{#if project.author.organization}
				<span class="pill">소속 {project.author.organization}</span>
			{/if}
			<span class="pill">등록일 {formatDate(project.created_at)}</span>
			<span class="pill">조회 {formatCount(project.view_count)}</span>
			<span class="pill">댓글 {formatCount(project.comment_count)}</span>
		</div>
	</div>
	<div class="detail-card-preview">
		<ProjectCard {project} />
	</div>
</section>

{#if project.status === 'processing'}
	<div class="visual-panel">Power BI 보고서를 게시하는 중입니다. 잠시 후 다시 확인하세요.</div>
{:else if project.status === 'failed'}
	<div class="visual-panel">Power BI 보고서 게시에 실패했습니다.</div>
{:else if project.power_bi_url}
	<section class="visual-panel">
		<h2>대표 결과물</h2>
		<iframe class="dashboard-frame" title={`${project.title} 대표 결과물`} src={project.power_bi_url}></iframe>
		{#if resourceLinks.length > 0}
			<div class="actions">
				{#each resourceLinks as [label, url], index}
					<a class:primary={index === 0} class="button-link" href={url} target="_blank" rel="noreferrer">
						{label}
					</a>
				{/each}
			</div>
		{/if}
	</section>
{/if}

{#if reportSections.length > 0}
	<article class="report">
		<h2>프로젝트 리포트</h2>
		{#each reportSections as [title, body]}
			<section class="report-section">
				<h3>{title}</h3>
				<p>{plainTextFromHtml(body)}</p>
			</section>
		{/each}
	</article>
{:else}
	<div class="empty-panel">아직 작성된 프로젝트 설명이 없습니다.</div>
{/if}

<div class="actions" style="justify-content: flex-end; margin-top: 24px;">
	<a class="button-link" href="/">홈 갤러리로 돌아가기</a>
</div>
