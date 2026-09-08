import type { PlatformKey, ProjectCard, ProjectSubmitInput } from '$lib/types';

const PROJECT_TITLE_MAX_CHARS = 48;
const PROJECT_ONE_LINER_MAX_CHARS = 56;
const PROJECT_TAG_MAX_COUNT = 5;

type SubmitPlatformKey = PlatformKey | 'other';

export function validateProjectInput(input: ProjectSubmitInput) {
	if (!input.title.trim()) {
		return '프로젝트명을 입력하세요.';
	}
	if (input.title.length > PROJECT_TITLE_MAX_CHARS) {
		return `프로젝트명은 최대 ${PROJECT_TITLE_MAX_CHARS}자까지 입력할 수 있습니다.`;
	}
	if (input.one_liner.length > PROJECT_ONE_LINER_MAX_CHARS) {
		return `프로젝트 한 줄 소개는 최대 ${PROJECT_ONE_LINER_MAX_CHARS}자까지 입력할 수 있습니다.`;
	}
	if (!input.problem.trim() && !input.dataset.trim() && !input.process.trim() && !input.insights.trim()) {
		return '프로젝트 본문을 한 섹션 이상 입력하세요.';
	}
	if (input.power_bi_url.trim() && !normalizePowerBIEmbedUrl(input.power_bi_url)) {
		return 'Embed Code를 확인하세요. iframe 코드 또는 https URL을 입력해야 합니다.';
	}
	if (input.report_url.trim() && !normalizeOptionalUrl(input.report_url)) {
		return 'Web App URL은 http:// 또는 https://로 시작해야 합니다.';
	}
	if (input.github_url.trim() && !normalizeOptionalUrl(input.github_url)) {
		return 'GitHub URL은 http:// 또는 https://로 시작해야 합니다.';
	}
	if (input.thumbnail_mode === 'manual_url' && !normalizeOptionalUrl(input.thumbnail_url)) {
		return '썸네일 URL은 http:// 또는 https://로 시작해야 합니다.';
	}
	return '';
}

export function buildProjectPayload(input: ProjectSubmitInput) {
	const powerBiUrl = input.delete_pbix ? null : normalizePowerBIEmbedUrl(input.power_bi_url);
	const thumbnailUrl = input.delete_thumbnail || input.thumbnail_mode !== 'manual_url' ? null : normalizeOptionalUrl(input.thumbnail_url);
	const thumbnailMode = input.delete_thumbnail || input.thumbnail_mode === 'upload' ? 'auto_cover' : input.thumbnail_mode;
	return {
		title: input.title.trim(),
		one_liner: input.one_liner.trim() || null,
		problem: input.problem.trim(),
		dataset: input.dataset.trim() || null,
		process: input.process.trim() || null,
		insights: input.insights.trim(),
		power_bi_url: powerBiUrl,
		report_url: normalizeOptionalUrl(input.report_url),
		github_url: normalizeOptionalUrl(input.github_url),
		thumbnail_url: thumbnailUrl,
		thumbnail_mode: thumbnailMode,
		project_type: projectTypeForPlatform(input.platform),
		platform_key: normalizeSubmitPlatform(input.platform),
		status: 'published',
		embed_status: powerBiUrl ? 'supported' : 'external_only',
		tags: tagsWithPlatform(input.tags, input.platform),
		is_public: input.is_public
	};
}

export function projectInputForPbixReplacement(
	input: ProjectSubmitInput,
	mode: 'create' | 'edit',
	hasPbixFile: boolean
) {
	return mode === 'edit' && hasPbixFile && input.delete_pbix ? { ...input, delete_pbix: false } : input;
}

export function normalizeOptionalUrl(value: string) {
	const rawValue = value.trim();
	if (!rawValue) {
		return null;
	}
	try {
		const url = new URL(rawValue);
		return ['http:', 'https:'].includes(url.protocol) && url.hostname ? rawValue : null;
	} catch {
		return null;
	}
}

export function normalizePowerBIEmbedUrl(value: string | null | undefined) {
	let rawValue = (value ?? '').trim();
	if (!rawValue) {
		return null;
	}
	if (rawValue.toLowerCase().startsWith('<iframe')) {
		const match = rawValue.match(/\ssrc=["']([^"']+)["']/i);
		rawValue = match?.[1]?.trim() || rawValue;
	}
	return normalizeOptionalUrl(rawValue);
}

function tagsWithPlatform(tags: string, platformKey: SubmitPlatformKey) {
	const normalizedTags = normalizeTags(tags).filter((tag) => !isPlatformTag(tag));
	if (platformKey === 'other') {
		return normalizedTags.slice(0, PROJECT_TAG_MAX_COUNT);
	}
	const platformLabel = platformLabelFor(platformKey);
	return [platformLabel, ...normalizedTags].slice(0, PROJECT_TAG_MAX_COUNT);
}

function normalizeTags(value: string) {
	const tags: string[] = [];
	for (const tag of value.replaceAll('#', '').split(',')) {
		const normalized = tag.trim();
		if (normalized && !tags.includes(normalized)) {
			tags.push(normalized);
		}
	}
	return tags;
}

function isPlatformTag(value: string) {
	const normalized = value.trim().toLowerCase().replaceAll(' ', '');
	return ['powerbi', 'pbi', 'tableau', 'vizgallery', 'lookerstudio', 'datastudio', 'streamlit'].includes(normalized);
}

function platformLabelFor(platformKey: SubmitPlatformKey) {
	const labels: Record<PlatformKey, string> = {
		powerbi: 'Power BI',
		tableau: 'Tableau',
		datastudio: 'Data Studio',
		streamlit: 'Streamlit'
	};
	return platformKey === 'other' ? '기타' : labels[platformKey];
}

function projectTypeForPlatform(platformKey: SubmitPlatformKey) {
	const projectTypes: Record<SubmitPlatformKey, ProjectCard['project_type']> = {
		powerbi: 'powerbi',
		tableau: 'tableau',
		datastudio: 'looker',
		streamlit: 'streamlit',
		other: 'other'
	};
	return projectTypes[platformKey];
}

function normalizeSubmitPlatform(value: SubmitPlatformKey) {
	return value === 'other' ? null : value;
}
