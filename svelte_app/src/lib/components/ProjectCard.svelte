<script lang="ts">
	import { formatCount, formatDate } from '$lib/format';
	import { projectCoverVariant } from '$lib/cover';
	import type { ProjectCard } from '$lib/types';

	let { project, compact = false, preview = false } = $props<{
		project: ProjectCard;
		compact?: boolean;
		preview?: boolean;
	}>();

	const visibleTags = $derived(project.tags.slice(0, 4));
	const extraTagCount = $derived(Math.max(project.tags.length - visibleTags.length, 0));
	const coverVariant = $derived(projectCoverVariant(project));
	const hasThumbnail = $derived(Boolean(project.thumbnail_url));
	const showIconMetrics = $derived(compact || preview);
	const activityLabel = $derived(preview ? '' : projectActivityLabel(project));

	function projectActivityLabel(project: ProjectCard) {
		const now = Date.now();
		const recentWindow = 7 * 24 * 60 * 60 * 1000;
		const createdAt = Date.parse(project.created_at);
		if (Number.isFinite(createdAt) && createdAt <= now && now - createdAt <= recentWindow) {
			return 'NEW';
		}
		const latestCommentAt = Date.parse(project.latest_comment_at ?? '');
		return Number.isFinite(latestCommentAt) && latestCommentAt <= now && now - latestCommentAt <= recentWindow ? '댓글 NEW' : '';
	}

</script>

{#snippet CardContent()}
	{#if activityLabel}
		<span class="card-activity-badge" aria-label={activityLabel} title={activityLabel}>{activityLabel}</span>
	{/if}
	<div class="card-cover">
		{#if project.thumbnail_url}
			<img src={project.thumbnail_url} alt={`${project.title} 대표 이미지`} loading="lazy" />
		{:else}
			<div class={`folio-auto-cover folio-auto-cover-${coverVariant}`} aria-hidden="true">
				<div class="folio-auto-cover-pattern"></div>
			</div>
		{/if}
	</div>
	<div class="card-body">
		<h3 class="card-title">{project.title}</h3>
		<p class="card-summary">{project.one_liner ?? '프로젝트 소개가 없습니다.'}</p>
		<div class="tags card-tags" aria-label="태그">
				{#each visibleTags as tag}
					<span class="tag">#{tag}</span>
				{/each}
				{#if extraTagCount > 0}
					<span class="tag">+{extraTagCount}</span>
				{/if}
		</div>
		<div class="card-footer">
			<div class="card-footer-meta">
				{#if preview}
					<span class="card-preview-author">{project.author.name ?? '작성자'}</span>
				{:else}
					<span>{formatDate(project.created_at)}</span>
					<span>{project.author.name ?? '작성자'}{project.author.organization ? ` · ${project.author.organization}` : ''}</span>
				{/if}
			</div>
			<div class="card-meta card-meta-bottom">
				{#if showIconMetrics}
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
				{:else}
					<span>조회 {formatCount(project.view_count)}</span>
					<span>좋아요 {formatCount(project.like_count)}</span>
					<span>댓글 {formatCount(project.comment_count)}</span>
				{/if}
			</div>
		</div>
	</div>
{/snippet}

{#if preview}
	<div class="project-card" class:has-thumbnail={hasThumbnail} class:compact class:preview aria-label={`${project.title} 미리보기`}>
		{@render CardContent()}
	</div>
{:else}
	<a class="project-card" class:has-thumbnail={hasThumbnail} class:compact href={`/projects/${project.id}`} aria-label={`${project.title} 상세 보기`}>
		{@render CardContent()}
	</a>
{/if}
