<script lang="ts">
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import { onMount } from 'svelte';
	import ProjectBodyEditor from '$lib/components/ProjectBodyEditor.svelte';
	import ProjectHeroThumbnailPreview from '$lib/components/ProjectHeroThumbnailPreview.svelte';
	import ProjectFormOverview from '$lib/components/ProjectFormOverview.svelte';
	import OperationProgress, { type OperationStep } from '$lib/components/OperationProgress.svelte';
	import { currentSession } from '$lib/auth';
	import { projectPbixExists } from '$lib/powerbi-publish';
	import { loadMyProject } from '$lib/projects';
	import type { ProjectSubmitInput } from '$lib/types';
	import { runProjectSaveWorkflow } from '$lib/projectSaveWorkflow';
	import {
		emptyProjectSubmitInput,
		previewTags,
		projectInputFromProject,
		PROJECT_PLATFORM_OPTIONS
	} from '$lib/projectForm';
	import { captureProjectThumbnail, deleteProjectThumbnail, uploadProjectThumbnail } from '$lib/thumbnails';
	import {
		stripPendingBodyImages,
		type PendingProjectBodyImage
	} from '$lib/projectBodyImages';
	import { parseProjectBody, projectBodyFromSections, PROJECT_BODY_TEMPLATE } from '$lib/projectBody';
	import type { ProjectCard as ProjectCardType } from '$lib/types';

	const platformOptions = PROJECT_PLATFORM_OPTIONS;

	let project = $state<ProjectCardType | null>(null);
	let input = $state<ProjectSubmitInput>(emptyProjectSubmitInput());
	let loading = $state(true);
	let message = $state('');
	let error = $state('');
	let submitting = $state(false);
	let thumbnailFile = $state<File | null>(null);
	let thumbnailPreviewUrl = $state<string | null>(null);
	let pbixFile = $state<File | null>(null);
	let bodyImageFiles = $state<PendingProjectBodyImage[]>([]);
	let hasPowerbiReport = $state(false);
	let bodyHtml = $state(PROJECT_BODY_TEMPLATE);
	let operationProgress = $state(0);
	let operationSteps = $state<OperationStep[]>([]);
	const projectId = $derived(page.params.id ?? '');

	const previewProject = $derived<ProjectCardType>({
		id: projectId,
		author_id: project?.author_id ?? '',
		title: input.title.trim() || '프로젝트명이 여기에 표시됩니다.',
		one_liner: input.one_liner.trim() || '프로젝트 한 줄 소개가 표시됩니다.',
		problem: input.problem,
		dataset: input.dataset,
		process: input.process,
		insights: input.insights,
		tags: previewTags(input.tags, input.platform),
		thumbnail_url:
			input.delete_thumbnail
				? null
				: input.thumbnail_mode === 'manual_url'
					? input.thumbnail_url.trim() || null
					: input.thumbnail_mode === 'upload'
						? (thumbnailPreviewUrl ?? input.thumbnail_url.trim()) || null
						: input.thumbnail_mode === 'capture'
							? input.thumbnail_url.trim() || null
							: null,
		thumbnail_mode: input.delete_thumbnail ? 'auto_cover' : input.thumbnail_mode,
		power_bi_url: input.delete_pbix ? null : input.power_bi_url.trim() || null,
		report_url: input.report_url.trim() || null,
		github_url: input.github_url.trim() || null,
		platform_key: input.platform === 'other' ? null : input.platform,
		project_type: input.platform === 'datastudio' ? 'looker' : input.platform === 'other' ? 'other' : input.platform,
		status: 'published',
		embed_status: !input.delete_pbix && input.power_bi_url.trim() ? 'supported' : 'external_only',
		is_public: input.is_public,
		view_count: project?.view_count ?? 0,
		created_at: project?.created_at ?? new Date().toISOString(),
		updated_at: project?.updated_at ?? new Date().toISOString(),
		author: project?.author ?? { name: '작성자' },
		like_count: project?.like_count ?? 0,
		comment_count: project?.comment_count ?? 0
	});

	onMount(async () => {
		const session = await currentSession();
		if (!session) {
			await goto(`/login?next=/projects/${projectId}/edit`);
			return;
		}
		const result = await loadMyProject(projectId);
		if (!result.project) {
			error = result.error;
			loading = false;
			return;
		}
		project = result.project;
		hasPowerbiReport = Boolean(result.project.power_bi_url);
		if (result.project.project_type === 'powerbi') {
			hasPowerbiReport = (await projectPbixExists(projectId)) || hasPowerbiReport;
		}
		input = projectInputFromProject(result.project);
		bodyHtml = projectBodyFromSections(input);
		loading = false;
	});

	function syncProjectBodyInput() {
		const sections = parseProjectBody(stripPendingBodyImages(bodyHtml, bodyImageFiles));
		input.problem = sections.problem;
		input.dataset = sections.dataset;
		input.process = sections.process;
		input.insights = sections.insights;
	}
	async function submitProject(event: SubmitEvent) {
		event.preventDefault();
		message = '';
		error = '';
		syncProjectBodyInput();
		if (input.thumbnail_mode === 'upload' && !thumbnailFile && !input.delete_thumbnail) {
			error = '업로드할 썸네일 이미지를 선택하세요.';
			return;
		}
		if (input.platform === 'powerbi' && input.power_bi_url.trim() === '' && !pbixFile && !input.delete_pbix) {
			error = 'Power BI 프로젝트는 Embed Code 또는 PBIX 파일 중 하나를 입력하세요.';
			return;
		}
		if (input.thumbnail_mode === 'capture' && !input.power_bi_url.trim() && !input.report_url.trim() && !pbixFile && !input.delete_thumbnail) {
			error = '자동 캡처를 사용하려면 Embed Code, Web App URL, 또는 PBIX 파일이 필요합니다.';
			return;
		}
		submitting = true;
		const result = await runProjectSaveWorkflow({
			mode: 'edit',
			projectId,
			input,
			bodyHtml,
			bodyImageFiles,
			thumbnailFile,
			pbixFile,
			setBodyHtml: (html) => (bodyHtml = html),
			syncProjectBodyInput,
			releaseBodyImageFiles,
			startOperation,
			setOperationStep,
			failOperation
		});
		if (!result.ok) {
			submitting = false;
			error = result.message;
			return;
		}
		submitting = false;
		message = result.message;
		await goto(`/projects/${result.projectId}`);
	}


	function startOperation(steps: OperationStep[]) {
		operationProgress = 10;
		operationSteps = steps;
	}


	function failOperation(detail = '작업 처리 중 문제가 발생했습니다.') {
		const activeIndex = operationSteps.findIndex((step) => step.status === 'active');
		const fallbackIndex = operationSteps.findIndex((step) => step.status === 'pending');
		const failedIndex = activeIndex >= 0 ? activeIndex : fallbackIndex;
		if (failedIndex < 0) {
			return;
		}
		operationProgress = Math.max(operationProgress, 10);
		operationSteps = operationSteps.map((step, index) =>
			index === failedIndex ? { ...step, status: 'error', detail } : step
		);
	}
	function setOperationStep(id: string, progress: number, detail: string) {
		const activeIndex = operationSteps.findIndex((step) => step.id === id);
		operationProgress = progress;
		operationSteps = operationSteps.map((step, index) => ({
			...step,
			detail: step.id === id ? detail : step.detail,
			status: activeIndex < 0 ? step.status : index < activeIndex ? 'done' : step.id === id ? 'active' : 'pending'
		}));
	}
	function selectThumbnail(event: Event) {
		const file = (event.currentTarget as HTMLInputElement).files?.[0] ?? null;
		if (thumbnailPreviewUrl) {
			URL.revokeObjectURL(thumbnailPreviewUrl);
		}
		thumbnailFile = file;
		thumbnailPreviewUrl = file ? URL.createObjectURL(file) : null;
	}

	function selectPbix(event: Event) {
		pbixFile = (event.currentTarget as HTMLInputElement).files?.[0] ?? null;
	}

	function selectBodyImage(file: File, objectUrl: string) {
		bodyImageFiles = [...bodyImageFiles, { file, objectUrl }];
	}

	function releaseBodyImageFiles() {
		for (const image of bodyImageFiles) {
			URL.revokeObjectURL(image.objectUrl);
		}
		bodyImageFiles = [];
	}


	function updateProjectBody(html: string) {
		bodyHtml = html;
		const sections = parseProjectBody(html);
		input.problem = sections.problem;
		input.dataset = sections.dataset;
		input.process = sections.process;
		input.insights = sections.insights;
	}
