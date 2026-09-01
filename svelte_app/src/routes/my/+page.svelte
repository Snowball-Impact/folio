<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { currentProfile, currentSession, updateProfile, type AuthProfile } from '$lib/auth';
	import { deleteProject, listMyProjects } from '$lib/projects';
	import { formatCount } from '$lib/format';
	import type { ProjectCard } from '$lib/types';

	let profile = $state<AuthProfile | null>(null);
	let projects = $state<ProjectCard[]>([]);
	let loading = $state(true);
	let deleting = $state(false);
	let deleteDialogProject = $state<ProjectCard | null>(null);
	let editingProfile = $state(false);
	let profileName = $state('');
	let profileOrganization = $state('');
	let profileBio = $state('');
	let profileSaving = $state(false);
	let message = $state('');
	let error = $state('');
	let needsLogin = $state(false);
	const MY_PROJECTS_PAGE_SIZE = 5;
	let projectPageIndex = $state(0);

	const stats = $derived({
		projectCount: projects.length,
		publicCount: projects.filter((project) => project.is_public).length,
		viewCount: projects.reduce((total, project) => total + project.view_count, 0),
		likeCount: projects.reduce((total, project) => total + project.like_count, 0)
	});
	const projectTotalPages = $derived(Math.max(Math.ceil(projects.length / MY_PROJECTS_PAGE_SIZE), 1));
	const visibleProjects = $derived(
		projects.slice(projectPageIndex * MY_PROJECTS_PAGE_SIZE, projectPageIndex * MY_PROJECTS_PAGE_SIZE + MY_PROJECTS_PAGE_SIZE)
	);

	$effect(() => {
		if (projectPageIndex > projectTotalPages - 1) {
			projectPageIndex = projectTotalPages - 1;
		}
		if (projectPageIndex < 0) {
			projectPageIndex = 0;
		}
	});

	onMount(async () => {
		const session = await currentSession();
		if (!session) {
			needsLogin = true;
			loading = false;
			return;
		}
		profile = await currentProfile(session.user);
		syncProfileForm();
		await refreshProjects();
	});

	async function refreshProjects() {
		loading = true;
		const result = await listMyProjects();
		projects = result.projects;
		error = result.error;
		projectPageIndex = 0;
		loading = false;
	}

	function moveProjectPage(direction: -1 | 1) {
		projectPageIndex = Math.min(Math.max(projectPageIndex + direction, 0), projectTotalPages - 1);
	}
	function openDeleteDialog(project: ProjectCard) {
		deleteDialogProject = project;
		message = '';
		error = '';
	}

	function closeDeleteDialog() {
		if (!deleting) {
			deleteDialogProject = null;
		}
	}

	async function confirmProjectDeletion() {
		if (!deleteDialogProject) {
			return;
		}
		message = '';
		error = '';
		deleting = true;
		const projectTitle = deleteDialogProject.title;
		const result = await deleteProject(deleteDialogProject.id);
		deleting = false;
		if (!result.ok) {
			error = result.message;
			return;
		}
		deleteDialogProject = null;
		message = result.message || `${projectTitle} 프로젝트를 삭제했습니다.`;
		await refreshProjects();
	}

	function startProfileEdit() {
		syncProfileForm();
		editingProfile = true;
		message = '';
		error = '';
	}

	function syncProfileForm() {
		profileName = profile?.name ?? '';
		profileOrganization = profile?.organization ?? '';
		profileBio = profile?.bio ?? '';
	}

	async function saveProfile(event: SubmitEvent) {
		event.preventDefault();
		message = '';
		error = '';
		profileSaving = true;
		const result = await updateProfile({
			name: profileName,
			organization: profileOrganization,
			bio: profileBio
		});
		profileSaving = false;
		if (!result.ok) {
			error = result.message;
			return;
		}
		profile = profile
			? {
					...profile,
					name: profileName.trim(),
					organization: profileOrganization.trim() || null,
					bio: profileBio.trim() || null
				}
			: profile;
		editingProfile = false;
		message = result.message;
	}
</script>

<svelte:head>
	<title>마이 페이지 | FOLIO</title>
	<meta name="description" content="FOLIO 프로필과 내 프로젝트를 관리합니다." />
</svelte:head>

