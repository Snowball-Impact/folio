<script lang="ts">
	export type OperationStepStatus = 'pending' | 'active' | 'done' | 'error';
	export type OperationStep = {
		id: string;
		label: string;
		status: OperationStepStatus;
		detail?: string;
	};

	let { title = '작업 진행', progress = 0, steps = [] }: { title?: string; progress?: number; steps: OperationStep[] } = $props();
	const boundedProgress = $derived(Math.max(0, Math.min(100, Math.round(progress))));
	const activeStep = $derived(steps.find((step) => step.status === 'active') ?? steps.at(-1));
</script>

{#if steps.length > 0}
	<section class="operation-progress-panel" aria-live="polite" aria-label={title}>
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
	</section>
{/if}