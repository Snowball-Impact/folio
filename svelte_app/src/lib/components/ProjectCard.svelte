<script lang="ts">
	import { formatCount, formatDate, platformLabel } from '$lib/format';
	import type { ProjectCard } from '$lib/types';

	let { project } = $props<{ project: ProjectCard }>();

	const visibleTags = $derived(project.tags.slice(0, 4));
	const extraTagCount = $derived(Math.max(project.tags.length - visibleTags.length, 0));
	const coverStyle = $derived(
		project.thumbnail_url ? `background-image: url("${project.thumbnail_url}")` : ''
	);
</script>

<a class="project-card" href={`/projects/${project.id}`} aria-label={`${project.title} 상세 보기`}>
	<div class="card-cover" style={coverStyle}></div>
	<div class="card-body">
		<div class="card-meta">
			<span class="pill">{platformLabel(project.platform_key, project.project_type)}</span>
			<span>{formatDate(project.created_at)}</span>
		</div>
		<h3 class="card-title">{project.title}</h3>
		<p class="card-summary">{project.one_liner ?? '프로젝트 소개가 없습니다.'}</p>
		<div class="tags" aria-label="태그">
			{#each visibleTags as tag}
				<span class="tag">#{tag}</span>
			{/each}
			{#if extraTagCount > 0}
				<span class="tag">+{extraTagCount}</span>
			{/if}
		</div>
		<div class="card-meta">
			<span>조회 {formatCount(project.view_count)}</span>
			<span>좋아요 {formatCount(project.like_count)}</span>
			<span>댓글 {formatCount(project.comment_count)}</span>
		</div>
	</div>
</a>
