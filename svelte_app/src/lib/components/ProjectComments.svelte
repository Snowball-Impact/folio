<script lang="ts">
	import { onMount } from 'svelte';
	import { createProjectComment, isCommentAuthenticated, listProjectComments } from '$lib/comments';
	import { formatDate } from '$lib/format';
	import type { ProjectComment } from '$lib/types';

	let { projectId, initialCommentCount }: { projectId: string; initialCommentCount: number } = $props();

	let initialized = $state(false);
	let comments = $state<ProjectComment[]>([]);
	let commentCount = $state(0);
	let body = $state('');
	let authenticated = $state(false);
	let loading = $state(true);
	let submitting = $state(false);
	let message = $state('');
	let error = $state('');

	$effect(() => {
		if (!initialized) {
			commentCount = initialCommentCount;
			initialized = true;
		}
	});

	onMount(async () => {
		await refreshComments();
		authenticated = await isCommentAuthenticated();
	});

	async function refreshComments() {
		loading = true;
		const result = await listProjectComments(projectId);
		comments = result.comments;
		commentCount = countComments(comments) || initialCommentCount;
		error = result.error;
		loading = false;
	}

	async function submitComment(event: SubmitEvent) {
		event.preventDefault();
		message = '';
		error = '';
		submitting = true;
		const result = await createProjectComment(projectId, body);
		submitting = false;
		if (!result.ok) {
			error = result.message;
			return;
		}
		body = '';
		message = result.message;
		await refreshComments();
	}

	function countComments(nodes: ProjectComment[]): number {
		return nodes.reduce((total, comment) => total + 1 + countComments(comment.children), 0);
	}
</script>

<section class="comments-panel">
	<div class="comments-heading">
		<h2>댓글 {commentCount}개</h2>
		<p>프로젝트에 대한 의견이나 질문을 남겨보세요.</p>
	</div>

	{#if message}
		<div class="auth-message success">{message}</div>
	{/if}
	{#if error}
		<div class="auth-message error">{error}</div>
	{/if}

	{#if authenticated}
		<form class="comment-form" onsubmit={submitComment}>
			<textarea bind:value={body} maxlength="1000" placeholder="댓글을 남겨보세요."></textarea>
			<button type="submit" disabled={submitting}>{submitting ? '등록 중...' : '댓글 남기기'}</button>
		</form>
	{:else}
		<div class="comments-login-note">
			<span>로그인 후 댓글을 작성할 수 있습니다.</span>
			<a href="/login">로그인하기</a>
		</div>
	{/if}

	<div class="comments-divider"></div>

	{#if loading}
		<div class="comments-empty">댓글을 불러오는 중입니다.</div>
	{:else if comments.length === 0}
		<div class="comments-empty">
			<strong>아직 댓글이 없습니다.</strong>
			<span>첫 댓글로 프로젝트에 대한 의견이나 질문을 남겨보세요.</span>
		</div>
	{:else}
		<div class="comment-list">
			{#each comments as comment, index}
				{@render CommentNode(comment, `${index + 1}`)}
			{/each}
		</div>
	{/if}
</section>

{#snippet CommentNode(comment: ProjectComment, indexLabel: string)}
	<article class="comment-card" class:reply={comment.depth === 1}>
		<div class="comment-index">{indexLabel}</div>
		<div>
			<div class="comment-author-line">
				<strong>{comment.author.name ?? '작성자'}</strong>
				<span>{formatDate(comment.created_at)}</span>
			</div>
			<p>{comment.is_deleted ? '삭제된 댓글입니다.' : comment.body}</p>
		</div>
	</article>
	{#each comment.children as child, childIndex}
		{@render CommentNode(child, `${indexLabel}-${childIndex + 1}`)}
	{/each}
{/snippet}
