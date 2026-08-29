import type { ProjectCard, ProjectSubmitInput } from '$lib/types';

export const PROJECT_PLATFORM_OPTIONS = [
	{ key: 'other', label: '기타' },
	{ key: 'tableau', label: 'Tableau' },
	{ key: 'powerbi', label: 'Power BI' },
	{ key: 'datastudio', label: 'Data Studio' },
	{ key: 'streamlit', label: 'Streamlit' }
] as const satisfies readonly { key: ProjectSubmitInput['platform']; label: string }[];

export function emptyProjectSubmitInput(): ProjectSubmitInput {
	return {
		title: '',
		one_liner: '',
		tags: '',
		platform: 'other',
		problem: '',
		dataset: '',
		process: '',
		insights: '',
		power_bi_url: '',
		report_url: '',
		github_url: '',
		thumbnail_url: '',
		thumbnail_mode: 'auto_cover',
		delete_thumbnail: false,
		delete_pbix: false,
		is_public: true
	};
}

export function projectInputFromProject(value: ProjectCard): ProjectSubmitInput {
	return {
		title: value.title,
		one_liner: value.one_liner ?? '',
		tags: value.tags.join(', '),
		platform: value.platform_key ?? 'other',
		problem: value.problem ?? '',
		dataset: value.dataset ?? '',
		process: value.process ?? '',
		insights: value.insights ?? '',
		power_bi_url: value.power_bi_url ?? '',
		report_url: value.report_url ?? '',
		github_url: value.github_url ?? '',
		thumbnail_url: value.thumbnail_url ?? '',
		thumbnail_mode: value.thumbnail_mode,
		delete_thumbnail: false,
		delete_pbix: false,
		is_public: value.is_public
	};
}

export function previewTags(tags: string, platform: ProjectSubmitInput['platform']) {
	const rawTags = tags
		.replaceAll('#', '')
		.split(',')
		.map((tag) => tag.trim())
		.filter(Boolean);
	const uniqueTags = [...new Set(rawTags)];
	if (platform === 'other') {
		return uniqueTags.slice(0, 5);
	}
	const platformLabel = PROJECT_PLATFORM_OPTIONS.find((option) => option.key === platform)?.label ?? '';
	const platformAliases = new Set(
		[
			platformLabel,
			platform,
			platform === 'datastudio' ? 'Data Studio' : '',
			platform === 'datastudio' ? 'Looker Studio' : '',
			platform === 'powerbi' ? 'PowerBI' : '',
			platform === 'powerbi' ? 'Power BI' : ''
		]
			.filter(Boolean)
			.map(normalizeProjectTag)
	);
	return [platformLabel, ...uniqueTags.filter((tag) => !platformAliases.has(normalizeProjectTag(tag)))].slice(0, 5);
}

export function projectFormTagLabel(tags: string, platform: ProjectSubmitInput['platform']) {
	const rawTags = tags
		.replaceAll('#', '')
		.split(',')
		.map((tag) => tag.trim())
		.filter(Boolean);
	const platformOption = PROJECT_PLATFORM_OPTIONS.find((option) => option.key === platform);
	const platformTag = platformOption?.key === 'other' ? '' : platformOption?.label ?? '';
	const platformAliases = new Set(
		[
			platformOption?.label ?? '',
			platformOption?.key ?? '',
			platform === 'datastudio' ? 'Data Studio' : '',
			platform === 'datastudio' ? 'Looker Studio' : '',
			platform === 'powerbi' ? 'PowerBI' : '',
			platform === 'powerbi' ? 'Power BI' : ''
		]
			.filter(Boolean)
			.map(normalizeProjectTag)
	);
	const visibleTags = [platformTag, ...rawTags.filter((tag) => !platformAliases.has(normalizeProjectTag(tag)))]
		.filter(Boolean)
		.filter((tag, index, values) => values.findIndex((value) => normalizeProjectTag(value) === normalizeProjectTag(tag)) === index)
		.slice(0, 5);
	return visibleTags.length ? `태그 ${visibleTags.map((tag) => `#${tag}`).join(' ')}` : '태그';
}

export function normalizeProjectTag(value: string) {
	return value.trim().toLowerCase().replaceAll(' ', '');
}
