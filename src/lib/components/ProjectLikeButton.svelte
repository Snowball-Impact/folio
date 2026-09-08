<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { loadLikeState, setProjectLiked } from '$lib/likes';
	import { formatCount } from '$lib/format';

	let {
		projectId,
		initialLikeCount
	}: {
		projectId: string;
		initialLikeCount: number;
	} = $props();

	let initialized = $state(false);
	let likeCount = $state(0);
	let authenticated = $state(false);
	let liked = $state(false);
	let message = $state('');
	let error = $state('');
	let loading = $state(true);
	let saving = $state(false);

	$effect(() => {
		if (!initialized) {
			likeCount = initialLikeCount;
			initialized = true;
		}
	});

	onMount(async () => {
		const state = await loadLikeState(projectId);
		authenticated = state.authenticated;
		liked = state.liked;
		error = state.error;
		loading = false;
	});

	async function toggleLike() {
		message = '';
		error = '';
		if (!authenticated) {
			await goto(`/login?next=${encodeURIComponent(window.location.pathname)}`);
			return;
		}

		const nextLiked = !liked;
		saving = true;
		const previousLiked = liked;
		const previousCount = likeCount;
		liked = nextLiked;
		likeCount = Math.max(0, likeCount + (nextLiked ? 1 : -1));

		const result = await setProjectLiked(projectId, nextLiked);
		saving = false;
		if (!result.ok) {
			liked = previousLiked;
			likeCount = previousCount;
			error = result.message;
			return;
		}
		message = result.message;
	}
</script>

<div class="like-control">
	<button class:liked type="button" disabled={loading || saving} onclick={toggleLike}>
		<span aria-hidden="true">{liked ? '♥' : '♡'}</span>
		좋아요 {formatCount(likeCount)}
	</button>
	{#if error}
		<p class="like-error">{error}</p>
	{:else if message}
		<p class="like-message">{message}</p>
	{/if}
</div>