</script>

<svelte:head>
	<title>{project?.title ?? '프로젝트 수정'} | FOLIO</title>
	<meta name="description" content="FOLIO 프로젝트 정보를 수정합니다." />
</svelte:head>

{#if loading}
	<div class="comments-empty">프로젝트 정보를 불러오는 중입니다.</div>
{:else if error && !project}
	<div class="auth-message error">{error}</div>
	<a class="button-link" href="/my">마이 페이지로 돌아가기</a>
{:else}
	<section class="submit-hero edit-hero">
		<div>
			<div class="eyebrow">Edit</div>
			<h1>프로젝트 수정</h1>
			<p>프로젝트 정보와 대표 썸네일을 업데이트하세요.</p>
		</div>
		<ProjectHeroThumbnailPreview project={previewProject} />
	</section>

	<form class="project-form" onsubmit={submitProject}>
		{#if message}
			<div class="auth-message success">{message}</div>
		{/if}
		{#if error}
			<div id="project-form-error" class="auth-message error" role="alert" aria-live="assertive">{error}</div>
		{/if}

		<OperationProgress progress={operationProgress} steps={operationSteps} />

		<ProjectFormOverview
			bind:input
			{platformOptions}
			onSelectThumbnail={selectThumbnail}
			onSelectPbix={selectPbix}
			hasPowerbiReport={hasPowerbiReport}
			hasExistingThumbnail={Boolean(project?.thumbnail_url)}
		/>

		<section class="project-form-section">
			<header>
				<h2>프로젝트 내용</h2>
				<p>섹션 제목을 유지하면 상세 화면에서 분석 흐름이 깔끔하게 나뉩니다.</p>
			</header>
			<ProjectBodyEditor value={bodyHtml} onChange={updateProjectBody} onImageFile={selectBodyImage} />
		</section>

		<div class="project-form-final-row">
			<div class="visibility-setting-card">
				<div class="visibility-setting-copy">
					<strong>공개 설정</strong>
					<span>공개를 끄면 목록과 검색에서 숨겨지고 작성자만 볼 수 있습니다.</span>
				</div>
				<label class="switch-row">
					<input type="checkbox" bind:checked={input.is_public} />
					<span>프로젝트 공개</span>
				</label>
			</div>
			<div class="project-form-actions">
				<a class="button-link" href="/my">목록으로 돌아가기</a>
				<button type="submit" disabled={submitting}>{submitting ? '수정 중...' : '수정 완료'}</button>
			</div>
		</div>
	</form>
{/if}
