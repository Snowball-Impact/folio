import { redirect } from '@sveltejs/kit';
import { loadHomeSnapshot } from '$lib/projects';

export async function load({ url }) {
	redirectLegacyStreamlitUrl(url);
	const search = url.searchParams.get('q')?.trim() ?? '';
	const tag = normalizeTag(url.searchParams.get('tag'));
	return {
		...(await loadHomeSnapshot('powerbi', { search, tag })),
		filters: { search, tag }
	};
}

function redirectLegacyStreamlitUrl(url: URL) {
	const page = normalizePage(url.searchParams.get('page'));
	if (!page) {
		return;
	}

	const projectId = url.searchParams.get('project_id')?.trim();
	const editProjectId = url.searchParams.get('edit_project')?.trim();
	const topic = normalizeTopic(url.searchParams.get('topic'));
	const policyType = url.searchParams.get('type') === 'terms' ? 'terms' : 'privacy';
	const referencePlatform = normalizeReferencePlatform(url.searchParams.get('platform'));
	const referenceSort = normalizeReferenceSort(url.searchParams.get('sort'));

	if (projectId) {
		const fromReference = page === 'reference';
		const target = fromReference
			? `/projects/${encodeURIComponent(projectId)}?from=references&platform=${referencePlatform}`
			: `/projects/${encodeURIComponent(projectId)}`;
		throw redirect(301, target);
	}

	if (editProjectId && (page === 'my page' || page === 'my portfolio' || page === 'profile')) {
		throw redirect(301, `/projects/${encodeURIComponent(editProjectId)}/edit`);
	}

	switch (page) {
		case 'home':
			throw redirect(301, homeRedirectTarget(url));
		case 'reference':
			throw redirect(301, referenceRedirectTarget(referencePlatform, referenceSort));
		case 'power bi':
			throw redirect(301, topic === 'news' ? '/powerbi' : `/powerbi?topic=${topic}`);
		case 'login':
			throw redirect(301, '/login');
		case 'sign up':
		case 'signup':
			throw redirect(301, '/signup');
		case 'submit':
			throw redirect(301, '/submit');
		case 'my page':
		case 'my portfolio':
		case 'profile':
			throw redirect(301, '/my');
		case 'notifications':
			throw redirect(301, '/notifications');
		case 'about':
			throw redirect(301, '/about');
		case 'policy':
			throw redirect(301, `/policy/${policyType}`);
	}
}

function normalizePage(value: string | null) {
	return String(value ?? '').trim().replace(/\+/g, ' ').replace(/\s+/g, ' ').toLowerCase();
}

function normalizeReferencePlatform(value: string | null) {
	const platform = String(value ?? '').trim().toLowerCase();
	if (platform === 'tableau' || platform === 'datastudio' || platform === 'streamlit') {
		return platform;
	}
	return 'powerbi';
}

function normalizeReferenceSort(value: string | null) {
	const sort = String(value ?? '').trim().toLowerCase();
	if (sort === 'likes' || sort === 'views') {
		return sort;
	}
	return 'latest';
}

function referenceRedirectTarget(platform: string, sort: string) {
	return sort === 'latest' ? `/references/${platform}` : `/references/${platform}?sort=${sort}`;
}
function normalizeTopic(value: string | null) {
	if (value === 'learning' || value === 'community') {
		return value;
	}
	if (value === 'cert' || value === 'certifications') {
		return 'certifications';
	}
	return 'news';
}
function normalizeTag(value: string | null) {
	const tag = String(value ?? '').trim();
	return tag && tag !== '전체' ? tag : '';
}

function homeRedirectTarget(url: URL) {
	const params = new URLSearchParams();
	const search = url.searchParams.get('q')?.trim();
	const tag = normalizeTag(url.searchParams.get('tag'));
	if (search) {
		params.set('q', search);
	}
	if (tag) {
		params.set('tag', tag);
	}
	const query = params.toString();
	return query ? `/?${query}` : '/';
}
