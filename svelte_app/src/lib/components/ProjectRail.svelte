<script lang="ts">
	import ProjectCard from '$lib/components/ProjectCard.svelte';
	import type { ProjectCard as ProjectCardType } from '$lib/types';

	let {
		title,
		description,
		projects
	} = $props<{
		title: string;
		description: string;
		projects: ProjectCardType[];
	}>();
</script>

<section>
	<div class="section-header">
		<h2>{title}</h2>
		<p>{description}</p>
	</div>
	{#if projects.length > 0}
		<div class="rail">
			{#each projects as project}
				<ProjectCard {project} />
			{/each}
		</div>
	{:else}
		<div class="empty-panel">표시할 프로젝트가 아직 없습니다.</div>
	{/if}
</section>
