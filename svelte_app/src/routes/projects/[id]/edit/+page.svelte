<script lang="ts">
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import { onMount } from 'svelte';
	import ProjectBodyEditor from '$lib/components/ProjectBodyEditor.svelte';
	import ProjectHeroThumbnailPreview from '$lib/components/ProjectHeroThumbnailPreview.svelte';
	import ProjectFormOverview from '$lib/components/ProjectFormOverview.svelte';
	import OperationProgress, { type OperationStep } from '$lib/components/OperationProgress.svelte';
	import { currentSession } from '$lib/auth';
	import { projectPbixExists, publishProjectPbix, unlinkProjectPbix } from '$lib/powerbi-publish';
	import { loadMyProject, updateProject, type ProjectSubmitInput } from '$lib/projects';
	import { captureProjectThumbnail, deleteProjectThumbnail, uploadProjectThumbnail } from '$lib/thumbnails';
	import {
		replacePendingBodyImages,
		stripPendingBodyImages,
		uploadProjectBodyImages,
		type PendingProjectBodyImage
	} from '$lib/projectBodyImages';
	import { parseProjectBody, projectBodyFromSections, PROJECT_BODY_TEMPLATE } from '$lib/projectBody';
	import type { ProjectCard as ProjectCardType } from '$lib/types';

	const platformOptions = [
		{ key: 'other', label: '기타' },
		{ key: 'tableau', label: 'Tableau' },
		{ key: 'powerbi', label: 'Power BI' },
		{ key: 'datastudio', label: 'Data Studio' },
		{ key: 'streamlit', label: 'Streamlit' }
	] as const;

	let project = $state<ProjectCardType | null>(null);
	let input = $state<ProjectSubmitInput>(emptyInput());
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
		input = inputFromProject(result.project);
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
		startOperation(buildEditOperationSteps());
		setOperationStep('save', 18, '프로젝트 정보를 저장하는 중입니다.');
		// Keep the current embed URL while a replacement PBIX is being imported.
		// The publish endpoint replaces it only after the new import succeeds.
		const projectUpdateInput = pbixFile && input.delete_pbix ? { ...input, delete_pbix: false } : input;
		const result = await updateProject(projectId, projectUpdateInput);
		if (!result.ok || !result.projectId) {
			failOperation();
			submitting = false;
			error = result.message;
			return;
		}
		if (bodyImageFiles.length > 0) {
			setOperationStep('body-image-upload', 32, '본문 이미지를 업로드하는 중입니다.');
			const bodyImageResult = await uploadProjectBodyImages(result.projectId, bodyImageFiles);
			if (!bodyImageResult.ok || bodyImageResult.urls.length !== bodyImageFiles.length) {
				failOperation();
				submitting = false;
				error = bodyImageResult.message;
				return;
			}
			bodyHtml = replacePendingBodyImages(bodyHtml, bodyImageFiles, bodyImageResult.urls);
			syncProjectBodyInput();
			const bodyUpdateResult = await updateProject(result.projectId, input);
			if (!bodyUpdateResult.ok) {
				failOperation();
				submitting = false;
				error = bodyUpdateResult.message;
				return;
			}
			releaseBodyImageFiles();
		}
		if (input.delete_thumbnail && !thumbnailFile && input.thumbnail_mode !== 'capture') {
			setOperationStep('thumbnail-delete', 36, '기존 썸네일 파일과 연결을 삭제하는 중입니다.');
			const deleteThumbnailResult = await deleteProjectThumbnail(result.projectId);
			if (!deleteThumbnailResult.ok) {
				failOperation();
				submitting = false;
				error = deleteThumbnailResult.message;
				return;
			}
		}
		if (input.delete_pbix && !pbixFile) {
			setOperationStep('pbix-unlink', 48, '기존 Power BI 게시본 연결을 삭제하는 중입니다.');
			const unlinkResult = await unlinkProjectPbix(result.projectId);
			if (!unlinkResult.ok) {
				failOperation();
				submitting = false;
				error = unlinkResult.message;
				return;
			}
		}
		if (thumbnailFile) {
			setOperationStep('thumbnail-upload', 58, '썸네일 이미지를 업로드하는 중입니다.');
			const uploadResult = await uploadProjectThumbnail(result.projectId, thumbnailFile);
			if (!uploadResult.ok) {
				failOperation();
				submitting = false;
				error = uploadResult.message;
				return;
			}
		}
		if (pbixFile) {
			setOperationStep('pbix-publish', 72, '새 PBIX 파일을 Power BI Workspace에 게시하는 중입니다.');
			const publishResult = await publishProjectPbix(result.projectId, pbixFile);
			if (!publishResult.ok) {
				failOperation();
				submitting = false;
				error = publishResult.message;
				return;
			}
		}
		if (input.thumbnail_mode === 'capture') {
			setOperationStep('thumbnail-capture', 86, '프로젝트 대표 썸네일을 자동 캡처 중입니다.');
			const captureResult = await captureProjectThumbnail(result.projectId);
			if (!captureResult.ok) {
				failOperation();
				submitting = false;
				error = captureResult.message;
				return;
			}
		}
		setOperationStep('finish', 100, '프로젝트 수정 요청이 완료되었습니다.');
		submitting = false;
		message = result.message;
		await goto(`/projects/${result.projectId}`);
	}

	function buildEditOperationSteps(): OperationStep[] {
		const steps: OperationStep[] = [{ id: 'save', label: '프로젝트 정보를 저장합니다.', status: 'pending' }];
		if (bodyImageFiles.length > 0) {
			steps.push({ id: 'body-image-upload', label: '본문 이미지를 업로드합니다.', status: 'pending' });
		}
		if (input.delete_thumbnail && !thumbnailFile && input.thumbnail_mode !== 'capture') {
			steps.push({ id: 'thumbnail-delete', label: '기존 썸네일을 삭제합니다.', status: 'pending' });
		}
		if (input.delete_pbix && !pbixFile) {
			steps.push({ id: 'pbix-unlink', label: '기존 Power BI 연결을 삭제합니다.', status: 'pending' });
		}
		if (thumbnailFile) {
			steps.push({ id: 'thumbnail-upload', label: '썸네일 이미지를 업로드합니다.', status: 'pending' });
		}
		if (pbixFile) {
			steps.push({ id: 'pbix-publish', label: '새 PBIX 파일을 Power BI Workspace에 게시합니다.', status: 'pending' });
		}
		if (input.thumbnail_mode === 'capture') {
			steps.push({ id: 'thumbnail-capture', label: '대표 썸네일을 자동 캡처합니다.', status: 'pending' });
		}
		steps.push({ id: 'finish', label: '프로젝트 수정 요청을 완료합니다.', status: 'pending' });
		return steps;
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

	function emptyInput(): ProjectSubmitInput {
		return {
			title: '',
			one_liner: '',
			tags: '',
			platform: 'other',
			problem: '',
			dataset: '',
			process: '',
			insights: '',
			power_bi_url: '',
			report_url: '',
			github_url: '',
			thumbnail_url: '',
			thumbnail_mode: 'auto_cover',
			delete_thumbnail: false,
			delete_pbix: false,
			is_public: true
		};
	}

	function inputFromProject(value: ProjectCardType): ProjectSubmitInput {
		return {
			title: value.title,
			one_liner: value.one_liner ?? '',
			tags: value.tags.join(', '),
			platform: value.platform_key ?? 'other',
			problem: value.problem ?? '',
			dataset: value.dataset ?? '',
			process: value.process ?? '',
			insights: value.insights ?? '',
			power_bi_url: value.power_bi_url ?? '',
			report_url: value.report_url ?? '',
			github_url: value.github_url ?? '',
			thumbnail_url: value.thumbnail_url ?? '',
			thumbnail_mode: value.thumbnail_mode,
			delete_thumbnail: false,
			delete_pbix: false,
			is_public: value.is_public
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
	function previewTags(tags: string, platform: ProjectSubmitInput['platform']) {
		const rawTags = tags
			.replaceAll('#', '')
			.split(',')
			.map((tag) => tag.trim())
			.filter(Boolean);
		const uniqueTags = [...new Set(rawTags)];
		if (platform === 'other') {
			return uniqueTags.slice(0, 5);
		}
		const platformLabel = platformOptions.find((option) => option.key === platform)?.label ?? '';
		const platformAliases = new Set([
			platformLabel,
			platform,
			platform === 'datastudio' ? 'Data Studio' : '',
			platform === 'datastudio' ? 'Looker Studio' : '',
			platform === 'powerbi' ? 'PowerBI' : '',
			platform === 'powerbi' ? 'Power BI' : ''
		].map(normalizeTag));
		return [platformLabel, ...uniqueTags.filter((tag) => !platformAliases.has(normalizeTag(tag)))].slice(0, 5);
	}

	function normalizeTag(value: string) {
		return value.trim().toLowerCase().replaceAll(' ', '');
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
