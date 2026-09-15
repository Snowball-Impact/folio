import { error } from '@sveltejs/kit';
import { loadProjectDetail } from '$lib/projects';
import { frameSourceFromUrl } from '$lib/server/security-headers';

export async function load({ params, locals }) {
	const result = await loadProjectDetail(params.id);
	if (!result.project) {
		throw error(404, result.error || '프로젝트를 찾을 수 없습니다.');
	}
	const frameSource = frameSourceFromUrl(result.project.power_bi_url);
	locals.frameSources = frameSource ? [frameSource] : [];
	return result;
}
