import { getSupabaseClient } from '$lib/supabase';
import { currentSession } from '$lib/auth';
import { buildProjectPayload, normalizePowerBIEmbedUrl, validateProjectInput } from '$lib/projectInput';
import { normalizeHomeTag, normalizePopularHomeTags, popularTagsFromTagLists, projectTagsInclude } from '$lib/projectTags';
export { normalizePowerBIEmbedUrl } from '$lib/projectInput';
import type {
	HomeSnapshot,
	PlatformKey,
	ProjectCard,
	ProjectDetail,
	ProjectSubmitInput,
	ReferenceProjectsResult,
	ReferenceSort
} from '$lib/types';
export type { ProjectSubmitInput } from '$lib/types';

const HOME_LIKED_PROJECT_SAMPLE_MULTIPLIER = 20;
const HOME_FILTER_FETCH_LIMIT = 500;
const HOME_RAIL_PROJECT_LIMIT = 6;
const HOME_TAG_LIMIT = 10;
const REFERENCE_FETCH_LIMIT = 500;
const REFERENCE_PLATFORM_RULES: Record<PlatformKey, { aliases: string[]; urlMarkers: string[] }> = {
	powerbi: {
		aliases: ['powerbi', 'power bi', 'pbi'],
		urlMarkers: ['app.powerbi.com', 'powerbi.com']
	},
	tableau: {
		aliases: ['tableau', 'viz gallery'],
		urlMarkers: ['tableau.com', 'public.tableau.com']
	},
	datastudio: {
		aliases: ['looker studio', 'data studio', 'data studio gallery', 'lookerstudio'],
		urlMarkers: ['datastudio.google.com', 'lookerstudio.google.com']
	},
	streamlit: {
		aliases: ['streamlit'],
		urlMarkers: ['streamlit.app', 'streamlit.io/gallery', 'share.streamlit.io']
	}
};
export const REFERENCE_PLATFORMS = {
	tableau: {
		key: 'tableau',
		label: 'Tableau',
		description: 'Tableau Public과 Viz Gallery에서 수집한 인터랙티브 시각화 레퍼런스입니다.'
	},
	powerbi: {
		key: 'powerbi',
		label: 'Power BI',
		description: 'Power BI 공개 보고서와 대시보드 레퍼런스입니다.'
	},
	datastudio: {
		key: 'datastudio',
		label: 'Data Studio',
		description: 'Looker Studio/Data Studio Gallery에서 수집한 보고서 레퍼런스입니다.'
	},
	streamlit: {
		key: 'streamlit',
		label: 'Streamlit',
		description: 'Streamlit 공식 갤러리에서 수집한 앱 레퍼런스입니다.'
	}
} satisfies Record<PlatformKey, { key: PlatformKey; label: string; description: string }>;

const emptyHomeSnapshot: HomeSnapshot = {
	total_project_count: 0,
	popular_tags: [],
	recent_projects: [],
	viewed_projects: [],
	liked_projects: []
};

