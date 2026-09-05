// @ts-nocheck
import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load = async ({ url }: Parameters<PageServerLoad>[0]) => {
	const type = url.searchParams.get('type') === 'terms' ? 'terms' : 'privacy';
	throw redirect(301, `/policy/${type}`);
};