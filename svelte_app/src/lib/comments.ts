import { currentSession } from '$lib/auth';
import { getSupabaseClient } from '$lib/supabase';
import type { ProjectComment } from '$lib/types';

type CommentRow = Omit<ProjectComment, 'author' | 'children'>;

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

export async function createProjectComment(projectId: string, body: string) {
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

	const { error } = await supabase.from('comments').insert({
		project_id: projectId,
		author_id: session.user.id,
		body: normalizedBody,
		parent_id: null,
		depth: 0
	});

	if (error) {
		return { ok: false, message: '댓글 등록에 실패했습니다. 잠시 후 다시 시도하세요.' };
	}

	return { ok: true, message: '댓글이 등록되었습니다.' };
}

export async function isCommentAuthenticated() {
	return Boolean(await currentSession());
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
