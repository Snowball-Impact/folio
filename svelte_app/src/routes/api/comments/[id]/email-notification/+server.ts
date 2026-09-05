import { json, type RequestHandler } from '@sveltejs/kit';
import { authFailureResponse, authenticateBearerRequest } from '$lib/server/request-auth';
import { sendProjectCommentEmail } from '$lib/server/email';

type CommentRecord = {
	id: string;
	project_id: string;
	author_id: string;
	body: string | null;
};

type ProjectRecord = {
	id: string;
	author_id: string;
	title: string | null;
};

type ProfileRecord = {
	id: string;
	email: string | null;
	name: string | null;
};

export const POST: RequestHandler = async ({ params, request }) => {
	const commentId = params.id;
	if (!commentId) {
		return json({ error: '댓글 ID가 없습니다.' }, { status: 400 });
	}

	const auth = await authenticateBearerRequest(request);
	if (!auth.ok) {
		return authFailureResponse(auth, {
			missingToken: '로그인 후 이메일 알림을 요청할 수 있습니다.',
			unavailable: '이메일 알림 서버 환경 변수가 설정되지 않았습니다.',
			invalidSession: '로그인 세션을 확인하지 못했습니다.'
		});
	}

	const { data: comment, error: commentError } = await auth.serviceClient
		.from('comments')
		.select('id,project_id,author_id,body')
		.eq('id', commentId)
		.maybeSingle<CommentRecord>();
	if (commentError || !comment) {
		return json({ error: '댓글을 찾을 수 없습니다.' }, { status: 404 });
	}
	if (comment.author_id !== auth.user.id) {
		return json({ error: '본인이 작성한 댓글만 이메일 알림을 요청할 수 있습니다.' }, { status: 403 });
	}

	const { data: project, error: projectError } = await auth.serviceClient
		.from('projects')
		.select('id,author_id,title')
		.eq('id', comment.project_id)
		.maybeSingle<ProjectRecord>();
	if (projectError || !project || project.author_id === auth.user.id) {
		return json({ ok: true, skipped: true, message: '이메일 알림 대상이 없습니다.' });
	}

	const [{ data: recipient }, { data: actor }] = await Promise.all([
		auth.serviceClient.from('profiles').select('id,email,name').eq('id', project.author_id).maybeSingle<ProfileRecord>(),
		auth.serviceClient.from('profiles').select('id,email,name').eq('id', auth.user.id).maybeSingle<ProfileRecord>()
	]);

	try {
		const result = await sendProjectCommentEmail({
			recipient: recipient ?? { id: project.author_id, email: null, name: null },
			actor: actor ?? null,
			project,
			comment
		});
		return json(result, { status: result.ok ? 200 : 202 });
	} catch (error) {
		console.warn('Failed to send comment email notification', error);
		return json({ ok: false, skipped: false, message: '이메일 알림 발송에 실패했습니다.' }, { status: 202 });
	}
};
