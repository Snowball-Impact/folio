import { t as getSupabaseClient } from "./supabase2.js";
import { r as currentSession } from "./auth.js";
//#region lib/projectTags.ts
var EXCLUDED_HOME_TAGS = /* @__PURE__ */ new Set([
	"powerbi",
	"pbi",
	"reference",
	"references",
	"레퍼런스",
	"참고",
	"전체",
	"all"
]);
function normalizeHomeTag(value) {
	const tag = String(value ?? "").trim().replace(/^#+/, "");
	return tag && tag !== "전체" ? tag : "";
}
function comparableProjectTag(value) {
	return value.trim().replace(/^#+/, "").toLowerCase().replaceAll(" ", "");
}
function projectTagsInclude(tags, selectedTag) {
	const targetTag = comparableProjectTag(selectedTag);
	return !targetTag || tags.some((tag) => comparableProjectTag(tag) === targetTag);
}
function popularTagsFromTagLists(tagLists, limit) {
	return popularTagStatsFromTagLists(tagLists, limit).map((entry) => entry.label);
}
function popularTagStatsFromTagLists(tagLists, limit) {
	const counts = /* @__PURE__ */ new Map();
	for (const tags of tagLists) for (const tag of tags) {
		const label = tag.trim();
		const comparableTag = comparableProjectTag(label);
		if (!label || EXCLUDED_HOME_TAGS.has(comparableTag)) continue;
		const current = counts.get(comparableTag);
		counts.set(comparableTag, {
			label: current?.label ?? label,
			count: (current?.count ?? 0) + 1
		});
	}
	return [...counts.values()].sort((first, second) => second.count - first.count || first.label.localeCompare(second.label, "ko-KR")).slice(0, limit);
}
function normalizePopularHomeTags(tags, limit) {
	const seen = /* @__PURE__ */ new Set();
	const normalizedTags = [];
	for (const tag of tags) {
		const label = tag.trim();
		const comparableTag = comparableProjectTag(label);
		if (!label || EXCLUDED_HOME_TAGS.has(comparableTag) || seen.has(comparableTag)) continue;
		seen.add(comparableTag);
		normalizedTags.push(label);
		if (normalizedTags.length >= limit) break;
	}
	return normalizedTags;
}
//#endregion
//#region lib/projects.ts
var HOME_FILTER_FETCH_LIMIT = 500;
var HOME_RAIL_PROJECT_LIMIT = 6;
var HOME_TAG_LIMIT = 10;
var REFERENCE_FETCH_LIMIT = 500;
var REFERENCE_PLATFORM_RULES = {
	powerbi: {
		aliases: [
			"powerbi",
			"power bi",
			"pbi"
		],
		urlMarkers: ["app.powerbi.com", "powerbi.com"]
	},
	tableau: {
		aliases: ["tableau", "viz gallery"],
		urlMarkers: ["tableau.com", "public.tableau.com"]
	},
	datastudio: {
		aliases: [
			"looker studio",
			"data studio",
			"data studio gallery",
			"lookerstudio"
		],
		urlMarkers: ["datastudio.google.com", "lookerstudio.google.com"]
	},
	streamlit: {
		aliases: ["streamlit"],
		urlMarkers: [
			"streamlit.app",
			"streamlit.io/gallery",
			"share.streamlit.io"
		]
	}
};
var REFERENCE_PLATFORMS = {
	tableau: {
		key: "tableau",
		label: "Tableau",
		description: "Tableau Public과 Viz Gallery에서 수집한 인터랙티브 시각화 레퍼런스입니다."
	},
	powerbi: {
		key: "powerbi",
		label: "Power BI",
		description: "Power BI 공개 보고서와 대시보드 레퍼런스입니다."
	},
	datastudio: {
		key: "datastudio",
		label: "Data Studio",
		description: "Looker Studio/Data Studio Gallery에서 수집한 보고서 레퍼런스입니다."
	},
	streamlit: {
		key: "streamlit",
		label: "Streamlit",
		description: "Streamlit 공식 갤러리에서 수집한 앱 레퍼런스입니다."
	}
};
var emptyHomeSnapshot = {
	total_project_count: 0,
	popular_tags: [],
	popular_tag_counts: [],
	recent_projects: [],
	viewed_projects: [],
	liked_projects: []
};
async function loadHomeSnapshot(platformKey = "powerbi", filters = {}) {
	const supabase = getSupabaseClient();
	if (!supabase) return {
		snapshot: emptyHomeSnapshot,
		error: "Supabase 환경 변수가 설정되지 않았습니다."
	};
	const search = filters.search?.trim() ?? "";
	const selectedTag = normalizeHomeTag(filters.tag);
	if (search || selectedTag) return await loadFilteredHomeSnapshot(platformKey, search, selectedTag);
	const limit = HOME_RAIL_PROJECT_LIMIT;
	const { data, error } = await supabase.rpc("home_project_snapshot", {
		p_limit: limit,
		p_tag_limit: 40,
		p_like_sample_limit: 120,
		p_platform_key: platformKey
	});
	if (error) return {
		snapshot: emptyHomeSnapshot,
		error: "홈 프로젝트를 불러오지 못했습니다."
	};
	return {
		snapshot: await withHomeTagStats(normalizeHomeSnapshot(data), platformKey),
		error: ""
	};
}
async function loadFilteredHomeSnapshot(platformKey, search, selectedTag) {
	const supabase = getSupabaseClient();
	if (!supabase) return {
		snapshot: emptyHomeSnapshot,
		error: "Supabase 환경 변수가 설정되지 않았습니다."
	};
	const { data, error } = await supabase.from("projects").select(projectListColumns).eq("is_public", true).eq("status", "published").order("created_at", { ascending: false }).limit(HOME_FILTER_FETCH_LIMIT);
	if (error) return {
		snapshot: emptyHomeSnapshot,
		error: "홈 프로젝트를 불러오지 못했습니다."
	};
	const projects = await attachPublicProjectMetadata((Array.isArray(data) ? data : []).map(normalizeProject).filter((project) => !platformKey || referencePlatformForProject(project) === platformKey));
	const filteredProjects = projects.filter((project) => projectMatchesSearch(project, search) && projectMatchesTag(project, selectedTag));
	const viewedProjects = [...filteredProjects].sort((first, second) => second.view_count - first.view_count || compareDateDesc(first, second));
	const likedProjects = [...filteredProjects].sort((first, second) => second.like_count - first.like_count || compareDateDesc(first, second));
	return {
		snapshot: {
			total_project_count: projects.length,
			popular_tags: popularTagsFromProjects(projects),
			popular_tag_counts: popularTagStatsFromProjects(projects),
			recent_projects: filteredProjects.slice(0, HOME_RAIL_PROJECT_LIMIT),
			viewed_projects: viewedProjects.slice(0, HOME_RAIL_PROJECT_LIMIT),
			liked_projects: likedProjects.slice(0, HOME_RAIL_PROJECT_LIMIT)
		},
		error: ""
	};
}
async function loadProjectDetail(projectId) {
	const supabase = getSupabaseClient();
	if (!supabase) return {
		project: null,
		error: "Supabase 환경 변수가 설정되지 않았습니다."
	};
	const { data, error } = await supabase.rpc("project_detail_snapshot", { p_project_id: projectId });
	if (!error && data) {
		const project = normalizeProject(data);
		if (project && project.status !== "deleted") return {
			project,
			error: ""
		};
	}
	await currentSession();
	const { data: row, error: fallbackError } = await supabase.from("projects").select(projectListColumns).eq("id", projectId).neq("status", "deleted").maybeSingle();
	if (fallbackError || !row) return {
		project: null,
		error: error ? "프로젝트를 불러오지 못했습니다." : "프로젝트를 찾을 수 없습니다."
	};
	const [project] = await attachPublicProjectMetadata([normalizeProject(row)]);
	return project ? {
		project,
		error: ""
	} : {
		project: null,
		error: "프로젝트를 찾을 수 없습니다."
	};
}
async function loadProjectEmbedState(projectId) {
	const supabase = getSupabaseClient();
	if (!supabase) return {
		state: null,
		error: "Supabase 환경 변수가 설정되지 않았습니다."
	};
	const { data, error } = await supabase.from("projects").select("status,project_type,is_public").eq("id", projectId).neq("status", "deleted").maybeSingle();
	if (error) return {
		state: null,
		error: "프로젝트를 불러오지 못했습니다."
	};
	return {
		state: data ? {
			status: String(data.status ?? ""),
			project_type: String(data.project_type ?? ""),
			is_public: Boolean(data.is_public)
		} : null,
		error: ""
	};
}
async function loadReferenceProjects(platformKey = "powerbi", sort = "latest") {
	const supabase = getSupabaseClient();
	const platform = REFERENCE_PLATFORMS[platformKey] ?? REFERENCE_PLATFORMS.powerbi;
	if (!supabase) return {
		platform,
		sort,
		projects: [],
		error: "Supabase 환경 변수가 설정되지 않았습니다."
	};
	const { data, error } = await supabase.from("projects").select(projectListColumns).eq("is_public", true).eq("status", "published").order("created_at", { ascending: false }).limit(REFERENCE_FETCH_LIMIT);
	if (error) return {
		platform,
		sort,
		projects: [],
		error: "레퍼런스를 불러오지 못했습니다."
	};
	const projects = await attachPublicProjectMetadata((Array.isArray(data) ? data : []).map(normalizeProject).filter((project) => referencePlatformForProject(project) === platformKey));
	sortReferenceProjects(projects, sort);
	return {
		platform,
		sort,
		projects,
		error: ""
	};
}
async function recordProjectView(projectId, anonymousViewerId) {
	const supabase = getSupabaseClient();
	if (!supabase) return false;
	const { data, error } = await supabase.rpc("increment_project_view_count", {
		project_id_input: projectId,
		anonymous_viewer_id_input: anonymousViewerId
	});
	return !error && data === true;
}
async function loadMyProject(projectId) {
	const supabase = getSupabaseClient();
	const session = await currentSession();
	if (!supabase || !session) return {
		project: null,
		error: "로그인 후 프로젝트를 수정할 수 있습니다."
	};
	const { data, error } = await supabase.from("projects").select(projectListColumns).eq("id", projectId).eq("author_id", session.user.id).maybeSingle();
	if (error) return {
		project: null,
		error: "프로젝트를 불러오지 못했습니다. 잠시 후 다시 시도하세요."
	};
	const project = data ? normalizeProject(data) : null;
	if (!project || project.status === "deleted") return {
		project: null,
		error: "수정할 프로젝트를 찾을 수 없습니다."
	};
	return {
		project,
		error: ""
	};
}
async function listMyProjects() {
	const supabase = getSupabaseClient();
	const session = await currentSession();
	if (!supabase || !session) return {
		projects: [],
		error: "로그인 후 내 프로젝트를 확인할 수 있습니다."
	};
	const { data, error } = await supabase.from("projects").select(projectListColumns).eq("author_id", session.user.id).order("created_at", { ascending: false });
	if (error) return {
		projects: [],
		error: "내 프로젝트를 불러오지 못했습니다. 잠시 후 다시 시도하세요."
	};
	return {
		projects: await attachUnreadCommentStatus(await attachPublicProjectMetadata((Array.isArray(data) ? data : []).map(normalizeProject).filter((project) => project.status !== "deleted")), session.user.id),
		error: ""
	};
}
var projectListColumns = [
	"id",
	"author_id",
	"title",
	"one_liner",
	"problem",
	"dataset",
	"process",
	"insights",
	"tags",
	"thumbnail_url",
	"thumbnail_mode",
	"power_bi_url",
	"report_url",
	"github_url",
	"platform_key",
	"project_type",
	"status",
	"embed_status",
	"is_public",
	"view_count",
	"created_at",
	"updated_at"
].join(",");
function normalizeHomeSnapshot(value) {
	const payload = asRecord(value);
	return {
		total_project_count: Number(payload.total_project_count ?? 0),
		popular_tags: normalizeHomePopularTags(asStringArray(payload.popular_tags)),
		popular_tag_counts: [],
		recent_projects: asProjectArray(payload.recent_projects),
		viewed_projects: asProjectArray(payload.viewed_projects),
		liked_projects: asProjectArray(payload.liked_projects)
	};
}
async function withHomeTagStats(snapshot, platformKey) {
	const supabase = getSupabaseClient();
	if (!supabase) return snapshot;
	const { data, error } = await supabase.from("projects").select(projectListColumns).eq("is_public", true).eq("status", "published").order("created_at", { ascending: false }).limit(HOME_FILTER_FETCH_LIMIT);
	if (error) return {
		...snapshot,
		popular_tag_counts: snapshot.popular_tags.map((label) => ({
			label,
			count: 0
		}))
	};
	const popularTagCounts = popularTagStatsFromProjects((Array.isArray(data) ? data : []).map(normalizeProject).filter((project) => !platformKey || referencePlatformForProject(project) === platformKey));
	return {
		...snapshot,
		popular_tags: popularTagCounts.map((tag) => tag.label),
		popular_tag_counts: popularTagCounts
	};
}
async function attachUnreadCommentStatus(projects, userId) {
	const supabase = getSupabaseClient();
	const projectIds = projects.map((project) => project.id).filter(Boolean);
	if (!supabase || projects.length === 0 || projectIds.length === 0 || !userId) return projects;
	try {
		const [commentsResult, readsResult] = await Promise.all([supabase.from("comments").select("project_id,author_id,created_at").in("project_id", projectIds).neq("author_id", userId), supabase.from("project_comment_reads").select("project_id,last_read_at").eq("user_id", userId).in("project_id", projectIds)]);
		if (commentsResult.error || readsResult.error) throw commentsResult.error ?? readsResult.error;
		const latestExternalComments = latestCommentByProjectId(commentsResult.data);
		const reads = readsResult.data;
		const readsByProject = new Map((Array.isArray(reads) ? reads : []).map((read) => asRecord(read)).map((read) => [nullableString(read.project_id), nullableString(read.last_read_at)]).filter((entry) => Boolean(entry[0])));
		return projects.map((project) => {
			const latestCommentAt = latestExternalComments.get(project.id);
			const lastReadAt = readsByProject.get(project.id);
			const hasUnreadComments = Boolean(latestCommentAt && (!lastReadAt || Date.parse(latestCommentAt) > Date.parse(lastReadAt)));
			return {
				...project,
				has_unread_comments: hasUnreadComments
			};
		});
	} catch (error) {
		console.warn("Failed to load unread comment state", error);
		return projects;
	}
}
async function attachPublicProjectMetadata(projects) {
	const supabase = getSupabaseClient();
	if (!supabase || projects.length === 0) return projects;
	const authorIds = [...new Set(projects.map((project) => project.author_id).filter(Boolean))];
	const projectIds = projects.map((project) => project.id).filter(Boolean);
	const [{ data: profiles }, { data: likes }, { data: comments }] = await Promise.all([
		authorIds.length ? supabase.from("public_profiles").select("id,name,organization,avatar_url").in("id", authorIds) : Promise.resolve({ data: [] }),
		projectIds.length ? supabase.from("likes").select("project_id").in("project_id", projectIds) : Promise.resolve({ data: [] }),
		projectIds.length ? supabase.from("comments").select("project_id,created_at").in("project_id", projectIds) : Promise.resolve({ data: [] })
	]);
	const profileById = new Map((Array.isArray(profiles) ? profiles : []).map((profile) => {
		const record = asRecord(profile);
		return [String(record.id), record];
	}));
	const likeCounts = countByProjectId(likes, "project_id");
	const commentCounts = countByProjectId(comments, "project_id");
	const latestComments = latestCommentByProjectId(comments);
	return projects.map((project) => {
		const author = profileById.get(project.author_id);
		return {
			...project,
			author: author ? {
				id: nullableString(author.id) ?? void 0,
				name: nullableString(author.name) ?? void 0,
				organization: nullableString(author.organization),
				avatar_url: nullableString(author.avatar_url)
			} : project.author,
			like_count: likeCounts.get(project.id) ?? 0,
			comment_count: commentCounts.get(project.id) ?? 0,
			latest_comment_at: latestComments.get(project.id) ?? null
		};
	});
}
function projectMatchesTag(project, selectedTag) {
	return projectTagsInclude(project.tags, selectedTag);
}
function projectMatchesSearch(project, search) {
	const term = search.trim().toLowerCase();
	if (!term) return true;
	const author = project.author ?? {};
	return [
		project.title,
		project.one_liner,
		project.problem,
		project.dataset,
		project.process,
		project.insights,
		project.tags.join(" "),
		author.name,
		author.organization,
		project.created_at
	].some((field) => String(field ?? "").toLowerCase().includes(term));
}
function popularTagsFromProjects(projects, limit = HOME_TAG_LIMIT) {
	return popularTagsFromTagLists(projects.map((project) => project.tags), limit);
}
function popularTagStatsFromProjects(projects, limit = HOME_TAG_LIMIT) {
	return popularTagStatsFromTagLists(projects.map((project) => project.tags), limit);
}
function normalizeHomePopularTags(tags, limit = HOME_TAG_LIMIT) {
	return normalizePopularHomeTags(tags, limit);
}
function sortReferenceProjects(projects, sort) {
	if (sort === "likes") {
		projects.sort((first, second) => second.like_count - first.like_count || compareDateDesc(first, second));
		return;
	}
	if (sort === "views") {
		projects.sort((first, second) => second.view_count - first.view_count || compareDateDesc(first, second));
		return;
	}
	projects.sort(compareDateDesc);
}
function compareDateDesc(first, second) {
	return Date.parse(second.created_at || "") - Date.parse(first.created_at || "");
}
function referencePlatformForProject(project) {
	if (project.platform_key && project.platform_key in REFERENCE_PLATFORM_RULES) return project.platform_key;
	const tags = new Set(project.tags.map((tag) => tag.trim().toLowerCase()).filter(Boolean));
	const urlText = [
		project.power_bi_url,
		project.report_url,
		project.github_url,
		project.thumbnail_url
	].map((value) => value?.toLowerCase() ?? "").join(" ");
	for (const platformKey of Object.keys(REFERENCE_PLATFORM_RULES)) {
		const rules = REFERENCE_PLATFORM_RULES[platformKey];
		if (rules.aliases.some((alias) => tags.has(alias))) return platformKey;
		if (rules.urlMarkers.some((marker) => urlText.includes(marker))) return platformKey;
	}
	return null;
}
function countByProjectId(rows, key) {
	const counts = /* @__PURE__ */ new Map();
	if (!Array.isArray(rows)) return counts;
	for (const row of rows) {
		const projectId = nullableString(asRecord(row)[key]);
		if (projectId) counts.set(projectId, (counts.get(projectId) ?? 0) + 1);
	}
	return counts;
}
function latestCommentByProjectId(rows) {
	const latest = /* @__PURE__ */ new Map();
	if (!Array.isArray(rows)) return latest;
	for (const row of rows) {
		const record = asRecord(row);
		const projectId = nullableString(record.project_id);
		const createdAt = nullableString(record.created_at);
		if (projectId && createdAt && (!latest.has(projectId) || Date.parse(createdAt) > Date.parse(latest.get(projectId)))) latest.set(projectId, createdAt);
	}
	return latest;
}
function asProjectArray(value) {
	return Array.isArray(value) ? value.map(normalizeProject) : [];
}
function normalizeProject(value) {
	const payload = asRecord(value);
	const author = asRecord(payload.author);
	return {
		id: String(payload.id ?? ""),
		author_id: String(payload.author_id ?? ""),
		title: String(payload.title ?? "Untitled"),
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
		project_type: String(payload.project_type ?? "other"),
		status: String(payload.status ?? "published"),
		embed_status: String(payload.embed_status ?? "external_only"),
		is_public: Boolean(payload.is_public ?? true),
		view_count: Number(payload.view_count ?? 0),
		created_at: String(payload.created_at ?? ""),
		updated_at: String(payload.updated_at ?? ""),
		author: {
			id: nullableString(author.id) ?? void 0,
			name: nullableString(author.name) ?? void 0,
			organization: nullableString(author.organization)
		},
		like_count: Number(payload.like_count ?? 0),
		comment_count: Number(payload.comment_count ?? 0),
		latest_comment_at: nullableString(payload.latest_comment_at),
		has_unread_comments: Boolean(payload.has_unread_comments)
	};
}
function normalizePlatformKey(value) {
	const platformKey = String(value ?? "").trim();
	if ([
		"powerbi",
		"tableau",
		"datastudio",
		"streamlit"
	].includes(platformKey)) return platformKey;
	return null;
}
function normalizeThumbnailMode(value) {
	const thumbnailMode = String(value ?? "").trim();
	if ([
		"auto_cover",
		"manual_url",
		"capture",
		"upload"
	].includes(thumbnailMode)) return thumbnailMode;
	return "auto_cover";
}
function asRecord(value) {
	return value && typeof value === "object" ? value : {};
}
function asStringArray(value) {
	if (!Array.isArray(value)) return [];
	return value.map((item) => String(item)).filter(Boolean);
}
function nullableString(value) {
	return String(value ?? "").trim() || null;
}
//#endregion
export { loadProjectDetail as a, recordProjectView as c, loadMyProject as i, listMyProjects as n, loadProjectEmbedState as o, loadHomeSnapshot as r, loadReferenceProjects as s, REFERENCE_PLATFORMS as t };
