<script lang="ts">
	import { onDestroy, onMount } from 'svelte';
	import type { service as PowerBIServiceNamespace } from 'powerbi-client';
	import type { PowerBIEmbedConfig } from '$lib/types';

	type PowerBIClientModule = typeof import('powerbi-client');
	type PowerBIReportStatus = 'loading' | 'ready' | 'error';

	let {
		config,
		title,
		onStatusChange
	}: {
		config: PowerBIEmbedConfig;
		title: string;
		onStatusChange?: (status: PowerBIReportStatus) => void;
	} = $props();

	const REPORT_ASPECT_RATIO = 9 / 16;
	const REPORT_MIN_HEIGHT = 560;
	const REPORT_MAX_HEIGHT = 860;

	let shell: HTMLDivElement;
	let container: HTMLDivElement;
	let status = $state<PowerBIReportStatus>('loading');
	let loadDurationMs = $state<number | null>(null);
	let powerBIService: PowerBIServiceNamespace.Service | null = null;
	let embedStartedAt = 0;
	let metricRecorded = false;
	let measurementName = '';
	let resizeObserver: ResizeObserver | null = null;
	let resizeFrame = 0;

	function setStatus(nextStatus: PowerBIReportStatus) {
		status = nextStatus;
		if (nextStatus !== 'loading' && !metricRecorded && embedStartedAt > 0) {
			metricRecorded = true;
			loadDurationMs = Math.round(performance.now() - embedStartedAt);
			const endMark = `${measurementName}:end`;
			performance.mark(endMark);
			performance.measure(measurementName, `${measurementName}:start`, endMark);
			window.dispatchEvent(
				new CustomEvent('folio:powerbi-metric', {
					detail: { status: nextStatus, durationMs: loadDurationMs, title }
				})
			);
		}
		onStatusChange?.(nextStatus);
	}

	function updateReportHeight() {
		if (!shell) {
			return;
		}
		const width = shell.clientWidth;
		if (!width) {
			return;
		}
		const nextHeight = Math.round(Math.min(REPORT_MAX_HEIGHT, Math.max(REPORT_MIN_HEIGHT, width * REPORT_ASPECT_RATIO)));
		shell.style.setProperty('--powerbi-report-height', `${nextHeight}px`);
		window.dispatchEvent(new Event('resize'));
	}

	function scheduleReportHeightUpdate() {
		cancelAnimationFrame(resizeFrame);
		resizeFrame = requestAnimationFrame(updateReportHeight);
	}

	onMount(async () => {
		measurementName = `folio-powerbi-${Date.now()}-${Math.random().toString(36).slice(2)}`;
		embedStartedAt = performance.now();
		performance.mark(`${measurementName}:start`);
		resizeObserver = new ResizeObserver(scheduleReportHeightUpdate);
		resizeObserver.observe(shell);
		scheduleReportHeightUpdate();
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
					layoutType: models.LayoutType.Custom,
					customLayout: {
						displayOption: models.DisplayOption.FitToWidth
					},
					panes: {
						filters: { visible: false },
						pageNavigation: { visible: true }
					},
					background: models.BackgroundType.Transparent
				}
			});

			report.on('loaded', () => {
				scheduleReportHeightUpdate();
				setStatus('ready');
			});
			report.on('rendered', () => {
				scheduleReportHeightUpdate();
				setStatus('ready');
			});
			report.on('error', () => {
				setStatus('error');
			});
		} catch {
			setStatus('error');
		}
	});

	onDestroy(() => {
		cancelAnimationFrame(resizeFrame);
		resizeObserver?.disconnect();
		if (powerBIService && container) {
			powerBIService.reset(container);
		}
	});
</script>

<div bind:this={shell} class="powerbi-shell" data-powerbi-status={status} data-powerbi-load-ms={loadDurationMs ?? undefined}>
	<div bind:this={container} class="powerbi-report" aria-label={`${title} Power BI 보고서`}></div>
	{#if status === 'loading'}
		<div class="powerbi-overlay">Power BI 보고서를 불러오는 중...</div>
	{:else if status === 'error'}
		<div class="powerbi-overlay">Power BI 보고서를 불러오지 못했습니다.</div>
	{/if}
</div>
