export type ThumbnailMode = 'auto_cover' | 'manual_url' | 'capture' | 'upload';

export type ProjectType =
	| 'powerbi'
	| 'tableau'
	| 'looker'
	| 'streamlit'
	| 'notebook'
	| 'html_report'
	| 'markdown_report'
	| 'web'
	| 'other';

export type ProjectStatus = 'processing' | 'published' | 'failed' | 'deleted';

export type EmbedStatus = 'supported' | 'external_only' | 'failed';

export type PlatformKey = 'powerbi' | 'tableau' | 'datastudio' | 'streamlit';

export type PublicAuthor = {
	id?: string;
	name?: string;
	organization?: string | null;
	avatar_url?: string | null;
};

export type ProjectCard = {
	id: string;
	author_id: string;
	title: string;
	one_liner: string | null;
	problem: string | null;
	dataset: string | null;
	process: string | null;
	insights: string | null;
	tags: string[];
	thumbnail_url: string | null;
	thumbnail_mode: ThumbnailMode;
	power_bi_url: string | null;
	report_url: string | null;
	github_url: string | null;
	platform_key: PlatformKey | null;
	project_type: ProjectType;
	status: ProjectStatus;
	embed_status: EmbedStatus;
	is_public: boolean;
	view_count: number;
	created_at: string;
	updated_at: string;
	author: PublicAuthor;
	like_count: number;
	comment_count: number;
	latest_comment_at?: string | null;
	has_unread_comments?: boolean;
};

export type HomeSnapshot = {
	total_project_count: number;
	popular_tags: string[];
	recent_projects: ProjectCard[];
	viewed_projects: ProjectCard[];
	liked_projects: ProjectCard[];
};

export type ProjectDetail = ProjectCard;

export type ReferenceSort = 'latest' | 'likes' | 'views';

export type ReferencePlatform = {
	key: PlatformKey;
	label: string;
	description: string;
};

export type ReferenceProjectsResult = {
	platform: ReferencePlatform;
	sort: ReferenceSort;
	projects: ProjectCard[];
	error: string;
};

export type PowerBIHubTopic = 'news' | 'learning' | 'community' | 'certifications';

export type PowerBIContentLink = {
	title: string;
	summary: string;
	url: string;
	source: string;
	date: string;
	topic: string;
	image_url: string | null;
};

export type PowerBINewsItem = {
	label: string;
	title: string;
	date: string;
	source_url: string;
	bullets: string[];
	video: PowerBIContentLink | null;
};

export type PowerBILearningGroup = {
	category: string;
	programs: PowerBIContentLink[];
	videos: PowerBIContentLink[];
};

export type PowerBIHubContent = {
	topic: PowerBIHubTopic;
	desktop: PowerBIContentLink | null;
	news: PowerBINewsItem[];
	learning: PowerBILearningGroup[];
	community: PowerBIContentLink[];
	certifications: PowerBIContentLink[];
	counts: Record<PowerBIHubTopic, number>;
};

export type PowerBIEmbedConfig = {
	report_id: string;
	dataset_id: string;
	embed_url: string;
	embed_token: string;
	token_expiration: string | null;
};

export type ProjectCommentAuthor = {
	id?: string;
	name?: string;
};

export type ProjectComment = {
	id: string;
	project_id: string;
	author_id: string;
	parent_id: string | null;
	body: string;
	depth: 0 | 1;
	is_deleted: boolean;
	created_at: string;
	author: ProjectCommentAuthor;
	children: ProjectComment[];
};
