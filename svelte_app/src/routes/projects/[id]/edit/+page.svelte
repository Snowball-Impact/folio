<script lang="ts">
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import { onMount } from 'svelte';
	import ProjectCard from '$lib/components/ProjectCard.svelte';
	import { currentSession } from '$lib/auth';
	import { publishProjectPbix } from '$lib/powerbi-publish';
	import { loadMyProject, updateProject, type ProjectSubmitInput } from '$lib/projects';
	import { uploadProjectThumbnail } from '$lib/thumbnails';
	import type { ProjectCard as ProjectCardType } from '$lib/types';

	const platformOptions = [
		{ key: 'other', label: '기타' },
		{ key: 'powerbi', label: 'Power BI' },
		{ key: 'tableau', label: 'Tableau' },
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
			input.thumbnail_mode === 'manual_url'
				? input.thumbnail_url.trim() || null
				: input.thumbnail_mode === 'upload'
					? thumbnailPreviewUrl
					: null,
		power_bi_url: input.power_bi_url.trim() || null,
		report_url: input.report_url.trim() || null,
		github_url: input.github_url.trim() || null,
		platform_key: input.platform === 'other' ? null : input.platform,
		project_type: input.platform === 'datastudio' ? 'looker' : input.platform === 'other' ? 'other' : input.platform,
		status: 'published',
		embed_status: input.power_bi_url.trim() ? 'supported' : 'external_only',
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
		input = inputFromProject(result.project);
		loading = false;
	});

	async function submitProject(event: SubmitEvent) {
		event.preventDefault();
		message = '';
		error = '';
		if (input.thumbnail_mode === 'upload' && !thumbnailFile) {
			error = '업로드할 썸네일 이미지를 선택하세요.';
			return;
		}
		if (input.platform === 'powerbi' && input.power_bi_url.trim() === '' && !pbixFile) {
			error = 'Power BI 프로젝트는 Embed Code 또는 PBIX 파일 중 하나를 입력하세요.';
			return;
		}
		submitting = true;
		const result = await updateProject(projectId, input);
		if (!result.ok || !result.projectId) {
			submitting = false;
			error = result.message;
			return;
		}
		if (thumbnailFile) {
			const uploadResult = await uploadProjectThumbnail(result.projectId, thumbnailFile);
			if (!uploadResult.ok) {
				submitting = false;
				error = uploadResult.message;
				return;
			}
		}
		if (pbixFile) {
			const publishResult = await publishProjectPbix(result.projectId, pbixFile);
			if (!publishResult.ok) {
				submitting = false;
				error = publishResult.message;
				return;
			}
		}
		submitting = false;
		message = result.message;
		await goto(`/projects/${result.projectId}`);
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
			thumbnail_mode: value.thumbnail_url ? 'manual_url' : 'auto_cover',
			is_public: value.is_public
		};
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
		return [platformLabel, ...uniqueTags.filter((tag) => tag.toLowerCase() !== platformLabel.toLowerCase())].slice(0, 5);
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
	<section class="submit-hero">
		<div>
			<div class="eyebrow">Edit</div>
			<h1>프로젝트 수정</h1>
			<p>프로젝트 정보와 공개 상태를 업데이트하세요.</p>
		</div>
		<div class="detail-card-preview">
			<ProjectCard project={previewProject} />
		</div>
	</section>

	<form class="project-form" onsubmit={submitProject}>
		{#if message}
			<div class="auth-message success">{message}</div>
		{/if}
		{#if error}
			<div class="auth-message error">{error}</div>
		{/if}

		<section class="project-form-section">
			<header>
				<h2>기본 정보</h2>
				<p>프로젝트를 한눈에 이해할 수 있는 정보를 입력하세요.</p>
			</header>
			<div class="form-grid two">
				<label>
					<span>프로젝트명 *</span>
					<input bind:value={input.title} maxlength="48" />
				</label>
				<label>
					<span>프로젝트 한 줄 소개</span>
					<input bind:value={input.one_liner} maxlength="56" />
				</label>
				<label>
					<span>플랫폼</span>
					<select bind:value={input.platform}>
						{#each platformOptions as option}
							<option value={option.key}>{option.label}</option>
						{/each}
					</select>
				</label>
				<label>
					<span>태그</span>
					<input bind:value={input.tags} />
				</label>
			</div>
		</section>

		<section class="project-form-section">
			<header>
				<h2>산출물 링크</h2>
				<p>공개 프로젝트에서 연결할 외부 산출물을 입력하세요.</p>
			</header>
			<div class="form-grid two">
				<label>
					<span>Embed Code</span>
					<input bind:value={input.power_bi_url} placeholder="https://... 또는 iframe 코드" />
				</label>
				{#if input.platform === 'powerbi'}
					<label>
						<span>PBIX 파일</span>
						<input type="file" accept=".pbix" onchange={selectPbix} />
					</label>
				{/if}
				<label>
					<span>GitHub URL</span>
					<input bind:value={input.github_url} placeholder="https://github.com/..." />
				</label>
				<label>
					<span>Web App URL</span>
					<input bind:value={input.report_url} placeholder="https://..." />
				</label>
				<div class="inline-controls">
					<label class="switch-row">
						<input type="checkbox" bind:checked={input.is_public} />
						<span>프로젝트 공개</span>
					</label>
				</div>
			</div>
			<div class="thumbnail-row">
				<label>
					<span>썸네일 설정</span>
					<select bind:value={input.thumbnail_mode}>
						<option value="auto_cover">기본 커버</option>
						<option value="upload">이미지 업로드</option>
						<option value="manual_url">URL 입력</option>
					</select>
				</label>
				{#if input.thumbnail_mode === 'upload'}
					<label>
						<span>썸네일 이미지</span>
						<input type="file" accept="image/jpeg,image/png,image/webp" onchange={selectThumbnail} />
					</label>
				{/if}
				{#if input.thumbnail_mode === 'manual_url'}
					<label>
						<span>썸네일 URL</span>
						<input bind:value={input.thumbnail_url} placeholder="https://..." />
					</label>
				{/if}
			</div>
		</section>

		<section class="project-form-section">
			<header>
				<h2>프로젝트 내용</h2>
				<p>분석의 배경과 과정, 핵심 인사이트를 기록하세요.</p>
			</header>
			<div class="form-grid two">
				<label>
					<span>문제 정의 *</span>
					<textarea bind:value={input.problem}></textarea>
				</label>
				<label>
					<span>사용 데이터</span>
					<textarea bind:value={input.dataset}></textarea>
				</label>
				<label>
					<span>분석 및 시각화</span>
					<textarea bind:value={input.process}></textarea>
				</label>
				<label>
					<span>주요 관찰 포인트 *</span>
					<textarea bind:value={input.insights}></textarea>
				</label>
			</div>
		</section>

		<div class="project-form-actions">
			<a class="button-link" href="/my">목록으로 돌아가기</a>
			<button type="submit" disabled={submitting}>{submitting ? '수정 중...' : '수정 완료'}</button>
		</div>
	</form>
{/if}
