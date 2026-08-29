<script lang="ts">
	import ProjectCard from '$lib/components/ProjectCard.svelte';
	import type { ProjectCard as ProjectCardType } from '$lib/types';

	let { project } = $props<{ project: ProjectCardType }>();
</script>

<div class="hero-thumbnail-preview" aria-label="프로젝트 카드 미리보기">
	<ProjectCard {project} compact preview />
</div>