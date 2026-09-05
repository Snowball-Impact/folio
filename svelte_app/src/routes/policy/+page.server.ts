import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ url }) => {
	const type = url.searchParams.get('type') === 'terms' ? 'terms' : 'privacy';
	throw redirect(301, `/policy/${type}`);
};