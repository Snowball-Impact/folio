import {
	loadPowerBIHubContent,
	normalizePowerBIHubTopic
} from '$lib/server/powerbi-content';

export async function load({ url }) {
	const topic = normalizePowerBIHubTopic(url.searchParams.get('topic'));
	return await loadPowerBIHubContent(topic);
}
