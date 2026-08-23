<script lang="ts">
	import { onMount } from 'svelte';
	import ProjectCard from '$lib/components/ProjectCard.svelte';
	import PowerBIReport from '$lib/components/PowerBIReport.svelte';
	import { formatCount, formatDate, plainTextFromHtml } from '$lib/format';
	import { recordProjectView } from '$lib/projects';
	import type { PowerBIEmbedConfig } from '$lib/types';
	import { getOrCreateVisitorId } from '$lib/visitor';

	let { data } = $props();
	const project = $derived(data.project);
	let embedConfig = $state<PowerBIEmbedConfig | null>(null);
	let embedError = $state('');
	let embedLoading = $state(false);

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

	const shouldLoadPowerBIEmbed = $derived(
		project.status === 'published' && project.project_type === 'powerbi'
	);

	onMount(() => {
		const visitorId = getOrCreateVisitorId();
		recordProjectView(project.id, visitorId);

		if (shouldLoadPowerBIEmbed) {
			loadPowerBIEmbedConfig();
		}
	});

	async function loadPowerBIEmbedConfig() {
		embedLoading = true;
		try {
			const response = await fetch(`/api/projects/${project.id}/powerbi-embed`);
			if (!response.ok) {
				const payload = (await response.json().catch(() => ({}))) as { error?: string };
				embedError = payload.error || 'Power BI 보고서를 불러오지 못했습니다.';
				return;
			}
			embedConfig = (await response.json()) as PowerBIEmbedConfig;
		} catch {
			embedError = 'Power BI 보고서를 불러오지 못했습니다.';
		} finally {
			embedLoading = false;
		}
	}
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
{:else if shouldLoadPowerBIEmbed || project.power_bi_url}
	<section class="visual-panel">
		<h2>대표 결과물</h2>
		{#if embedConfig}
			<PowerBIReport config={embedConfig} title={project.title} />
			<p class="visual-caption">Power BI Embed Token은 요청 시 발급되며 저장하지 않습니다.</p>
		{:else if project.power_bi_url}
			<iframe class="dashboard-frame" title={`${project.title} 대표 결과물`} src={project.power_bi_url}></iframe>
			<p class="visual-caption">
				{embedLoading
					? 'Power BI 임베드 토큰을 확인하는 중입니다.'
					: embedError || '화면이 표시되지 않으면 원본 대시보드를 새 탭에서 확인하세요.'}
			</p>
		{:else}
			<div class="embed-empty">
				{embedLoading ? 'Power BI 임베드 토큰을 확인하는 중입니다.' : embedError || '표시할 대시보드가 없습니다.'}
			</div>
		{/if}
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
