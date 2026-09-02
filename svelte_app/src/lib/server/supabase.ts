import { env as privateEnv } from '$env/dynamic/private';
import { createClient } from '@supabase/supabase-js';

export function getSupabaseServerClient() {
	const supabaseUrl = import.meta.env.PUBLIC_SUPABASE_URL;
	const serviceRoleKey = privateEnv.SUPABASE_SERVICE_ROLE_KEY;
	if (!supabaseUrl || !serviceRoleKey) {
		return null;
	}
	return createClient(supabaseUrl, serviceRoleKey, {
		auth: {
			autoRefreshToken: false,
			persistSession: false
		}
	});
}

export function getSupabaseUserClient(accessToken: string) {
	const supabaseUrl = import.meta.env.PUBLIC_SUPABASE_URL;
	const publishableKey = import.meta.env.PUBLIC_SUPABASE_PUBLISHABLE_KEY;
	if (!supabaseUrl || !publishableKey || !accessToken) {
		return null;
	}
	return createClient(supabaseUrl, publishableKey, {
		auth: {
			autoRefreshToken: false,
			persistSession: false
		},
		global: {
			headers: {
				Authorization: `Bearer ${accessToken}`
			}
		}
	});
}
