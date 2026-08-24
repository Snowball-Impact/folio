<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { currentSession } from '$lib/auth';
	import ProjectCard from '$lib/components/ProjectCard.svelte';
	import ProjectComments from '$lib/components/ProjectComments.svelte';
	import ProjectLikeButton from '$lib/components/ProjectLikeButton.svelte';
	import PowerBIReport from '$lib/components/PowerBIReport.svelte';
	import { formatCount, formatDate, plainTextFromHtml } from '$lib/format';
	import { deleteProject, recordProjectView } from '$lib/projects';
	import { PROJECT_REPORT_REASONS, submitProjectReport, type ProjectReportReason } from '$lib/projectReports';
	import type { PowerBIEmbedConfig } from '$lib/types';
	import { getOrCreateVisitorId } from '$lib/visitor';

	let { data } = $props();
	const project = $derived(data.project);
	let embedConfig = $state<PowerBIEmbedConfig | null>(null);
	let embedError = $state('');
	let embedLoading = $state(false);
	let authenticated = $state(false);
	let isOwner = $state(false);
	let shareMessage = $state('');
	let reportOpen = $state(false);
	let reportReason = $state<ProjectReportReason>('embed_broken');
	let reportDetails = $state('');
	let reportSubmitting = $state(false);
	let reportMessage = $state('');
	let deleteConfirm = $state(false);
	let deleteSubmitting = $state(false);
	let actionMessage = $state('');

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

	onMount(async () => {
		const visitorId = getOrCreateVisitorId();
		recordProjectView(project.id, visitorId);

		const session = await currentSession();
		authenticated = Boolean(session);
		isOwner = session?.user.id === project.author_id;

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

	async function shareProject() {
		const url = `${window.location.origin}/projects/${project.id}?utm_source=folio&utm_medium=share&utm_campaign=project_share`;
		try {
			await navigator.clipboard.writeText(url);
			shareMessage = '프로젝트 링크를 복사했습니다.';
		} catch {
			shareMessage = url;
		}
		setTimeout(() => {
			shareMessage = '';
		}, 2600);
	}

	function openReport() {
		if (!authenticated) {
			reportMessage = '로그인 후 신고할 수 있습니다.';
			return;
		}
		reportOpen = !reportOpen;
		reportMessage = '';
	}

	async function submitReport() {
		reportSubmitting = true;
		reportMessage = '';
		const result = await submitProjectReport({
			projectId: project.id,
			reason: reportReason,
			details: reportDetails
		});
		reportSubmitting = false;
		reportMessage = result.message;
		if (result.ok) {
			reportOpen = false;
			reportDetails = '';
		}
	}

	async function removeProject() {
		if (!deleteConfirm) {
			deleteConfirm = true;
			actionMessage = '한 번 더 누르면 프로젝트가 삭제됩니다.';
			return;
		}
		deleteSubmitting = true;
		const result = await deleteProject(project.id);
		deleteSubmitting = false;
		if (!result.ok) {
			actionMessage = result.message;
			return;
		}
		await goto('/my');
	}
</script>

<svelte:head>
	<title>{project.title} | FOLIO</title>
	<meta name="description" content={project.one_liner ?? project.title} />
</svelte:head>

<section class="detail-hero project-detail-image-hero">
	<div class="detail-hero-copy">
		<div class="detail-hero-eyebrow">프로젝트 상세</div>
		<h1>{project.title}</h1>
		<p>{project.one_liner ?? '프로젝트 소개가 없습니다.'}</p>
	</div>
	<div class="detail-card-preview">
		<ProjectCard {project} />
	</div>
</section>

<section class="detail-footer-row" aria-label="프로젝트 메타 및 액션">
	<div class="detail-meta" aria-label="프로젝트 메타 정보">
		<span class="pill">작성자 {project.author.name ?? '작성자'}</span>
		{#if project.author.organization}
			<span class="pill">소속 {project.author.organization}</span>
		{/if}
		<span class="pill">등록일 {formatDate(project.created_at)}</span>
		<span class="pill">조회 {formatCount(project.view_count)}</span>
		<span class="pill">좋아요 {formatCount(project.like_count)}</span>
		<span class="pill">댓글 {formatCount(project.comment_count)}</span>
	</div>
	<div class="detail-action-bar">
		<div class="detail-action-primary">
			<ProjectLikeButton projectId={project.id} initialLikeCount={project.like_count} />
		</div>
		<div class="detail-action-group">
			<button type="button" class="button-link" onclick={shareProject}>링크 복사</button>
			{#if isOwner}
				<a class="button-link" href={`/projects/${project.id}/edit`}>수정</a>
				<button type="button" class:danger={deleteConfirm} disabled={deleteSubmitting} onclick={removeProject}>
					{deleteConfirm ? '삭제 확인' : '삭제'}
				</button>
				{#if deleteConfirm}
					<button type="button" class="button-link" onclick={() => { deleteConfirm = false; actionMessage = ''; }}>취소</button>
				{/if}
			{:else}
				<button type="button" class="button-link" onclick={openReport}>신고</button>
			{/if}
		</div>
	</div>
	{#if shareMessage || reportMessage || actionMessage}
		<div class="detail-action-message">{shareMessage || reportMessage || actionMessage}</div>
	{/if}
	{#if reportOpen && !isOwner}
		<div class="detail-report-modal" role="presentation" onclick={(event) => { if (event.target === event.currentTarget) reportOpen = false; }}>
			<form class="detail-report-form" aria-label="콘텐츠 신고" onsubmit={(event) => { event.preventDefault(); submitReport(); }}>
				<label>
					신고 사유
					<select bind:value={reportReason}>
						{#each PROJECT_REPORT_REASONS as [value, label]}
							<option value={value}>{label}</option>
						{/each}
					</select>
				</label>
				<label>
					상세 내용
					<textarea bind:value={reportDetails} maxlength="500" placeholder="운영자가 확인할 수 있도록 필요한 내용을 적어주세요."></textarea>
				</label>
				<div class="detail-report-actions">
					<button type="button" class="button-link" onclick={() => (reportOpen = false)}>취소</button>
					<button type="submit" disabled={reportSubmitting}>신고 접수</button>
				</div>
			</form>
		</div>
	{/if}
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

<ProjectComments
	projectId={project.id}
	projectAuthorId={project.author_id}
	projectTitle={project.title}
	initialCommentCount={project.comment_count}
/>

<div class="actions" style="justify-content: flex-end; margin-top: 24px;">
	<a class="button-link" href="/">홈 갤러리로 돌아가기</a>
</div>