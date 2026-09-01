<script lang="ts">
	import { onDestroy, onMount } from 'svelte';
	import ProjectCard from '$lib/components/ProjectCard.svelte';
	import type { ProjectCard as ProjectCardType } from '$lib/types';

	let {
		title,
		description,
		projects,
		emptyMessage = '표시할 프로젝트가 아직 없습니다.'
	} = $props<{
		title: string;
		description: string;
		projects: ProjectCardType[];
		emptyMessage?: string;
	}>();

	let railElement = $state<HTMLDivElement | null>(null);
	let scrollbarElement = $state<HTMLDivElement | null>(null);
	let thumbWidth = $state(44);
	let thumbLeft = $state(0);
	let hasOverflow = $state(false);
	let dragState: { startX: number; startScrollLeft: number; maxThumbLeft: number; maxScroll: number } | null = null;
	const titleParts = $derived(splitRailTitle(title));

	onMount(() => {
		updateScrollbar();
		window.addEventListener('resize', updateScrollbar);
		return () => window.removeEventListener('resize', updateScrollbar);
	});

	onDestroy(() => {
		endThumbDrag();
	});

	function updateScrollbar() {
		const rail = railElement;
		const track = scrollbarElement;
		if (!rail || !track) {
			return;
		}
		const maxScroll = Math.max(rail.scrollWidth - rail.clientWidth, 0);
		hasOverflow = maxScroll > 1;
		if (!hasOverflow) {
			thumbWidth = 44;
			thumbLeft = 0;
			return;
		}
		const trackWidth = track.clientWidth || 1;
		const nextThumbWidth = Math.max((rail.clientWidth / rail.scrollWidth) * trackWidth, 44);
		const maxThumbLeft = Math.max(trackWidth - nextThumbWidth, 0);
		thumbWidth = nextThumbWidth;
		thumbLeft = (rail.scrollLeft / maxScroll) * maxThumbLeft;
	}

	function scrollRail(direction: -1 | 1) {
		const rail = railElement;
		if (!rail) {
			return;
		}
		const firstCard = rail.querySelector<HTMLElement>('.project-card');
		const railStyle = window.getComputedStyle(rail);
		const gap = Number.parseFloat(railStyle.columnGap || railStyle.gap || '0') || 0;
		const distance = firstCard ? firstCard.getBoundingClientRect().width + gap : Math.max(rail.clientWidth * 0.72, 320);
		rail.scrollBy({ left: direction * distance, behavior: 'smooth' });
	}

	function seekScrollbar(event: PointerEvent) {
		const track = scrollbarElement;
		const rail = railElement;
		if (!track || !rail || !hasOverflow || event.target !== track) {
			return;
		}
		const rect = track.getBoundingClientRect();
		const ratio = (event.clientX - rect.left) / Math.max(rect.width, 1);
		rail.scrollTo({ left: ratio * (rail.scrollWidth - rail.clientWidth), behavior: 'smooth' });
	}

	function startThumbDrag(event: PointerEvent) {
		const track = scrollbarElement;
		const rail = railElement;
		if (!track || !rail || !hasOverflow) {
			return;
		}
		event.preventDefault();
		const maxScroll = Math.max(rail.scrollWidth - rail.clientWidth, 0);
		const maxThumbLeft = Math.max(track.clientWidth - thumbWidth, 1);
		dragState = {
			startX: event.clientX,
			startScrollLeft: rail.scrollLeft,
			maxThumbLeft,
			maxScroll
		};
		window.addEventListener('pointermove', dragThumb);
		window.addEventListener('pointerup', endThumbDrag, { once: true });
	}

	function dragThumb(event: PointerEvent) {
		if (!dragState || !railElement) {
			return;
		}
		const delta = event.clientX - dragState.startX;
		railElement.scrollLeft = dragState.startScrollLeft + (delta / dragState.maxThumbLeft) * dragState.maxScroll;
	}

	function endThumbDrag() {
		if (typeof window !== 'undefined') {
			window.removeEventListener('pointermove', dragThumb);
		}
		dragState = null;
	}

	function splitRailTitle(value: string) {
		const highlights = ['새로 공개', '조회수', '좋아요'];
		const highlight = highlights.find((item) => value.includes(item));
		if (!highlight) {
			return { before: value, highlight: '', after: '' };
		}
		const index = value.indexOf(highlight);
		return {
			before: value.slice(0, index),
			highlight,
			after: value.slice(index + highlight.length)
		};
	}
</script>

<section class="project-rail-section">
	<div class="project-rail-head">
		<button
			class="rail-scroll-button"
			type="button"
			aria-label={`${description} 왼쪽으로 스크롤`}
			onclick={() => scrollRail(-1)}
		>
			‹
		</button>
		<h2>{titleParts.before}<span>{titleParts.highlight}</span>{titleParts.after}</h2>
		<button
			class="rail-scroll-button"
			type="button"
			aria-label={`${description} 오른쪽으로 스크롤`}
			onclick={() => scrollRail(1)}
		>
			›
		</button>
	</div>
	{#if projects.length > 0}
		<div class="project-rail-wrap">
			<div
				class="project-rail-scrollbar"
				class:hidden={!hasOverflow}
				bind:this={scrollbarElement}
				onpointerdown={seekScrollbar}
				aria-hidden="true"
			>
				<button
					type="button"
					class="project-rail-thumb"
					style={`width: ${thumbWidth}px; transform: translateX(${thumbLeft}px);`}
					aria-label="레일 스크롤바 이동"
					onpointerdown={startThumbDrag}
				></button>
			</div>
			<div class="project-rail-spacer" aria-hidden="true"></div>
			<div class="rail" bind:this={railElement} onscroll={updateScrollbar}>
				{#each projects as project}
					<ProjectCard {project} />
				{/each}
			</div>
		</div>
	{:else}
		<div class="empty-panel">{emptyMessage}</div>
	{/if}
</section>
