<script lang="ts">
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import { onMount } from 'svelte';
	import { currentSession } from '$lib/auth';
	import ProjectCard from '$lib/components/ProjectCard.svelte';
	import ProjectComments from '$lib/components/ProjectComments.svelte';
	import ProjectLikeButton from '$lib/components/ProjectLikeButton.svelte';
	import PowerBIReport from '$lib/components/PowerBIReport.svelte';
	import { formatCount, formatDate } from '$lib/format';
	import ProjectRichContent from '$lib/components/ProjectRichContent.svelte';
	import { deleteProject, normalizePowerBIEmbedUrl, recordProjectView } from '$lib/projects';
	import { PROJECT_REPORT_REASONS, submitProjectReport, type ProjectReportReason } from '$lib/projectReports';
	import type { PowerBIEmbedConfig } from '$lib/types';
	import { getOrCreateVisitorId } from '$lib/visitor';

	let { data } = $props();
	const project = $derived(data.project);
	let embedConfig = $state<PowerBIEmbedConfig | null>(null);
	let embedError = $state('');
	let embedLoading = $state(false);
	let powerBIStatus = $state<'loading' | 'ready' | 'error'>('loading');
	let authenticated = $state(false);
	let isOwner = $state(false);
	let shareLabel = $state('링크 복사');
	let reportOpen = $state(false);
	let reportReason = $state<ProjectReportReason>('embed_broken');
	let reportDetails = $state('');
	let reportSubmitting = $state(false);
	let reportMessage = $state('');
	let deleteDialogOpen = $state(false);
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

	const dashboardUrl = $derived(normalizePowerBIEmbedUrl(project.power_bi_url));
	const resourceActions = $derived([
		{ label: '대시보드 열기 ↗', url: dashboardUrl },
		{ label: '보고서 보기 ↗', url: project.report_url },
		{ label: 'GitHub 보기 ↗', url: project.github_url }
	]);

	const shouldLoadPowerBIEmbed = $derived(
		project.status === 'published' && project.project_type === 'powerbi'
	);
	const hasDashboardUrl = $derived(Boolean(dashboardUrl));
	const hasExternalResource = $derived(Boolean(project.report_url || project.github_url));
	const canRenderDashboardFrame = $derived(hasDashboardUrl);
	const hasVisualOutput = $derived(true);
	const isTableauOutput = $derived(
		project.platform_key === 'tableau' ||
		project.project_type === 'tableau' ||
		(dashboardUrl ?? '').includes('public.tableau.com')
	);
	const isExternalOnlyOutput = $derived(project.embed_status === 'external_only' && !canRenderDashboardFrame);
	const isEmbedFailedOutput = $derived(
		project.embed_status === 'failed' ||
		Boolean(embedError) ||
		(powerBIStatus === 'error' && !hasDashboardUrl)
	);

	const backPlatform = $derived(normalizeBackPlatform(page.url.searchParams.get('platform')));
	const fromReferences = $derived(page.url.searchParams.get('from') === 'references');
	const backHref = $derived(fromReferences ? `/references/${backPlatform}` : '/');
	const backLabel = $derived(fromReferences ? '레퍼런스로 돌아가기' : '홈 갤러리로 돌아가기');

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
		powerBIStatus = 'loading';
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
		const target = new URL(window.location.origin + '/');
		target.searchParams.set('page', 'Home');
		target.searchParams.set('project_id', project.id);
		target.searchParams.set('utm_source', 'folio');
		target.searchParams.set('utm_medium', 'share');
		target.searchParams.set('utm_campaign', 'project_share');
		try {
			await copyText(target.toString());
			shareLabel = '복사 완료';
		} catch {
			shareLabel = '복사 실패';
		}
		setTimeout(() => {
			shareLabel = '링크 복사';
		}, 1600);
	}

	async function copyText(value: string) {
		if (navigator.clipboard?.writeText) {
			await navigator.clipboard.writeText(value);
			return;
		}

		const input = document.createElement('textarea');
		input.value = value;
		input.setAttribute('readonly', '');
		input.style.position = 'fixed';
		input.style.left = '-9999px';
		document.body.appendChild(input);
		input.select();
		const copied = document.execCommand('copy');
		document.body.removeChild(input);
		if (!copied) {
			throw new Error('copy failed');
		}
	}

	function normalizeBackPlatform(platform: string | null) {
		return ['powerbi', 'tableau', 'datastudio', 'streamlit'].includes(platform ?? '') ? (platform as string) : 'powerbi';
	}

	async function openReport() {
		if (!authenticated) {
			await goto(`/login?next=${encodeURIComponent(`/projects/${project.id}`)}`);
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

	function openDeleteDialog() {
		deleteDialogOpen = true;
		actionMessage = '';
	}

	function closeDeleteDialog() {
		if (!deleteSubmitting) {
			deleteDialogOpen = false;
		}
	}

	async function confirmProjectDeletion() {
		deleteSubmitting = true;
		actionMessage = '';
		const result = await deleteProject(project.id);
		deleteSubmitting = false;
		if (!result.ok) {
			actionMessage = result.message;
			return;
		}
		deleteDialogOpen = false;
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
		<ProjectCard {project} compact />
	</div>
</section>

<section class="detail-footer-row" aria-label="프로젝트 메타 및 액션">
	<div class="detail-meta" aria-label="프로젝트 메타 정보">
		<span class="pill meta-line">작성자 {project.author.name ?? '작성자'}</span>
		{#if project.author.organization}
			<span class="pill meta-line">소속 {project.author.organization}</span>
		{/if}
		<span class="pill meta-line">등록일 {formatDate(project.created_at)}</span>
		<span class="pill metric-pill">조회 {formatCount(project.view_count)}</span>
		<span class="pill metric-pill">좋아요 {formatCount(project.like_count)}</span>
		<span class="pill metric-pill">댓글 {formatCount(project.comment_count)}</span>
		<span class="pill visibility-pill">{project.is_public ? '공개' : '비공개'}</span>
	</div>
	<div class="detail-action-bar">
		<div class="detail-action-group">
			<button type="button" class="button-link share-button" aria-label="공유 링크 복사" onclick={shareProject}>
				<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
					<path d="M10 13a5 5 0 0 0 7.07 0l2.83-2.83a5 5 0 0 0-7.07-7.07L11.5 4.43"></path>
					<path d="M14 11a5 5 0 0 0-7.07 0L4.1 13.83a5 5 0 0 0 7.07 7.07l1.33-1.33"></path>
				</svg>
				<span>{shareLabel}</span>
			</button>
			<ProjectLikeButton projectId={project.id} initialLikeCount={project.like_count} />
			{#if isOwner}
				<a class="button-link" href={`/projects/${project.id}/edit`}>수정</a>
				<button type="button" class="danger" disabled={deleteSubmitting} onclick={openDeleteDialog}>삭제</button>
			{:else}
				<button type="button" class="button-link" onclick={openReport}>신고</button>
			{/if}
		</div>
	</div>
	{#if reportMessage || actionMessage}
		<div class="detail-action-message">{reportMessage || actionMessage}</div>
	{/if}
	{#if reportOpen && !isOwner}
		<div class="detail-report-modal" role="presentation" onclick={(event) => { if (event.target === event.currentTarget) reportOpen = false; }}>
			<form class="detail-report-form" aria-label="콘텐츠 신고" onsubmit={(event) => { event.preventDefault(); submitReport(); }}>
				<header>
					<h2>콘텐츠 신고</h2>
					<p>‘{project.title || '제목 없는 프로젝트'}’ 콘텐츠에 어떤 문제가 있나요?</p>
				</header>
				<label>
					신고 사유
					<select bind:value={reportReason}>
						{#each PROJECT_REPORT_REASONS as [value, label]}
							<option value={value}>{label}</option>
						{/each}
					</select>
				</label>
				<label>
					메모
					<textarea bind:value={reportDetails} maxlength="500" placeholder="예: 임베딩 영역이 비어 있거나, 보고서 보기 링크가 열리지 않아요."></textarea>
				</label>
				<div class="detail-report-actions">
					<button type="button" class="button-link" onclick={() => (reportOpen = false)}>취소</button>
					<button type="submit" disabled={reportSubmitting}>신고 접수</button>
				</div>
			</form>
		</div>
	{/if}
	{#if deleteDialogOpen && isOwner}
		<div class="detail-report-modal" role="presentation" onclick={(event) => { if (event.target === event.currentTarget) closeDeleteDialog(); }}>
			<div class="detail-delete-dialog" role="dialog" aria-modal="true" aria-labelledby="detail-delete-title" aria-describedby="detail-delete-description">
				<header>
					<h2 id="detail-delete-title">프로젝트 삭제</h2>
				</header>
				<p id="detail-delete-description"><strong>‘{project.title || '제목 없는 프로젝트'}’</strong> 프로젝트를 삭제할까요?</p>
				<span>삭제한 프로젝트는 복구할 수 없습니다.</span>
				<div class="detail-report-actions">
					<button type="button" class="button-link" disabled={deleteSubmitting} onclick={closeDeleteDialog}>취소</button>
					<button type="button" disabled={deleteSubmitting} onclick={confirmProjectDeletion}>{deleteSubmitting ? '삭제 중...' : '삭제하기'}</button>
				</div>
			</div>
		</div>
	{/if}
</section>


{#if hasVisualOutput}
	<section
		id="project-output"
		class="visual-panel"
		class:tableau-output={isTableauOutput}
		class:external-only-output={isExternalOnlyOutput}
		class:embed-failed-output={isEmbedFailedOutput || project.status === 'failed'}
	>
		<div class="visual-panel-head">
			<h2>대표 결과물</h2>
		</div>
		{#if project.status === 'processing'}
			<div class="embed-empty embed-loading-state">Power BI 보고서를 게시하는 중입니다. 잠시 후 다시 확인하세요.</div>
		{:else if project.status === 'failed'}
			<div class="embed-empty embed-failed-state">Power BI 보고서 게시에 실패했습니다. 프로젝트 작성자는 마이페이지에서 상태를 확인하세요.</div>
		{:else if embedConfig && powerBIStatus !== 'error'}
			<PowerBIReport
				config={embedConfig}
				title={project.title}
				onStatusChange={(status) => (powerBIStatus = status)}
			/>
			<p class="visual-caption">Power BI Embed Token은 요청 시 발급되며 저장하지 않습니다.</p>
		{:else if embedLoading && !dashboardUrl}
			<div class="embed-empty embed-loading-state">Power BI 임베드 토큰을 확인하는 중입니다.</div>
		{:else if canRenderDashboardFrame && dashboardUrl}
			<iframe class="dashboard-frame" title={`${project.title} 대표 결과물`} src={dashboardUrl}></iframe>
			<p class="visual-caption">화면이 표시되지 않으면 원본 대시보드를 새 탭에서 확인하세요.</p>
		{:else if project.embed_status === 'failed' || embedError}
			<div class="embed-empty embed-failed-state">
				{embedError || 'Power BI 보고서를 불러오지 못했습니다. 프로젝트 작성자는 마이페이지에서 상태를 확인하세요.'}
			</div>
		{:else if hasExternalResource}
			<div class="embed-empty embed-external-state">연결된 산출물을 새 탭에서 확인하세요.</div>
		{:else}
			<div class="embed-empty">표시할 대시보드가 없습니다.</div>
		{/if}
		<div class="actions" aria-label="외부 산출물 링크">
			{#each resourceActions as action}
				{#if action.url}
					<a class="button-link" href={action.url} target="_blank" rel="noreferrer">
						{action.label}
					</a>
				{:else}
					<button type="button" class="button-link" disabled aria-disabled="true">
						{action.label}
					</button>
				{/if}
			{/each}
		</div>
	</section>
{/if}

{#if reportSections.length > 0}
	<article id="project-report" class="report">
		<div class="report-head">
			<h2>프로젝트 리포트</h2>
		</div>
		{#each reportSections as [, body]}
			<section class="report-section">
				<div class="report-section-content"><ProjectRichContent html={body} emptyMessage="아직 작성된 프로젝트 설명이 없습니다." /></div>
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

<div class="detail-back-action-row">
	<a class="button-link" href={backHref}>← {backLabel}</a>
</div>
