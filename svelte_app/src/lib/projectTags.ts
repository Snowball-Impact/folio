const EXCLUDED_HOME_TAGS = new Set(['powerbi', 'pbi', 'reference', 'references', '레퍼런스', '참고', '전체', 'all']);

export function normalizeHomeTag(value: string | undefined | null) {
	const tag = String(value ?? '').trim().replace(/^#+/, '');
	return tag && tag !== '전체' ? tag : '';
}

export function comparableProjectTag(value: string) {
	return value.trim().replace(/^#+/, '').toLowerCase().replaceAll(' ', '');
}

export function projectTagsInclude(tags: string[], selectedTag: string) {
	const targetTag = comparableProjectTag(selectedTag);
	return !targetTag || tags.some((tag) => comparableProjectTag(tag) === targetTag);
}

export function popularTagsFromTagLists(tagLists: string[][], limit: number) {
	const counts = new Map<string, { label: string; count: number }>();
	for (const tags of tagLists) {
		for (const tag of tags) {
			const label = tag.trim();
			const comparableTag = comparableProjectTag(label);
			if (!label || EXCLUDED_HOME_TAGS.has(comparableTag)) {
				continue;
			}
			const current = counts.get(comparableTag);
			counts.set(comparableTag, {
				label: current?.label ?? label,
				count: (current?.count ?? 0) + 1
			});
		}
	}
	return [...counts.values()]
		.sort((first, second) => second.count - first.count || first.label.localeCompare(second.label, 'ko-KR'))
		.slice(0, limit)
		.map((entry) => entry.label);
}

export function normalizePopularHomeTags(tags: string[], limit: number) {
	const seen = new Set<string>();
	const normalizedTags: string[] = [];
	for (const tag of tags) {
		const label = tag.trim();
		const comparableTag = comparableProjectTag(label);
		if (!label || EXCLUDED_HOME_TAGS.has(comparableTag) || seen.has(comparableTag)) {
			continue;
		}
		seen.add(comparableTag);
		normalizedTags.push(label);
		if (normalizedTags.length >= limit) {
			break;
		}
	}
	return normalizedTags;
}

export function isExcludedHomeTag(tag: string) {
	return EXCLUDED_HOME_TAGS.has(comparableProjectTag(tag));
}
