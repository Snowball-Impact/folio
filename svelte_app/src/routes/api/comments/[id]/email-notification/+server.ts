import { json, type RequestHandler } from '@sveltejs/kit';
import { getSupabaseServerClient, getSupabaseUserClient } from '$lib/server/supabase';
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

	const accessToken = bearerToken(request);
	if (!accessToken) {
		return json({ error: '로그인 후 이메일 알림을 요청할 수 있습니다.' }, { status: 401 });
	}

	const userClient = getSupabaseUserClient(accessToken);
	const serviceClient = getSupabaseServerClient();
	if (!userClient || !serviceClient) {
		return json({ error: '이메일 알림 서버 환경 변수가 설정되지 않았습니다.' }, { status: 503 });
	}

	const { data: userData, error: userError } = await userClient.auth.getUser(accessToken);
	const user = userData.user;
	if (userError || !user) {
		return json({ error: '로그인 세션을 확인하지 못했습니다.' }, { status: 401 });
	}

	const { data: comment, error: commentError } = await serviceClient
		.from('comments')
		.select('id,project_id,author_id,body')
		.eq('id', commentId)
		.maybeSingle<CommentRecord>();
	if (commentError || !comment) {
		return json({ error: '댓글을 찾을 수 없습니다.' }, { status: 404 });
	}
	if (comment.author_id !== user.id) {
		return json({ error: '본인이 작성한 댓글만 이메일 알림을 요청할 수 있습니다.' }, { status: 403 });
	}

	const { data: project, error: projectError } = await serviceClient
		.from('projects')
		.select('id,author_id,title')
		.eq('id', comment.project_id)
		.maybeSingle<ProjectRecord>();
	if (projectError || !project || project.author_id === user.id) {
		return json({ ok: true, skipped: true, message: '이메일 알림 대상이 없습니다.' });
	}

	const [{ data: recipient }, { data: actor }] = await Promise.all([
		serviceClient.from('profiles').select('id,email,name').eq('id', project.author_id).maybeSingle<ProfileRecord>(),
		serviceClient.from('profiles').select('id,email,name').eq('id', user.id).maybeSingle<ProfileRecord>()
	]);

	try {
		const result = await sendProjectCommentEmail({
			recipient: recipient ?? { id: project.author_id, email: null, name: null },
			actor: actor ?? null,
			project,
			comment
		});
		return json(result, { status: result.ok ? 200 : 202 });
	} catch {
		return json({ ok: false, skipped: false, message: '이메일 알림 발송에 실패했습니다.' }, { status: 202 });
	}
};

function bearerToken(request: Request) {
	const header = request.headers.get('authorization') ?? '';
	const match = header.match(/^Bearer\s+(.+)$/i);
	return match?.[1]?.trim() ?? '';
}
