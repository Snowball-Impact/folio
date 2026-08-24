<script lang="ts">
	import { formatCount } from '$lib/format';
	import type { ProjectCard } from '$lib/types';

	let { project } = $props<{ project: ProjectCard }>();

	const visibleTags = $derived(project.tags.slice(0, 4));
	const extraTagCount = $derived(Math.max(project.tags.length - visibleTags.length, 0));
	const coverVariant = $derived(projectCoverVariant(project));
	const hasThumbnail = $derived(Boolean(project.thumbnail_url));

	function projectCoverVariant(project: ProjectCard, variantCount = 24) {
		const seed = project.id || project.title || 'folio';
		let hash = 2166136261;
		for (let index = 0; index < seed.length; index += 1) {
			hash ^= seed.charCodeAt(index);
			hash = Math.imul(hash, 16777619);
		}
		return Math.abs(hash) % variantCount;
	}
</script>

<a class="project-card" class:has-thumbnail={hasThumbnail} href={`/projects/${project.id}`} aria-label={`${project.title} 상세 보기`}>
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
		<div class="card-footer">
			<div class="tags" aria-label="태그">
				{#each visibleTags as tag}
					<span class="tag">#{tag}</span>
				{/each}
				{#if extraTagCount > 0}
					<span class="tag">+{extraTagCount}</span>
				{/if}
			</div>
			<div class="card-meta card-meta-bottom">
				<span>조회 {formatCount(project.view_count)}</span>
				<span>좋아요 {formatCount(project.like_count)}</span>
				<span>댓글 {formatCount(project.comment_count)}</span>
			</div>
		</div>
	</div>
</a>