export async function loadHomeSnapshot(
	platformKey: PlatformKey | null = 'powerbi',
	filters: { search?: string; tag?: string } = {}
) {
	const supabase = getSupabaseClient();
	if (!supabase) {
		return {
			snapshot: emptyHomeSnapshot,
			error: 'Supabase 환경 변수가 설정되지 않았습니다.'
		};
	}

	const search = filters.search?.trim() ?? '';
	const selectedTag = normalizeHomeTag(filters.tag);
	if (search || selectedTag) {
		return await loadFilteredHomeSnapshot(platformKey, search, selectedTag);
	}

	const limit = HOME_RAIL_PROJECT_LIMIT;
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

async function loadFilteredHomeSnapshot(platformKey: PlatformKey | null, search: string, selectedTag: string) {
	const supabase = getSupabaseClient();
	if (!supabase) {
		return {
			snapshot: emptyHomeSnapshot,
			error: 'Supabase 환경 변수가 설정되지 않았습니다.'
		};
	}

	let query = supabase
		.from('projects')
		.select(projectListColumns)
		.eq('is_public', true)
		.eq('status', 'published')
		.order('created_at', { ascending: false });

	if (selectedTag && !search) {
		query = query.contains('tags', [selectedTag]);
	}

	const { data, error } = await query.limit(HOME_FILTER_FETCH_LIMIT);

	if (error) {
		return {
			snapshot: emptyHomeSnapshot,
			error: '홈 프로젝트를 불러오지 못했습니다.'
		};
	}

	const platformProjects = (Array.isArray(data) ? data : [])
		.map(normalizeProject)
		.filter((project) => !platformKey || referencePlatformForProject(project) === platformKey);
	const projects = await attachPublicProjectMetadata(platformProjects);
	const filteredProjects = projects.filter(
		(project) => projectMatchesSearch(project, search) && projectMatchesTag(project, selectedTag)
	);
	const viewedProjects = [...filteredProjects].sort(
		(first, second) => second.view_count - first.view_count || compareDateDesc(first, second)
	);
	const likedProjects = [...filteredProjects].sort(
		(first, second) => second.like_count - first.like_count || compareDateDesc(first, second)
	);

	return {
		snapshot: {
			total_project_count: projects.length,
			popular_tags: popularTagsFromProjects(projects),
			recent_projects: filteredProjects.slice(0, HOME_RAIL_PROJECT_LIMIT),
			viewed_projects: viewedProjects.slice(0, HOME_RAIL_PROJECT_LIMIT),
			liked_projects: likedProjects.slice(0, HOME_RAIL_PROJECT_LIMIT)
		},
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

	if (!error && data) {
		const project = normalizeProject(data);
		if (project && project.status !== 'deleted') {
			return { project, error: '' };
		}
	}

	// Match the Streamlit service fallback when the remote detail RPC is stale or unavailable.
	// Resolve the browser session first so the owner-read RLS policy can expose a private project.
	await currentSession();
	const { data: row, error: fallbackError } = await supabase
		.from('projects')
		.select(projectListColumns)
		.eq('id', projectId)
		.neq('status', 'deleted')
		.maybeSingle();

	if (fallbackError || !row) {
		return {
			project: null,
			error: error ? '프로젝트를 불러오지 못했습니다.' : '프로젝트를 찾을 수 없습니다.'
		};
	}

	const [project] = await attachPublicProjectMetadata([normalizeProject(row)]);
	return project ? { project, error: '' } : { project: null, error: '프로젝트를 찾을 수 없습니다.' };
}

export async function loadProjectEmbedState(projectId: string) {
	const supabase = getSupabaseClient();
	if (!supabase) {
		return {
			state: null,
			error: 'Supabase 환경 변수가 설정되지 않았습니다.'
		};
	}

	const { data, error } = await supabase
		.from('projects')
		.select('status,project_type,is_public')
		.eq('id', projectId)
		.neq('status', 'deleted')
		.maybeSingle();

	if (error) {
		return { state: null, error: '프로젝트를 불러오지 못했습니다.' };
	}

	return {
		state: data
			? {
					status: String(data.status ?? ''),
					project_type: String(data.project_type ?? ''),
					is_public: Boolean(data.is_public)
				}
			: null,
		error: ''
	};
}

export async function loadReferenceProjects(
	platformKey: PlatformKey = 'powerbi',
	sort: ReferenceSort = 'latest'
): Promise<ReferenceProjectsResult> {
	const supabase = getSupabaseClient();
	const platform = REFERENCE_PLATFORMS[platformKey] ?? REFERENCE_PLATFORMS.powerbi;
	if (!supabase) {
		return {
			platform,
			sort,
			projects: [],
			error: 'Supabase 환경 변수가 설정되지 않았습니다.'
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

	const payload = {
		author_id: session.user.id,
		...buildProjectPayload(input)
	};

	const { data, error } = await supabase.from('projects').insert(payload).select('id').single();
	if (error) {
		return { ok: false, message: '프로젝트 등록에 실패했습니다. 잠시 후 다시 시도하세요.', projectId: null };
	}

	return { ok: true, message: '프로젝트가 등록되었습니다.', projectId: String(data.id ?? '') };
}

export async function loadMyProject(projectId: string) {
	const supabase = getSupabaseClient();
	const session = await currentSession();
	if (!supabase || !session) {
		return {
			project: null,
			error: '로그인 후 프로젝트를 수정할 수 있습니다.'
		};
	}

	const { data, error } = await supabase
		.from('projects')
		.select(projectListColumns)
		.eq('id', projectId)
		.eq('author_id', session.user.id)
		.maybeSingle();
	if (error) {
		return {
			project: null,
			error: '프로젝트를 불러오지 못했습니다. 잠시 후 다시 시도하세요.'
		};
	}

	const project = data ? normalizeProject(data) : null;
	if (!project || project.status === 'deleted') {
		return {
			project: null,
			error: '수정할 프로젝트를 찾을 수 없습니다.'
		};
	}

	return {
		project,
		error: ''
	};
}

export async function updateProject(projectId: string, input: ProjectSubmitInput) {
	const supabase = getSupabaseClient();
	const session = await currentSession();
	if (!supabase || !session) {
		return { ok: false, message: '로그인 후 프로젝트를 수정할 수 있습니다.', projectId: null };
	}

	const validationError = validateProjectInput(input);
	if (validationError) {
		return { ok: false, message: validationError, projectId: null };
	}

	const { error } = await supabase
		.from('projects')
		.update(buildProjectPayload(input))
		.eq('id', projectId)
		.eq('author_id', session.user.id);
	if (error) {
		return { ok: false, message: '프로젝트 수정에 실패했습니다. 잠시 후 다시 시도하세요.', projectId: null };
	}

	return { ok: true, message: '프로젝트가 수정되었습니다.', projectId };
}

export async function listMyProjects() {
	const supabase = getSupabaseClient();
	const session = await currentSession();
	if (!supabase || !session) {
		return {
			projects: [],
			error: '로그인 후 내 프로젝트를 확인할 수 있습니다.'
		};
	}

	const { data, error } = await supabase
		.from('projects')
		.select(projectListColumns)
		.eq('author_id', session.user.id)
		.order('created_at', { ascending: false });

	if (error) {
		return {
			projects: [],
			error: '내 프로젝트를 불러오지 못했습니다. 잠시 후 다시 시도하세요.'
		};
	}

	const projects = (Array.isArray(data) ? data : [])
		.map(normalizeProject)
		.filter((project) => project.status !== 'deleted');
	const projectsWithMetadata = await attachPublicProjectMetadata(projects);
	return {
		projects: await attachUnreadCommentStatus(projectsWithMetadata, session.user.id),
		error: ''
	};
}

export async function deleteProject(projectId: string) {
	const supabase = getSupabaseClient();
	const session = await currentSession();
	if (!supabase || !session) {
		return { ok: false, message: '로그인 후 프로젝트를 삭제할 수 있습니다.' };
	}

	const { error } = await supabase
		.from('projects')
		.update({
			status: 'deleted',
			deleted_at: new Date().toISOString(),
			is_public: false
		})
		.eq('id', projectId)
		.eq('author_id', session.user.id);

	if (error) {
		return { ok: false, message: '프로젝트 삭제에 실패했습니다. 잠시 후 다시 시도하세요.' };
	}

	return { ok: true, message: '프로젝트가 삭제되었습니다.' };
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
	'thumbnail_mode',
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
		popular_tags: normalizeHomePopularTags(asStringArray(payload.popular_tags)),
		recent_projects: asProjectArray(payload.recent_projects),
		viewed_projects: asProjectArray(payload.viewed_projects),
		liked_projects: asProjectArray(payload.liked_projects)
	};
}


async function attachUnreadCommentStatus(projects: ProjectCard[], userId: string) {
	const supabase = getSupabaseClient();
	const projectIds = projects.map((project) => project.id).filter(Boolean);
	if (!supabase || projects.length === 0 || projectIds.length === 0 || !userId) {
		return projects;
	}

	try {
		const [commentsResult, readsResult] = await Promise.all([
			supabase.from('comments').select('project_id,author_id,created_at').in('project_id', projectIds).neq('author_id', userId),
			supabase.from('project_comment_reads').select('project_id,last_read_at').eq('user_id', userId).in('project_id', projectIds)
		]);
		if (commentsResult.error || readsResult.error) {
			throw commentsResult.error ?? readsResult.error;
		}
		const latestExternalComments = latestCommentByProjectId(commentsResult.data);
		const reads = readsResult.data;
		const readsByProject = new Map(
			(Array.isArray(reads) ? reads : [])
				.map((read) => asRecord(read))
				.map((read) => [nullableString(read.project_id), nullableString(read.last_read_at)] as const)
				.filter((entry): entry is [string, string | null] => Boolean(entry[0]))
		);

		return projects.map((project) => {
			const latestCommentAt = latestExternalComments.get(project.id);
			const lastReadAt = readsByProject.get(project.id);
			const hasUnreadComments = Boolean(
				latestCommentAt && (!lastReadAt || Date.parse(latestCommentAt) > Date.parse(lastReadAt))
			);
			return { ...project, has_unread_comments: hasUnreadComments };
		});
	} catch (error) {
		console.warn('Failed to load unread comment state', error);
		return projects;
	}
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

function projectMatchesTag(project: ProjectCard, selectedTag: string) {
	return projectTagsInclude(project.tags, selectedTag);
}

function projectMatchesSearch(project: ProjectCard, search: string) {
	const term = search.trim().toLowerCase();
	if (!term) {
		return true;
	}
	const author = project.author ?? {};
	const fields = [
		project.title,
		project.one_liner,
		project.problem,
		project.dataset,
		project.process,
		project.insights,
		project.tags.join(' '),
		author.name,
		author.organization,
		project.created_at
	];
	return fields.some((field) => String(field ?? '').toLowerCase().includes(term));
}

function popularTagsFromProjects(projects: ProjectCard[], limit = HOME_TAG_LIMIT) {
	return popularTagsFromTagLists(projects.map((project) => project.tags), limit);
}

function normalizeHomePopularTags(tags: string[], limit = HOME_TAG_LIMIT) {
	return normalizePopularHomeTags(tags, limit);
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

function referencePlatformForProject(project: ProjectCard): PlatformKey | null {
	if (project.platform_key && project.platform_key in REFERENCE_PLATFORM_RULES) {
		return project.platform_key;
	}

	const tags = new Set(project.tags.map((tag) => tag.trim().toLowerCase()).filter(Boolean));
	const urlText = [project.power_bi_url, project.report_url, project.github_url, project.thumbnail_url]
		.map((value) => value?.toLowerCase() ?? '')
		.join(' ');

	for (const platformKey of Object.keys(REFERENCE_PLATFORM_RULES) as PlatformKey[]) {
		const rules = REFERENCE_PLATFORM_RULES[platformKey];
		if (rules.aliases.some((alias) => tags.has(alias))) {
			return platformKey;
		}
		if (rules.urlMarkers.some((marker) => urlText.includes(marker))) {
			return platformKey;
		}
	}

	return null;
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
		if (
			projectId &&
			createdAt &&
			(!latest.has(projectId) || Date.parse(createdAt) > Date.parse(latest.get(projectId)!))
		) {
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
		thumbnail_mode: normalizeThumbnailMode(payload.thumbnail_mode),
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
		latest_comment_at: nullableString(payload.latest_comment_at),
		has_unread_comments: Boolean(payload.has_unread_comments)
	};
}

function normalizePlatformKey(value: unknown) {
	const platformKey = String(value ?? '').trim();
	if (['powerbi', 'tableau', 'datastudio', 'streamlit'].includes(platformKey)) {
		return platformKey as PlatformKey;
	}
	return null;
}

function normalizeThumbnailMode(value: unknown) {
	const thumbnailMode = String(value ?? '').trim();
	if (['auto_cover', 'manual_url', 'capture', 'upload'].includes(thumbnailMode)) {
		return thumbnailMode as ProjectCard['thumbnail_mode'];
	}
	return 'auto_cover';
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
