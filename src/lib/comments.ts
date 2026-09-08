import { currentSession } from '$lib/auth';
import { getSupabaseClient } from '$lib/supabase';
import type { ProjectComment } from '$lib/types';

type CommentRow = Omit<ProjectComment, 'author' | 'children'>;

type CommentMutationOptions = {
	projectAuthorId?: string | null;
	projectTitle?: string | null;
};

export async function listProjectComments(projectId: string) {
	const supabase = getSupabaseClient();
	if (!supabase) {
		return {
			comments: [],
			error: 'Supabase 환경 변수가 설정되지 않았습니다.'
		};
	}

	const { data, error } = await supabase
		.from('comments')
		.select('id,project_id,author_id,parent_id,body,depth,is_deleted,created_at')
		.eq('project_id', projectId)
		.order('created_at', { ascending: true });

	if (error) {
		return {
			comments: [],
			error: '댓글을 불러오지 못했습니다.'
		};
	}

	const comments = await attachCommentAuthors((Array.isArray(data) ? data : []).map(normalizeComment));
	return {
		comments: buildCommentTree(comments),
		error: ''
	};
}

export async function createProjectComment(projectId: string, body: string, options: CommentMutationOptions = {}) {
	return createComment(projectId, body, null, options);
}

export async function createProjectReply(projectId: string, parentId: string, body: string, options: CommentMutationOptions = {}) {
	return createComment(projectId, body, parentId, options);
}

export async function deleteProjectComment(commentId: string) {
	const supabase = getSupabaseClient();
	const session = await currentSession();
	if (!supabase || !session) {
		return { ok: false, message: '로그인 후 댓글을 삭제할 수 있습니다.' };
	}

	const { error } = await supabase.from('comments').delete().eq('id', commentId).eq('author_id', session.user.id);
	if (error) {
		return { ok: false, message: '댓글 삭제에 실패했습니다. 잠시 후 다시 시도하세요.' };
	}

	return { ok: true, message: '댓글이 삭제되었습니다.' };
}

export async function currentCommentUserId() {
	const session = await currentSession();
	return session?.user.id ?? null;
}

export async function isCommentAuthenticated() {
	return Boolean(await currentSession());
}

export async function markProjectCommentsSeen(projectId: string, projectAuthorId?: string | null) {
	const supabase = getSupabaseClient();
	const session = await currentSession();
	if (!supabase || !session || !projectAuthorId || session.user.id !== projectAuthorId) {
		return false;
	}

	const now = new Date().toISOString();
	await supabase
		.from('project_comment_reads')
		.upsert(
			{
				project_id: projectId,
				user_id: session.user.id,
				last_read_at: now,
				updated_at: now
			},
			{ onConflict: 'project_id,user_id' }
		);

	await supabase
		.from('notifications')
		.update({ is_read: true, read_at: now })
		.eq('user_id', session.user.id)
		.eq('project_id', projectId)
		.eq('type', 'project_comment')
		.eq('is_read', false);

	return true;
}

async function createComment(projectId: string, body: string, parentId: string | null, options: CommentMutationOptions) {
	const supabase = getSupabaseClient();
	const session = await currentSession();
	if (!supabase || !session) {
		return { ok: false, message: '로그인 후 댓글을 작성할 수 있습니다.' };
	}

	const normalizedBody = body.trim();
	if (!normalizedBody) {
		return { ok: false, message: '댓글 내용을 입력하세요.' };
	}
	if (normalizedBody.length > 1000) {
		return { ok: false, message: '댓글은 1,000자 이내로 입력하세요.' };
	}

	const { data, error } = await supabase
		.from('comments')
		.insert({
			project_id: projectId,
			author_id: session.user.id,
			body: normalizedBody,
			parent_id: parentId,
			depth: parentId ? 1 : 0
		})
		.select('id,project_id,author_id,parent_id,body,depth,is_deleted,created_at')
		.single();

	if (error) {
		return { ok: false, message: '댓글 등록에 실패했습니다. 잠시 후 다시 시도하세요.' };
	}

	await createCommentNotification(projectId, normalizeComment(data), session.user.id, options);
	void sendCommentEmailNotification(String(data.id ?? ''));
	return { ok: true, message: '댓글이 등록되었습니다.' };
}

