import { currentSession } from '$lib/auth';
import { getSupabaseClient } from '$lib/supabase';

export type LikeState = {
	authenticated: boolean;
	liked: boolean;
	error: string;
};

export async function loadLikeState(projectId: string): Promise<LikeState> {
	const supabase = getSupabaseClient();
	const session = await currentSession();
	if (!supabase || !session) {
		return { authenticated: false, liked: false, error: '' };
	}

	const { data, error } = await supabase
		.from('likes')
		.select('project_id')
		.eq('project_id', projectId)
		.eq('user_id', session.user.id)
		.maybeSingle();

	if (error) {
		return { authenticated: true, liked: false, error: '좋아요 상태를 불러오지 못했습니다.' };
	}

	return { authenticated: true, liked: Boolean(data), error: '' };
}

export async function setProjectLiked(projectId: string, liked: boolean) {
	const supabase = getSupabaseClient();
	const session = await currentSession();
	if (!supabase || !session) {
		return { ok: false, message: '로그인 후 좋아요를 누를 수 있습니다.' };
	}

	const response = liked
		? await supabase.from('likes').insert({ project_id: projectId, user_id: session.user.id })
		: await supabase.from('likes').delete().eq('project_id', projectId).eq('user_id', session.user.id);

	if (response.error) {
		const duplicate = response.error.message.toLowerCase().includes('duplicate');
		if (liked && duplicate) {
			return { ok: true, message: '이미 좋아요를 누른 프로젝트입니다.' };
		}
		return { ok: false, message: '좋아요 처리에 실패했습니다. 잠시 후 다시 시도하세요.' };
	}

	return { ok: true, message: liked ? '좋아요를 눌렀습니다.' : '좋아요를 취소했습니다.' };
}
