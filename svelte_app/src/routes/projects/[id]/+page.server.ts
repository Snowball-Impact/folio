import { error } from '@sveltejs/kit';
import { loadProjectDetail } from '$lib/projects';

export async function load({ params }) {
	const result = await loadProjectDetail(params.id);
	if (!result.project) {
		throw error(404, result.error || '프로젝트를 찾을 수 없습니다.');
	}
	return result;
}
