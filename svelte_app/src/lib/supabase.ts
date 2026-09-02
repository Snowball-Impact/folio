import { createClient, type SupabaseClient } from '@supabase/supabase-js';

let client: SupabaseClient | null = null;

export function isSupabaseConfigured() {
	return Boolean(import.meta.env.PUBLIC_SUPABASE_URL && import.meta.env.PUBLIC_SUPABASE_PUBLISHABLE_KEY);
}

export function getSupabaseClient() {
	const supabaseUrl = import.meta.env.PUBLIC_SUPABASE_URL;
	const publishableKey = import.meta.env.PUBLIC_SUPABASE_PUBLISHABLE_KEY;
	if (!supabaseUrl || !publishableKey) {
		return null;
	}
	if (!client) {
		client = createClient(supabaseUrl, publishableKey);
	}
	return client;
}
