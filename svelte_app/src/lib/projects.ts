import { getSupabaseClient } from '$lib/supabase';
import { currentSession } from '$lib/auth';
import type {
	HomeSnapshot,
	PlatformKey,
	ProjectCard,
	ProjectDetail,
	ReferenceProjectsResult,
	ReferenceSort
} from '$lib/types';

const HOME_LIKED_PROJECT_SAMPLE_MULTIPLIER = 20;
const REFERENCE_FETCH_LIMIT = 500;
const POWERBI_URL_MARKERS = ['app.powerbi.com', 'powerbi.com'];
const POWERBI_TAG_ALIASES = ['powerbi', 'power bi', 'pbi'];
const PROJECT_TITLE_MAX_CHARS = 48;
const PROJECT_ONE_LINER_MAX_CHARS = 56;
const PROJECT_TAG_MAX_COUNT = 5;

type SubmitPlatformKey = PlatformKey | 'other';

export type ProjectSubmitInput = {
	title: string;
	one_liner: string;
	tags: string;
	platform: SubmitPlatformKey;
	problem: string;
	dataset: string;
	process: string;
	insights: string;
	power_bi_url: string;
	report_url: string;
	github_url: string;
	thumbnail_url: string;
	thumbnail_mode: 'auto_cover' | 'manual_url';
	is_public: boolean;
};

export const REFERENCE_PLATFORMS = {
	powerbi: {
		key: 'powerbi',
		label: 'Power BI',
		description: 'Power BI 공개 보고서와 대시보드 레퍼런스입니다.'
	}
} as const;

const emptyHomeSnapshot: HomeSnapshot = {
	total_project_count: 0,
	popular_tags: [],
	recent_projects: [],
	viewed_projects: [],
	liked_projects: []
};

export async function loadHomeSnapshot(platformKey: PlatformKey | null = 'powerbi') {
	const supabase = getSupabaseClient();
	if (!supabase) {
		return {
			snapshot: emptyHomeSnapshot,
			error: 'Supabase 환경 변수가 설정되지 않았습니다.'
		};
	}

	const limit = 6;
	const { data, error } = await supabase.rpc('home_project_snapshot', {
		p_limit: limit,
		p_tag_limit: 40,
		p_like_sample_limit: limit * HOME_LIKED_PROJECT_SAMPLE_MULTIPLIER,
		p_platform_key: platformKey
	});

	if (error) {
		return {
			snapshot: emptyHomeSnapshot,
			error: '홈 프로젝트를 불러오지 못했습니다.'
		};
	}

	return {
		snapshot: normalizeHomeSnapshot(data),
		error: ''
	};
}

export async function loadProjectDetail(projectId: string) {
	const supabase = getSupabaseClient();
	if (!supabase) {
		return {
			project: null,
			error: 'Supabase 환경 변수가 설정되지 않았습니다.'
		};
	}

	const { data, error } = await supabase.rpc('project_detail_snapshot', {
		p_project_id: projectId
	});

	if (error) {
		return {
			project: null,
			error: '프로젝트를 불러오지 못했습니다.'
		};
	}

	const project = data ? normalizeProject(data) : null;
	if (!project || project.status === 'deleted') {
		return {
			project: null,
			error: '프로젝트를 찾을 수 없습니다.'
		};
	}

	return {
		project,
		error: ''
	};
}

export async function loadReferenceProjects(
	platformKey: PlatformKey = 'powerbi',
	sort: ReferenceSort = 'latest'
): Promise<ReferenceProjectsResult> {
	const supabase = getSupabaseClient();
	const platform = REFERENCE_PLATFORMS.powerbi;
	if (!supabase) {
		return {
			platform,
			sort,
			projects: [],
			error: 'Supabase 환경 변수가 설정되지 않았습니다.'
		};
	}
	if (platformKey !== 'powerbi') {
		return {
			platform,
			sort,
			projects: [],
			error: '아직 공개된 레퍼런스 플랫폼이 아닙니다.'
		};
	}

	const { data, error } = await supabase
		.from('projects')
		.select(projectListColumns)
		.eq('is_public', true)
		.eq('status', 'published')
		.order('created_at', { ascending: false })
		.limit(REFERENCE_FETCH_LIMIT);

	if (error) {
		return {
			platform,
			sort,
			projects: [],
			error: '레퍼런스를 불러오지 못했습니다.'
		};
	}

	const referenceRows = (Array.isArray(data) ? data : [])
		.map(normalizeProject)
		.filter((project) => referencePlatformForProject(project) === platformKey);
	const projects = await attachPublicProjectMetadata(referenceRows);
	sortReferenceProjects(projects, sort);

	return {
		platform,
		sort,
		projects,
		error: ''
	};
}

export async function recordProjectView(projectId: string, anonymousViewerId: string) {
	const supabase = getSupabaseClient();
	if (!supabase) {
		return false;
	}

	const { data, error } = await supabase.rpc('increment_project_view_count', {
		project_id_input: projectId,
		anonymous_viewer_id_input: anonymousViewerId
	});

	return !error && data === true;
}

