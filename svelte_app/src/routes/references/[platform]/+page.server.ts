import { error } from '@sveltejs/kit';
import { loadReferenceProjects, REFERENCE_PLATFORMS } from '$lib/projects';
import type { PlatformKey, ReferenceSort } from '$lib/types';

const sortValues = new Set<ReferenceSort>(['latest', 'likes', 'views']);

export async function load({ params, url }) {
	const platformKey = params.platform as PlatformKey;
	if (!(platformKey in REFERENCE_PLATFORMS)) {
		throw error(404, '레퍼런스 플랫폼을 찾을 수 없습니다.');
	}
	const requestedSort = url.searchParams.get('sort') as ReferenceSort | null;
	const sort = requestedSort && sortValues.has(requestedSort) ? requestedSort : 'latest';
	return await loadReferenceProjects(platformKey, sort);
}