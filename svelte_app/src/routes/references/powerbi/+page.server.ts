import { loadReferenceProjects } from '$lib/projects';
import type { ReferenceSort } from '$lib/types';

const sortValues = new Set<ReferenceSort>(['latest', 'likes', 'views']);

export async function load({ url }) {
	const requestedSort = url.searchParams.get('sort') as ReferenceSort | null;
	const sort = requestedSort && sortValues.has(requestedSort) ? requestedSort : 'latest';
	return await loadReferenceProjects('powerbi', sort);
}