export async function createProject(input: ProjectSubmitInput) {
	const supabase = getSupabaseClient();
	const session = await currentSession();
	if (!supabase || !session) {
		return { ok: false, message: '로그인 후 프로젝트를 등록할 수 있습니다.', projectId: null };
	}

	const validationError = validateProjectInput(input);
	if (validationError) {
		return { ok: false, message: validationError, projectId: null };
	}

	const powerBiUrl = normalizePowerBIEmbedUrl(input.power_bi_url);
	const reportUrl = normalizeOptionalUrl(input.report_url);
	const githubUrl = normalizeOptionalUrl(input.github_url);
	const thumbnailUrl = input.thumbnail_mode === 'manual_url' ? normalizeOptionalUrl(input.thumbnail_url) : null;
	const platformKey = normalizeSubmitPlatform(input.platform);
	const payload = {
		author_id: session.user.id,
		title: input.title.trim(),
		one_liner: input.one_liner.trim() || null,
		problem: input.problem.trim(),
		dataset: input.dataset.trim() || null,
		process: input.process.trim() || null,
		insights: input.insights.trim(),
		power_bi_url: powerBiUrl,
		report_url: reportUrl,
		github_url: githubUrl,
		thumbnail_url: thumbnailUrl,
		thumbnail_mode: input.thumbnail_mode,
		project_type: projectTypeForPlatform(input.platform),
		platform_key: platformKey,
		status: 'published',
		embed_status: powerBiUrl ? 'supported' : 'external_only',
		tags: tagsWithPlatform(input.tags, input.platform),
		is_public: input.is_public
	};

	const { data, error } = await supabase.from('projects').insert(payload).select('id').single();
	if (error) {
		return { ok: false, message: '프로젝트 등록에 실패했습니다. 잠시 후 다시 시도하세요.', projectId: null };
	}

	return { ok: true, message: '프로젝트가 등록되었습니다.', projectId: String(data.id ?? '') };
}

const projectListColumns = [
	'id',
	'author_id',
	'title',
	'one_liner',
	'problem',
	'dataset',
	'process',
	'insights',
	'tags',
	'thumbnail_url',
	'power_bi_url',
	'report_url',
	'github_url',
	'platform_key',
	'project_type',
	'status',
	'embed_status',
	'is_public',
	'view_count',
	'created_at',
	'updated_at'
].join(',');

function normalizeHomeSnapshot(value: unknown): HomeSnapshot {
	const payload = asRecord(value);
	return {
		total_project_count: Number(payload.total_project_count ?? 0),
		popular_tags: asStringArray(payload.popular_tags),
		recent_projects: asProjectArray(payload.recent_projects),
		viewed_projects: asProjectArray(payload.viewed_projects),
		liked_projects: asProjectArray(payload.liked_projects)
	};
}

async function attachPublicProjectMetadata(projects: ProjectCard[]) {
	const supabase = getSupabaseClient();
	if (!supabase || projects.length === 0) {
		return projects;
	}

	const authorIds = [...new Set(projects.map((project) => project.author_id).filter(Boolean))];
	const projectIds = projects.map((project) => project.id).filter(Boolean);

	const [{ data: profiles }, { data: likes }, { data: comments }] = await Promise.all([
		authorIds.length
			? supabase.from('public_profiles').select('id,name,organization,avatar_url').in('id', authorIds)
			: Promise.resolve({ data: [] }),
		projectIds.length ? supabase.from('likes').select('project_id').in('project_id', projectIds) : Promise.resolve({ data: [] }),
		projectIds.length
			? supabase.from('comments').select('project_id,created_at').in('project_id', projectIds)
			: Promise.resolve({ data: [] })
	]);

	const profileById = new Map(
		(Array.isArray(profiles) ? profiles : []).map((profile) => {
			const record = asRecord(profile);
			return [String(record.id), record];
		})
	);
	const likeCounts = countByProjectId(likes, 'project_id');
	const commentCounts = countByProjectId(comments, 'project_id');
	const latestComments = latestCommentByProjectId(comments);

	return projects.map((project) => {
		const author = profileById.get(project.author_id);
		return {
			...project,
			author: author
				? {
						id: nullableString(author.id) ?? undefined,
						name: nullableString(author.name) ?? undefined,
						organization: nullableString(author.organization),
						avatar_url: nullableString(author.avatar_url)
					}
				: project.author,
			like_count: likeCounts.get(project.id) ?? 0,
			comment_count: commentCounts.get(project.id) ?? 0,
			latest_comment_at: latestComments.get(project.id) ?? null
		};
	});
}

function sortReferenceProjects(projects: ProjectCard[], sort: ReferenceSort) {
	if (sort === 'likes') {
		projects.sort((first, second) => second.like_count - first.like_count || compareDateDesc(first, second));
		return;
	}
	if (sort === 'views') {
		projects.sort((first, second) => second.view_count - first.view_count || compareDateDesc(first, second));
		return;
	}
	projects.sort(compareDateDesc);
}

