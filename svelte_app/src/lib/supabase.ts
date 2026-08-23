import { env } from '$env/dynamic/public';
import { createClient, type SupabaseClient } from '@supabase/supabase-js';

let client: SupabaseClient | null = null;

export function isSupabaseConfigured() {
	return Boolean(env.PUBLIC_SUPABASE_URL && env.PUBLIC_SUPABASE_PUBLISHABLE_KEY);
}

export function getSupabaseClient() {
	const supabaseUrl = env.PUBLIC_SUPABASE_URL;
	const publishableKey = env.PUBLIC_SUPABASE_PUBLISHABLE_KEY;
	if (!supabaseUrl || !publishableKey) {
		return null;
	}
	if (!client) {
		client = createClient(supabaseUrl, publishableKey);
	}
	return client;
}
