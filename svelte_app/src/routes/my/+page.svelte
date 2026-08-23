<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { currentProfile, currentSession, type AuthProfile } from '$lib/auth';
	import { deleteProject, listMyProjects } from '$lib/projects';
	import { formatCount, formatDate, platformLabel } from '$lib/format';
	import type { ProjectCard } from '$lib/types';

	let profile = $state<AuthProfile | null>(null);
	let projects = $state<ProjectCard[]>([]);
	let loading = $state(true);
	let deleting = $state(false);
	let deleteConfirmId = $state<string | null>(null);
	let message = $state('');
	let error = $state('');

	const stats = $derived({
		projectCount: projects.length,
		viewCount: projects.reduce((total, project) => total + project.view_count, 0),
		likeCount: projects.reduce((total, project) => total + project.like_count, 0),
		commentCount: projects.reduce((total, project) => total + project.comment_count, 0)
	});

	onMount(async () => {
		const session = await currentSession();
		if (!session) {
			await goto('/login?next=/my');
			return;
		}
		profile = await currentProfile(session.user);
		await refreshProjects();
	});

	async function refreshProjects() {
		loading = true;
		const result = await listMyProjects();
		projects = result.projects;
		error = result.error;
		loading = false;
	}

	async function removeProject(projectId: string) {
		message = '';
		error = '';
		if (deleteConfirmId !== projectId) {
			deleteConfirmId = projectId;
			return;
		}
		deleting = true;
		const result = await deleteProject(projectId);
		deleting = false;
		if (!result.ok) {
			error = result.message;
			return;
		}
		deleteConfirmId = null;
		message = result.message;
		await refreshProjects();
	}
</script>

<svelte:head>
	<title>마이 페이지 | FOLIO</title>
	<meta name="description" content="FOLIO 프로필과 내 프로젝트를 관리합니다." />
</svelte:head>

<section class="my-hero">
	<div>
		<div class="eyebrow">My Page</div>
		<h1>마이 페이지</h1>
		<p>프로필과 포트폴리오를 한곳에서 관리하세요.</p>
	</div>
	<div class="profile-summary">
		<strong>{profile?.name ?? '사용자'}</strong>
		<span>{profile?.email}</span>
		{#if profile?.organization}
			<em>{profile.organization}</em>
		{/if}
	</div>
</section>

<section class="stats-grid" aria-label="내 프로젝트 통계">
	<div>
		<span>프로젝트</span>
		<strong>{formatCount(stats.projectCount)}</strong>
	</div>
	<div>
		<span>조회</span>
		<strong>{formatCount(stats.viewCount)}</strong>
	</div>
	<div>
		<span>좋아요</span>
		<strong>{formatCount(stats.likeCount)}</strong>
	</div>
	<div>
		<span>댓글</span>
		<strong>{formatCount(stats.commentCount)}</strong>
	</div>
</section>

<section class="portfolio-section">
	<div class="section-header">
		<div>
			<h2>내 프로젝트</h2>
			<p>등록한 프로젝트를 확인하고 수정하거나 삭제할 수 있습니다.</p>
		</div>
		<a class="button-link primary" href="/submit">프로젝트 등록</a>
	</div>

	{#if message}
		<div class="auth-message success">{message}</div>
	{/if}
	{#if error}
		<div class="auth-message error">{error}</div>
	{/if}

	{#if loading}
		<div class="comments-empty">내 프로젝트를 불러오는 중입니다.</div>
	{:else if projects.length === 0}
		<div class="comments-empty">
			<strong>아직 등록한 프로젝트가 없습니다.</strong>
			<span>첫 프로젝트를 등록하면 이곳에서 관리할 수 있습니다.</span>
		</div>
	{:else}
		<div class="portfolio-list">
			{#each projects as project}
				<article class="portfolio-card">
					<div>
						<div class="portfolio-title-line">
							<strong>{project.title}</strong>
							<span class:private={!project.is_public}>{project.is_public ? '공개' : '비공개'}</span>
							{#if project.status === 'processing'}
								<span>처리 중</span>
							{:else if project.status === 'failed'}
								<span class="private">게시 실패</span>
							{/if}
						</div>
						<p>{project.one_liner ?? '프로젝트 소개가 없습니다.'}</p>
						<div class="tags">
							{#each project.tags.slice(0, 5) as tag}
								<span class="tag">#{tag}</span>
							{/each}
						</div>
						<div class="card-meta">
							<span>{platformLabel(project.platform_key, project.project_type)}</span>
							<span>등록일 {formatDate(project.created_at)}</span>
							<span>조회 {formatCount(project.view_count)}</span>
							<span>좋아요 {formatCount(project.like_count)}</span>
							<span>댓글 {formatCount(project.comment_count)}</span>
						</div>
					</div>
					<div class="portfolio-actions">
						<a class="button-link" href={`/projects/${project.id}`}>보기</a>
						<a class="button-link" href={`/projects/${project.id}/edit`}>수정</a>
						<button
							type="button"
							class:danger={deleteConfirmId === project.id}
							disabled={deleting}
							onclick={() => removeProject(project.id)}
						>
							{deleteConfirmId === project.id ? '삭제 확인' : '삭제'}
						</button>
						{#if deleteConfirmId === project.id}
							<button type="button" onclick={() => (deleteConfirmId = null)}>취소</button>
						{/if}
					</div>
				</article>
			{/each}
		</div>
	{/if}
</section>