function compareDateDesc(first: ProjectCard, second: ProjectCard) {
	return Date.parse(second.created_at || '') - Date.parse(first.created_at || '');
}

function referencePlatformForProject(project: ProjectCard) {
	if (project.platform_key === 'powerbi') {
		return 'powerbi';
	}

	const tags = new Set(project.tags.map((tag) => tag.trim().toLowerCase()).filter(Boolean));
	if (POWERBI_TAG_ALIASES.some((alias) => tags.has(alias))) {
		return 'powerbi';
	}

	const urlText = [project.power_bi_url, project.report_url, project.github_url, project.thumbnail_url]
		.map((value) => value?.toLowerCase() ?? '')
		.join(' ');
	if (POWERBI_URL_MARKERS.some((marker) => urlText.includes(marker))) {
		return 'powerbi';
	}

	return null;
}

function validateProjectInput(input: ProjectSubmitInput) {
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
	if (!input.problem.trim()) {
		return '문제 정의를 입력하세요.';
	}
	if (!input.insights.trim()) {
		return '주요 관찰 포인트를 입력하세요.';
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

function normalizeOptionalUrl(value: string) {
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

function normalizePowerBIEmbedUrl(value: string) {
	let rawValue = value.trim();
	if (!rawValue) {
		return null;
	}
	if (rawValue.toLowerCase().startsWith('<iframe')) {
		const match = rawValue.match(/\ssrc=["']([^"']+)["']/i);
		rawValue = match?.[1]?.trim() || rawValue;
	}
	return normalizeOptionalUrl(rawValue);
}

function countByProjectId(rows: unknown, key: string) {
	const counts = new Map<string, number>();
	if (!Array.isArray(rows)) {
		return counts;
	}
	for (const row of rows) {
		const projectId = nullableString(asRecord(row)[key]);
		if (projectId) {
			counts.set(projectId, (counts.get(projectId) ?? 0) + 1);
		}
	}
	return counts;
}

function latestCommentByProjectId(rows: unknown) {
	const latest = new Map<string, string>();
	if (!Array.isArray(rows)) {
		return latest;
	}
	for (const row of rows) {
		const record = asRecord(row);
		const projectId = nullableString(record.project_id);
		const createdAt = nullableString(record.created_at);
		if (projectId && createdAt && (!latest.has(projectId) || createdAt > latest.get(projectId)!)) {
			latest.set(projectId, createdAt);
		}
	}
	return latest;
}

function asProjectArray(value: unknown) {
	return Array.isArray(value) ? value.map(normalizeProject) : [];
}

function normalizeProject(value: unknown): ProjectDetail {
	const payload = asRecord(value);
	const author = asRecord(payload.author);
	return {
		id: String(payload.id ?? ''),
		author_id: String(payload.author_id ?? ''),
		title: String(payload.title ?? 'Untitled'),
		one_liner: nullableString(payload.one_liner),
		problem: nullableString(payload.problem),
		dataset: nullableString(payload.dataset),
		process: nullableString(payload.process),
		insights: nullableString(payload.insights),
		tags: asStringArray(payload.tags),
		thumbnail_url: nullableString(payload.thumbnail_url),
		power_bi_url: nullableString(payload.power_bi_url),
		report_url: nullableString(payload.report_url),
		github_url: nullableString(payload.github_url),
		platform_key: normalizePlatformKey(payload.platform_key),
		project_type: String(payload.project_type ?? 'other') as ProjectCard['project_type'],
		status: String(payload.status ?? 'published') as ProjectCard['status'],
		embed_status: String(payload.embed_status ?? 'external_only') as ProjectCard['embed_status'],
		is_public: Boolean(payload.is_public ?? true),
		view_count: Number(payload.view_count ?? 0),
		created_at: String(payload.created_at ?? ''),
		updated_at: String(payload.updated_at ?? ''),
		author: {
			id: nullableString(author.id) ?? undefined,
			name: nullableString(author.name) ?? undefined,
			organization: nullableString(author.organization)
		},
		like_count: Number(payload.like_count ?? 0),
		comment_count: Number(payload.comment_count ?? 0),
		latest_comment_at: nullableString(payload.latest_comment_at)
	};
}

function normalizePlatformKey(value: unknown) {
	const platformKey = String(value ?? '').trim();
	if (['powerbi', 'tableau', 'datastudio', 'streamlit'].includes(platformKey)) {
		return platformKey as PlatformKey;
	}
	return null;
}

function asRecord(value: unknown): Record<string, unknown> {
	return value && typeof value === 'object' ? (value as Record<string, unknown>) : {};
}

function asStringArray(value: unknown) {
	if (!Array.isArray(value)) {
		return [];
	}
	return value.map((item) => String(item)).filter(Boolean);
}

function nullableString(value: unknown) {
	const text = String(value ?? '').trim();
	return text || null;
}
