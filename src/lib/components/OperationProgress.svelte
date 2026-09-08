<script lang="ts">
	import { onMount } from 'svelte';

	export type OperationStepStatus = 'pending' | 'active' | 'done' | 'error';
	export type OperationStep = {
		id: string;
		label: string;
		status: OperationStepStatus;
		detail?: string;
		estimatedSeconds?: number;
	};

	let {
		title = '작업 진행',
		progress = 0,
		steps = [],
		dismissLabel = '닫기',
		onDismiss
	}: {
		title?: string;
		progress?: number;
		steps: OperationStep[];
		dismissLabel?: string;
		onDismiss?: () => void;
	} = $props();
	const boundedProgress = $derived(Math.max(0, Math.min(100, Math.round(progress))));
	const activeStep = $derived(steps.find((step) => step.status === 'error') ?? steps.find((step) => step.status === 'active') ?? steps.at(-1));
	const canDismiss = $derived(Boolean(onDismiss) && (boundedProgress >= 100 || steps.some((step) => step.status === 'error')));
	const actionLabel = $derived(boundedProgress >= 100 && !steps.some((step) => step.status === 'error') ? '완료' : dismissLabel);
	let now = $state(Date.now());
	let activeStepKey = $state('');
	let activeStepStartedAt = $state(Date.now());
	const activeEstimateSeconds = $derived(
		activeStep?.status === 'active' && activeStep.estimatedSeconds ? Math.max(activeStep.estimatedSeconds, 1) : 0
	);
	const elapsedSeconds = $derived(Math.max(0, Math.floor((now - activeStepStartedAt) / 1000)));
	const remainingSeconds = $derived(Math.max(0, activeEstimateSeconds - elapsedSeconds));
	const timeEstimateText = $derived(
		activeEstimateSeconds
			? remainingSeconds > 0
				? `예상 남은 시간 약 ${formatDuration(remainingSeconds)} · 경과 ${formatDuration(elapsedSeconds)}`
				: `예상 대기 시간을 넘겼지만 계속 처리 중입니다. 경과 ${formatDuration(elapsedSeconds)}`
			: ''
	);

	$effect(() => {
		const nextKey = activeStep ? `${activeStep.id}:${activeStep.status}` : '';
		if (nextKey !== activeStepKey) {
			activeStepKey = nextKey;
			activeStepStartedAt = Date.now();
			now = activeStepStartedAt;
		}
	});

	onMount(() => {
		const timer = setInterval(() => {
			now = Date.now();
		}, 1000);
		return () => clearInterval(timer);
	});

	function formatDuration(totalSeconds: number) {
		const seconds = Math.max(0, Math.round(totalSeconds));
		if (seconds < 60) {
			return `${seconds}초`;
		}
		const minutes = Math.floor(seconds / 60);
		const remainder = seconds % 60;
		return remainder ? `${minutes}분 ${remainder}초` : `${minutes}분`;
	}
</script>

{#if steps.length > 0}
	<div class="operation-progress-layer" role="presentation">
		<div class="operation-progress-panel" role="dialog" aria-modal="true" aria-live="polite" aria-label={title}>
			<header>
				<strong>{title}</strong>
				<span>{boundedProgress}%</span>
			</header>
			<div class="operation-progress-track" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow={boundedProgress} aria-valuetext={activeStep?.detail ?? activeStep?.label}>
				<div style={`width: ${boundedProgress}%`}></div>
			</div>
			{#if activeStep}
				<p>{activeStep.detail ?? activeStep.label}</p>
			{/if}
			{#if timeEstimateText}
				<div class="operation-progress-estimate">{timeEstimateText}</div>
			{/if}
			<ol>
				{#each steps as step}
					<li class={step.status}>
						<span></span>
						<em>{step.label}</em>
					</li>
				{/each}
			</ol>
			{#if canDismiss}
				<div class="operation-progress-actions">
					<button type="button" onclick={() => onDismiss?.()}>{actionLabel}</button>
				</div>
			{/if}
		</div>
	</div>
{/if}
