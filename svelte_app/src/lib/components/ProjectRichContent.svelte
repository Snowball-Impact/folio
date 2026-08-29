<script lang="ts">
	import { onMount, tick } from 'svelte';
	import katex from 'katex';
	import 'katex/dist/katex.min.css';
	import { sanitizeProjectHtml } from '$lib/format';

	let {
		html,
		emptyMessage = '입력한 본문이 여기에 표시됩니다.',
		allowLocalImages = false
	}: {
		html: string;
		emptyMessage?: string;
		allowLocalImages?: boolean;
	} = $props();

	let container = $state<HTMLDivElement | null>(null);

	function renderMath() {
		if (!container) {
			return;
		}
		for (const node of container.querySelectorAll<HTMLElement>('[data-type="inline-math"], [data-type="block-math"]')) {
			const latex = node.dataset.latex?.trim();
			if (!latex) {
				continue;
			}
			try {
				katex.render(latex, node, {
					displayMode: node.dataset.type === 'block-math',
					throwOnError: false
				});
			} catch {
				node.textContent = latex;
			}
		}
	}

	onMount(() => {
		void tick().then(renderMath);
	});

	$effect(() => {
		html;
		void tick().then(renderMath);
	});
</script>

<div bind:this={container} class="project-rich-content">
	{@html sanitizeProjectHtml(html, { allowLocalImages }) || `<p>${emptyMessage}</p>`}
</div>
