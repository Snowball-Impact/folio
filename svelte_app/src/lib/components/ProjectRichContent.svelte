<script lang="ts">
	import { onMount, tick } from 'svelte';
	import { sanitizeProjectHtml } from '$lib/format';

	type KatexRenderer = typeof import('katex').default;
	let katexPromise: Promise<KatexRenderer> | null = null;

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

	async function renderMath() {
		if (!container) {
			return;
		}
		const mathNodes = [...container.querySelectorAll<HTMLElement>('[data-type="inline-math"], [data-type="block-math"]')];
		if (mathNodes.length === 0) {
			return;
		}
		const katex = await loadKatex();
		for (const node of mathNodes) {
			if (!node.isConnected) {
				continue;
			}
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

	function loadKatex() {
		return (katexPromise ??= Promise.all([import('katex'), import('katex/dist/katex.min.css')]).then(([module]) => module.default));
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
