import { getSupabaseClient } from '$lib/supabase';
import type { HomeSnapshot, PlatformKey, ProjectCard, ProjectDetail } from '$lib/types';

const HOME_LIKED_PROJECT_SAMPLE_MULTIPLIER = 20;

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
