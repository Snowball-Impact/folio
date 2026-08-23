<script lang="ts">
	import { onDestroy, onMount } from 'svelte';
	import type { service as PowerBIServiceNamespace } from 'powerbi-client';
	import type { PowerBIEmbedConfig } from '$lib/types';

	type PowerBIClientModule = typeof import('powerbi-client');

	let { config, title }: { config: PowerBIEmbedConfig; title: string } = $props();

	let container: HTMLDivElement;
	let status = $state<'loading' | 'ready' | 'error'>('loading');
	let powerBIService: PowerBIServiceNamespace.Service | null = null;

	onMount(async () => {
		try {
			const powerbiClient = (await import('powerbi-client')) as PowerBIClientModule;
			const { factories, models, service } = powerbiClient;
			powerBIService = new service.Service(
				factories.hpmFactory,
				factories.wpmpFactory,
				factories.routerFactory
			);
			const report = powerBIService.embed(container, {
				type: 'report',
				id: config.report_id,
				embedUrl: config.embed_url,
				accessToken: config.embed_token,
				tokenType: models.TokenType.Embed,
				permissions: models.Permissions.Read,
				settings: {
					panes: {
						filters: { visible: false },
						pageNavigation: { visible: true }
					},
					background: models.BackgroundType.Transparent
				}
			});

			report.on('loaded', () => {
				status = 'ready';
			});
			report.on('error', () => {
				status = 'error';
			});
		} catch {
			status = 'error';
		}
	});

	onDestroy(() => {
		if (powerBIService && container) {
			powerBIService.reset(container);
		}
	});
</script>

<div class="powerbi-shell">
	<div bind:this={container} class="powerbi-report" aria-label={`${title} Power BI 보고서`}></div>
	{#if status === 'loading'}
		<div class="powerbi-overlay">Power BI 보고서를 불러오는 중...</div>
	{:else if status === 'error'}
		<div class="powerbi-overlay">Power BI 보고서를 불러오지 못했습니다.</div>
	{/if}
</div>
