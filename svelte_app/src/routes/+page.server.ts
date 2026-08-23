import { loadHomeSnapshot } from '$lib/projects';

export async function load() {
	return await loadHomeSnapshot('powerbi');
}
