<script lang="ts">
	import { onMount } from 'svelte';
	import {
		createProjectComment,
		createProjectReply,
		currentCommentUserId,
		deleteProjectComment,
		isCommentAuthenticated,
		listProjectComments,
		markProjectCommentsSeen
	} from '$lib/comments';
	import { formatDateTime } from '$lib/format';
	import type { ProjectComment } from '$lib/types';

	let {
		projectId,
		projectAuthorId,
		projectTitle,
		initialCommentCount
	}: {
		projectId: string;
		projectAuthorId?: string | null;
		projectTitle?: string | null;
		initialCommentCount: number;
	} = $props();

	let initialized = $state(false);
	let comments = $state<ProjectComment[]>([]);
	let commentCount = $state(0);
	let body = $state('');
	let replyBody = $state('');
	let replyTargetId = $state<string | null>(null);
	let deleteConfirmId = $state<string | null>(null);
	let currentUserId = $state<string | null>(null);
	let authenticated = $state(false);
	let loading = $state(true);
	let submitting = $state(false);
	let replySubmitting = $state(false);
	let deleting = $state(false);
	let message = $state('');
	let error = $state('');
	let currentPage = $state(1);
	const COMMENTS_PAGE_SIZE = 20;
	const totalPages = $derived(Math.max(1, Math.ceil(comments.length / COMMENTS_PAGE_SIZE)));
	const visibleComments = $derived(
		comments.slice((currentPage - 1) * COMMENTS_PAGE_SIZE, currentPage * COMMENTS_PAGE_SIZE)
	);

	$effect(() => {
		if (currentPage > totalPages) currentPage = totalPages;
		if (currentPage < 1) currentPage = 1;
	});

	$effect(() => {
		if (!initialized) {
			commentCount = initialCommentCount;
			initialized = true;
		}
	});

	onMount(async () => {
		await refreshComments();
		authenticated = await isCommentAuthenticated();
		currentUserId = await currentCommentUserId();
		if (currentUserId === projectAuthorId) {
			await markProjectCommentsSeen(projectId, projectAuthorId);
		}
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
		const result = await createProjectComment(projectId, body, { projectAuthorId, projectTitle });
		submitting = false;
		if (!result.ok) {
			error = result.message;
			return;
		}
		body = '';
		message = result.message;
		await refreshComments();
	}

	async function submitReply(event: SubmitEvent, parentId: string) {
		event.preventDefault();
		message = '';
		error = '';
		replySubmitting = true;
		const result = await createProjectReply(projectId, parentId, replyBody, { projectAuthorId, projectTitle });
		replySubmitting = false;
		if (!result.ok) {
			error = result.message;
			return;
		}
		replyBody = '';
		replyTargetId = null;
		message = result.message;
		await refreshComments();
	}

	async function removeComment(commentId: string) {
		message = '';
		error = '';
		if (deleteConfirmId !== commentId) {
			deleteConfirmId = commentId;
			return;
		}
		deleting = true;
		const result = await deleteProjectComment(commentId);
		deleting = false;
		if (!result.ok) {
			error = result.message;
			return;
		}
		deleteConfirmId = null;
		message = result.message;
		await refreshComments();
	}

	function countComments(nodes: ProjectComment[]): number {
		return nodes.reduce((total, comment) => total + 1 + countComments(comment.children), 0);
	}
</script>

<section id="project-comments" class="comments-panel">
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
			<a href={`/login?next=/projects/${projectId}`}>로그인하기</a>
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
			{#each visibleComments as comment, index}
				{@render CommentNode(comment, `${(currentPage - 1) * COMMENTS_PAGE_SIZE + index + 1}`)}
			{/each}
		</div>
	{/if}

	<div class="comments-pagination" aria-label="댓글 페이지 이동">
		{#if totalPages > 1}
			<button type="button" disabled={currentPage <= 1} onclick={() => (currentPage -= 1)}>이전</button>
		{/if}
		<span class="comments-page-status">{totalPages <= 1 ? currentPage : `${currentPage} / ${totalPages}`}</span>
		{#if totalPages > 1}
			<button type="button" disabled={currentPage >= totalPages} onclick={() => (currentPage += 1)}>다음</button>
		{/if}
	</div>
</section>

{#snippet CommentNode(comment: ProjectComment, indexLabel: string)}
	<article class="comment-card" class:reply={comment.depth === 1}>
		<div class="comment-index">{indexLabel}</div>
		<div class="comment-content">
			<div class="comment-author-line">
				<strong>{comment.author.name ?? '작성자'}</strong>
				{#if projectAuthorId && comment.author_id === projectAuthorId}
					<span class="comment-author-badge">작성자</span>
				{/if}
			</div>
			<p>{comment.is_deleted ? '삭제된 댓글입니다.' : comment.body}</p>
			<div class="comment-footer">
				{#if authenticated && !comment.is_deleted}
					<div class="comment-actions">
						{#if comment.depth === 0}
							<button type="button" onclick={() => (replyTargetId = replyTargetId === comment.id ? null : comment.id)}>
								답글
							</button>
						{/if}
						{#if authenticated}
							<button type="button" class:danger={deleteConfirmId === comment.id} disabled={deleting} onclick={() => removeComment(comment.id)}>
								{deleteConfirmId === comment.id ? '삭제 확인' : '삭제'}
							</button>
							{#if deleteConfirmId === comment.id}
								<button type="button" onclick={() => (deleteConfirmId = null)}>취소</button>
							{/if}
						{/if}
					</div>
				{/if}
				<span class="comment-date">{formatDateTime(comment.created_at)}</span>
			</div>
		</div>
	</article>
	{#if authenticated && replyTargetId === comment.id}
		<form class="comment-form reply-form" onsubmit={(event) => submitReply(event, comment.id)}>
			<textarea bind:value={replyBody} maxlength="1000" placeholder="답글을 남겨보세요."></textarea>
			<div class="reply-form-actions">
				<button type="button" class="secondary" onclick={() => (replyTargetId = null)}>취소</button>
				<button type="submit" disabled={replySubmitting}>{replySubmitting ? '등록 중...' : '답글 남기기'}</button>
			</div>
		</form>
	{/if}
	{#each comment.children as child, childIndex}
		{@render CommentNode(child, `${indexLabel}.${childIndex + 1}`)}
	{/each}
{/snippet}