<section class="my-hero page-image-hero">
	<div class="page-image-hero-copy">
		<div class="page-image-hero-eyebrow">My Page</div>
		<h1>마이 페이지</h1>
		<p>프로필과 포트폴리오를 한곳에서 관리하세요.</p>
	</div>
	<div class="page-image-hero-visual">
		<img src="/hero-my-page-v2.webp" alt="프로필 카드와 포트폴리오 통계를 표현한 일러스트" />
	</div>
</section>

{#if needsLogin}
	<section class="profile-overview profile-login-required">
		<div class="comments-empty notification-login-required">
			<span>마이 페이지를 이용하려면 로그인이 필요합니다.</span>
			<a class="button-link" href="/login?next=/my">로그인하기</a>
		</div>
	</section>
{:else if editingProfile}
	<section class="profile-edit-card">
		<form class="project-form" onsubmit={saveProfile}>
			<header>
				<div class="eyebrow">EDIT PROFILE</div>
				<h2>프로필 정보 수정</h2>
				<p>포트폴리오 방문자에게 보여줄 기본 정보를 관리합니다.</p>
			</header>
			<div class="form-grid two">
				<label>
					<span>이름 *</span>
					<input bind:value={profileName} placeholder="이름을 입력하세요" />
				</label>
				<label>
					<span>소속</span>
					<input bind:value={profileOrganization} placeholder="학교, 기관 또는 회사" />
				</label>
			</div>
			<label>
				<span>자기소개</span>
				<textarea bind:value={profileBio} maxlength="300" placeholder="관심 분야와 데이터 분석 관점을 소개해 보세요."></textarea>
			</label>
			<p class="form-caption">자기소개는 최대 300자까지 입력할 수 있습니다.</p>
			<div class="project-form-actions">
				<button type="button" class="secondary-action" onclick={() => (editingProfile = false)}>취소</button>
				<button type="submit" disabled={profileSaving}>{profileSaving ? '저장 중...' : '변경사항 저장'}</button>
			</div>
		</form>
	</section>
{:else}
	<section class="profile-overview">
		<div class="profile-summary">
			<dl class="profile-fields">
				<div>
					<dt>작성자</dt>
					<dd class="profile-name">{profile?.name ?? profile?.email ?? '사용자'}</dd>
				</div>
				<div>
					<dt>소속</dt>
					<dd class:empty={!profile?.organization}>{profile?.organization || '소속을 추가해 나를 더 잘 소개해 보세요'}</dd>
				</div>
				<div>
					<dt>이메일</dt>
					<dd class="profile-email">{profile?.email}</dd>
				</div>
			</dl>
			<div class="profile-about">
				<p class:empty={!profile?.bio}>{profile?.bio || '아직 자기소개가 없습니다. 어떤 관점으로 데이터를 바라보는지 들려주세요.'}</p>
			</div>
			<div class="profile-stats" aria-label="내 프로젝트 통계">
				<span><small>전체 프로젝트</small><strong>{formatCount(stats.projectCount)}</strong></span>
				<span><small>공개 프로젝트</small><strong>{formatCount(stats.publicCount)}</strong></span>
				<span><small>누적 조회</small><strong>{formatCount(stats.viewCount)}</strong></span>
				<span><small>총 좋아요</small><strong>{formatCount(stats.likeCount)}</strong></span>
			</div>
			<button type="button" onclick={startProfileEdit}>프로필 편집</button>
		</div>
	</section>

	<section class="portfolio-section">
		<div class="section-header">
			<div>
				<h2>내 프로젝트</h2>
				<p>등록한 프로젝트를 확인하고 수정하거나 삭제할 수 있습니다.</p>
			</div>
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
			<div class="comments-empty profile-empty-projects">
				<strong>아직 등록한 프로젝트가 없습니다.</strong>
				<span>첫 프로젝트를 등록하면 이곳에서 관리할 수 있습니다.</span>
				<a class="button-link primary" href="/submit">프로젝트 등록</a>
			</div>
		{:else}
			<div class="portfolio-list">
				{#each visibleProjects as project}
					<article class="portfolio-card">
						<div>
							<div class="portfolio-title-line">
								<strong>{project.title}</strong>
								{#if project.has_unread_comments}
									<span class="portfolio-unread-badge" aria-label="안 본 댓글 있음">NEW</span>
								{/if}
								{#if project.status === 'processing'}
									<span>처리 중</span>
								{:else if project.status === 'failed'}
									<span class="private">게시 실패</span>
								{/if}
							</div>
							{#if project.one_liner}
								<p>{project.one_liner}</p>
							{/if}
							<div class="portfolio-card-footer">
								<div class="tags">
									{#each project.tags as tag}
										<span class="tag">#{tag}</span>
									{/each}
								</div>
								<div class="card-meta portfolio-card-meta">
									<span title="조회수" aria-label={`조회수 ${formatCount(project.view_count)}`}>
										<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M2.5 12s3.5-6 9.5-6 9.5 6 9.5 6-3.5 6-9.5 6-9.5-6-9.5-6Z"></path><circle cx="12" cy="12" r="2.7"></circle></svg>
										{formatCount(project.view_count)}
									</span>
									<span title="좋아요" aria-label={`좋아요 ${formatCount(project.like_count)}`}>
										<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20.8 4.8a5.5 5.5 0 0 0-7.8 0L12 5.9l-1.1-1.1a5.5 5.5 0 0 0-7.8 7.8L12 21l8.8-8.4a5.5 5.5 0 0 0 0-7.8Z"></path></svg>
										{formatCount(project.like_count)}
									</span>
									<span title="댓글" aria-label={`댓글 ${formatCount(project.comment_count)}`}>
										<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M21 15a4 4 0 0 1-4 4H8l-5 3V7a4 4 0 0 1 4-4h10a4 4 0 0 1 4 4Z"></path></svg>
										{formatCount(project.comment_count)}
									</span>
									<span title={project.is_public ? '공개' : '비공개'} aria-label={`공개 상태 ${project.is_public ? '공개' : '비공개'}`}>
										<svg viewBox="0 0 24 24" aria-hidden="true">{#if project.is_public}<circle cx="12" cy="12" r="9"></circle><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"></path>{:else}<rect x="5" y="10" width="14" height="11" rx="2"></rect><path d="M8 10V7a4 4 0 0 1 8 0v3"></path>{/if}</svg>
									</span>
								</div>
							</div>
						</div>
						<div class="portfolio-actions">
							<a class="button-link" href={`/projects/${project.id}`}>보기</a>
							<a class="button-link" href={`/projects/${project.id}/edit`}>수정</a>
					<button type="button" disabled={deleting} onclick={() => openDeleteDialog(project)}>삭제</button>
						</div>
					</article>
				{/each}
			</div>
			{#if projects.length > MY_PROJECTS_PAGE_SIZE}
				<div class="news-pagination portfolio-pagination" aria-label="내 프로젝트 페이지">
					<button type="button" onclick={() => moveProjectPage(-1)} disabled={projectPageIndex <= 0} aria-label="이전 내 프로젝트">‹</button>
					<div class="news-page-indicator">{projectPageIndex + 1} / {projectTotalPages}</div>
					<button type="button" onclick={() => moveProjectPage(1)} disabled={projectPageIndex >= projectTotalPages - 1} aria-label="다음 내 프로젝트">›</button>
				</div>
			{/if}
		{/if}
	</section>
{/if}
{#if deleteDialogProject}
	<div class="my-delete-dialog-backdrop" role="presentation" onclick={(event) => { if (event.target === event.currentTarget) closeDeleteDialog(); }}>
		<div class="my-delete-dialog" role="dialog" aria-modal="true" aria-labelledby="delete-dialog-title" aria-describedby="delete-dialog-description">
			<header>
				<div class="eyebrow">Delete Project</div>
				<h2 id="delete-dialog-title">프로젝트 삭제</h2>
			</header>
			<p id="delete-dialog-description"><strong>‘{deleteDialogProject.title || '제목 없는 프로젝트'}’</strong> 프로젝트를 삭제할까요?</p>
			<span>삭제한 프로젝트는 복구할 수 없습니다.</span>
			<div class="my-delete-dialog-actions">
				<button type="button" class="secondary-action" disabled={deleting} onclick={closeDeleteDialog}>취소</button>
				<button type="button" class="danger" disabled={deleting} onclick={confirmProjectDeletion}>{deleting ? '삭제 중...' : '삭제하기'}</button>
			</div>
		</div>
	</div>
{/if}
