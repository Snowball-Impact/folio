<script lang="ts">
	export type OperationStepStatus = 'pending' | 'active' | 'done' | 'error';
	export type OperationStep = {
		id: string;
		label: string;
		status: OperationStepStatus;
		detail?: string;
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
					<button type="button" onclick={() => onDismiss?.()}>{dismissLabel}</button>
				</div>
			{/if}
		</div>
	</div>
{/if}