async function createCommentNotification(
	projectId: string,
	comment: ProjectComment,
	actorId: string,
	options: CommentMutationOptions
) {
	const supabase = getSupabaseClient();
	if (!supabase || !comment.id || !options.projectAuthorId || options.projectAuthorId === actorId) {
		return;
	}

	const { error } = await supabase.from('notifications').insert({
		user_id: options.projectAuthorId,
		actor_id: actorId,
		project_id: projectId,
		comment_id: comment.id,
		type: 'project_comment',
		title: `${options.projectTitle || '프로젝트'}에 새 댓글이 남겨졌습니다.`,
		body: comment.body
	});

	if (error && !isUniqueViolation(error)) {
		console.warn('Failed to create comment notification', error);
	}
}

async function sendCommentEmailNotification(commentId: string) {
	const session = await currentSession();
	if (!session || !commentId) {
		return;
	}
	const response = await fetch(`/api/comments/${commentId}/email-notification`, {
		method: 'POST',
		headers: {
			Authorization: `Bearer ${session.access_token}`
		}
	});
	if (!response.ok && response.status !== 202) {
		console.warn('Failed to request comment email notification');
	}
}

async function attachCommentAuthors(comments: ProjectComment[]) {
	const supabase = getSupabaseClient();
	if (!supabase || comments.length === 0) {
		return comments;
	}

	const authorIds = [...new Set(comments.map((comment) => comment.author_id).filter(Boolean))];
	const { data } = await supabase.from('public_profiles').select('id,name').in('id', authorIds);
	const profileById = new Map(
		(Array.isArray(data) ? data : []).map((profile) => {
			const record = asRecord(profile);
			return [String(record.id), { id: nullableString(record.id) ?? undefined, name: nullableString(record.name) ?? undefined }];
		})
	);

	return comments.map((comment) => ({
		...comment,
		author: profileById.get(comment.author_id) ?? {}
	}));
}

function buildCommentTree(comments: ProjectComment[]) {
	const byId = new Map(comments.map((comment) => [comment.id, { ...comment, children: [] as ProjectComment[] }]));
	const roots: ProjectComment[] = [];

	for (const comment of byId.values()) {
		if (comment.parent_id && byId.has(comment.parent_id)) {
			const parent = byId.get(comment.parent_id)!;
			parent.children.push(comment);
		} else if (comment.parent_id) {
			roots.push({ ...comment, parent_id: null, depth: 0 });
		} else {
			roots.push(comment);
		}
	}

	return roots;
}

function normalizeComment(value: unknown): ProjectComment {
	const payload = asRecord(value) as Partial<CommentRow>;
	return {
		id: String(payload.id ?? ''),
		project_id: String(payload.project_id ?? ''),
		author_id: String(payload.author_id ?? ''),
		parent_id: nullableString(payload.parent_id),
		body: String(payload.body ?? ''),
		depth: Number(payload.depth ?? 0) === 1 ? 1 : 0,
		is_deleted: Boolean(payload.is_deleted ?? false),
		created_at: String(payload.created_at ?? ''),
		author: {},
		children: []
	};
}

function asRecord(value: unknown): Record<string, unknown> {
	return value && typeof value === 'object' ? (value as Record<string, unknown>) : {};
}

function nullableString(value: unknown) {
	const text = String(value ?? '').trim();
	return text || null;
}

function isUniqueViolation(error: unknown) {
	const record = asRecord(error);
	const code = String(record.code ?? '');
	const message = String(record.message ?? '').toLowerCase();
	return code === '23505' || message.includes('duplicate key') || message.includes('unique constraint');
}
