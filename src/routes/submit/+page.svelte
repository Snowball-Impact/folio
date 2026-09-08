<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import ProjectBodyEditor from '$lib/components/ProjectBodyEditor.svelte';
	import ProjectHeroThumbnailPreview from '$lib/components/ProjectHeroThumbnailPreview.svelte';
	import ProjectFormOverview from '$lib/components/ProjectFormOverview.svelte';
	import OperationProgress, { type OperationStep } from '$lib/components/OperationProgress.svelte';
	import { currentSession } from '$lib/auth';
	import type { ProjectSubmitInput } from '$lib/types';
	import { runProjectSaveWorkflow } from '$lib/projectSaveWorkflow';
	import {
		emptyProjectSubmitInput,
		previewTags,
		PROJECT_PLATFORM_OPTIONS
	} from '$lib/projectForm';
	import {
		stripPendingBodyImages,
		type PendingProjectBodyImage
	} from '$lib/projectBodyImages';
	import { PROJECT_BODY_TEMPLATE, parseProjectBody } from '$lib/projectBody';
	import type { ProjectCard as ProjectCardType } from '$lib/types';

	const platformOptions = PROJECT_PLATFORM_OPTIONS;

	let input = $state<ProjectSubmitInput>(emptyProjectSubmitInput());
	let message = $state('');
	let error = $state('');
	let submitting = $state(false);
	let thumbnailFile = $state<File | null>(null);
	let thumbnailPreviewUrl = $state<string | null>(null);
	let pbixFile = $state<File | null>(null);
	let bodyImageFiles = $state<PendingProjectBodyImage[]>([]);
	let authChecked = $state(false);
	let isAuthenticated = $state(false);
	let draftLoaded = $state(false);
	let draftStorageKey = $state('');
	let bodyHtml = $state(PROJECT_BODY_TEMPLATE);
	let skipNextDraftSave = false;
	let operationProgress = $state(0);
	let operationSteps = $state<OperationStep[]>([]);
	let pendingProjectRedirect = $state('');

	const previewProject = $derived<ProjectCardType>({
		id: 'submit-preview',
		author_id: '',
		title: input.title.trim() || '프로젝트명이 여기에 표시됩니다.',
		one_liner: input.one_liner.trim() || '프로젝트 한 줄 소개가 표시됩니다.',
		problem: input.problem,
		dataset: input.dataset,
		process: input.process,
		insights: input.insights,
		tags: previewTags(input.tags, input.platform),
		thumbnail_url:
			input.thumbnail_mode === 'manual_url'
				? input.thumbnail_url.trim() || null
				: input.thumbnail_mode === 'upload'
					? thumbnailPreviewUrl
					: input.thumbnail_mode === 'capture'
						? input.thumbnail_url.trim() || null
						: null,
		thumbnail_mode: input.thumbnail_mode,
		power_bi_url: input.power_bi_url.trim() || null,
		report_url: input.report_url.trim() || null,
		github_url: input.github_url.trim() || null,
		platform_key: input.platform === 'other' ? null : input.platform,
		project_type: input.platform === 'datastudio' ? 'looker' : input.platform === 'other' ? 'other' : input.platform,
		status: 'published',
		embed_status: input.power_bi_url.trim() ? 'supported' : 'external_only',
		is_public: true,
		view_count: 0,
		created_at: new Date().toISOString(),
		updated_at: new Date().toISOString(),
		author: { name: '작성자' },
		like_count: 0,
		comment_count: 0
	});

	$effect(() => {
		if (!draftLoaded || !draftStorageKey) {
			return;
		}
		if (skipNextDraftSave) {
			skipNextDraftSave = false;
			return;
		}
		localStorage.setItem(draftStorageKey, JSON.stringify(draftPayload(input, bodyHtml)));
	});

	onMount(async () => {
		const session = await currentSession();
		isAuthenticated = Boolean(session);
		if (session) {
			draftStorageKey = `folio-submit-draft:${session.user.id}:v1`;
			restoreDraft();
		}
		draftLoaded = true;
		authChecked = true;
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
		if (!isAuthenticated) {
			await goto('/login?next=/submit');
			return;
		}
		message = '';
		error = '';
		syncProjectBodyInput();
		if (input.thumbnail_mode === 'upload' && !thumbnailFile) {
			error = '업로드할 썸네일 이미지를 선택하세요.';
			return;
		}
		if (input.platform === 'powerbi' && input.power_bi_url.trim() === '' && !pbixFile) {
			error = 'Power BI 프로젝트는 Embed Code 또는 PBIX 파일 중 하나를 입력하세요.';
			return;
		}
		if (input.thumbnail_mode === 'capture' && !input.power_bi_url.trim() && !input.report_url.trim() && !pbixFile) {
			error = '자동 캡처를 사용하려면 Embed Code, Web App URL, 또는 PBIX 파일이 필요합니다.';
			return;
		}
		submitting = true;
		pendingProjectRedirect = '';
		const result = await runProjectSaveWorkflow({
			mode: 'create',
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
			if (result.projectSaved && result.projectId) {
				pendingProjectRedirect = `/projects/${result.projectId}`;
			}
			return;
		}
		submitting = false;
		message = result.message;
		pendingProjectRedirect = `/projects/${result.projectId}`;
		clearDraft({ keepMessage: true });
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

	function clearOperation() {
		operationProgress = 0;
		operationSteps = [];
	}

	async function dismissOperationProgress() {
		const redirectPath = pendingProjectRedirect;
		clearOperation();
		pendingProjectRedirect = '';
		if (redirectPath) {
			await goto(redirectPath);
		}
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

	function restoreDraft() {
		if (!draftStorageKey) {
			return;
		}
		const rawDraft = localStorage.getItem(draftStorageKey);
		if (!rawDraft) {
			return;
		}
		try {
			const draft = JSON.parse(rawDraft);
			input = { ...emptyProjectSubmitInput(), ...draft, is_public: true };
			bodyHtml = typeof draft.project_body === 'string' && draft.project_body.trim() ? draft.project_body : bodyHtml;
		} catch {
			localStorage.removeItem(draftStorageKey);
		}
	}

	function clearDraft(options: { keepMessage?: boolean } = {}) {
		if (draftStorageKey) {
			localStorage.removeItem(draftStorageKey);
		}
		skipNextDraftSave = true;
		if (thumbnailPreviewUrl) {
			URL.revokeObjectURL(thumbnailPreviewUrl);
		}
		input = emptyProjectSubmitInput();
		bodyHtml = PROJECT_BODY_TEMPLATE;
		releaseBodyImageFiles();
		thumbnailFile = null;
		thumbnailPreviewUrl = null;
		pbixFile = null;
		error = '';
		if (!options.keepMessage) {
			message = '';
		}
	}

	function draftPayload(value: ProjectSubmitInput, projectBody: string) {
		return {
			title: value.title,
			one_liner: value.one_liner,
			tags: value.tags,
			platform: value.platform,
			problem: value.problem,
			dataset: value.dataset,
			process: value.process,
			insights: value.insights,
			project_body: projectBody,
			power_bi_url: value.power_bi_url,
			report_url: value.report_url,
			github_url: value.github_url,
			thumbnail_url: value.thumbnail_url,
			thumbnail_mode: value.thumbnail_mode,
			delete_thumbnail: false,
			delete_pbix: false,
			is_public: true
		};
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
	<title>새 프로젝트 등록 | FOLIO</title>
	<meta name="description" content="FOLIO에 데이터 분석 프로젝트를 등록합니다." />
</svelte:head>

<section class="submit-hero submit-preview-hero">
	<div>
		<div class="eyebrow">Submit</div>
		<h1>새 프로젝트 등록</h1>
		<p>당신의 데이터 분석 프로젝트를 포트폴리오로 공개하세요.</p>
	</div>
	<ProjectHeroThumbnailPreview project={previewProject} />
</section>

{#if authChecked && !isAuthenticated}
	<section class="login-required-panel" aria-label="로그인 필요">
		<p>프로젝트를 등록하려면 로그인이 필요합니다.</p>
		<a class="primary" href="/login?next=/submit">로그인하기</a>
		<a href="/">홈으로</a>
	</section>
{:else if authChecked}
<form class="project-form" onsubmit={submitProject}>
	{#if message}
		<div class="auth-message success">{message}</div>
	{/if}
	{#if error}
		<div id="project-form-error" class="auth-message error" role="alert" aria-live="assertive">{error}</div>
	{/if}

	<div class="project-form-intro">
		<strong>프로젝트 정보를 작성해 주세요.</strong>
		<span>작성 내용은 이 브라우저에 자동 임시 저장됩니다.</span>
		<small><b>*</b> 필수 입력</small>
	</div>

	<ProjectFormOverview bind:input {platformOptions} onSelectThumbnail={selectThumbnail} onSelectPbix={selectPbix} />

	<section class="project-form-section">
		<header>
			<h2>프로젝트 내용</h2>
			<p>섹션 제목을 유지하면 상세 화면에서 분석 흐름이 깔끔하게 나뉩니다.</p>
		</header>
		<ProjectBodyEditor value={bodyHtml} onChange={updateProjectBody} onImageFile={selectBodyImage} />
	</section>

	<OperationProgress progress={operationProgress} steps={operationSteps} onDismiss={dismissOperationProgress} />

	<div class="project-form-actions">
		<button class="secondary-action" type="button" onclick={() => clearDraft()}>초안 지우기</button>
		<button type="submit" disabled={submitting}>{submitting ? '등록 중...' : '프로젝트 등록하기'}</button>
	</div>
</form>
{/if}
