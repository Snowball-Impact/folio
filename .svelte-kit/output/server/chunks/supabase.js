import { t as private_env } from "./shared-server.js";
import { createClient } from "@supabase/supabase-js";
//#region lib/server/supabase.ts
function getSupabaseServerClient() {
	const supabaseUrl = "https://vfvcpxrmirlnsfdjuaaz.supabase.co";
	const serviceRoleKey = private_env.SUPABASE_SERVICE_ROLE_KEY;
	if (!serviceRoleKey) return null;
	return createClient(supabaseUrl, serviceRoleKey, { auth: {
		autoRefreshToken: false,
		persistSession: false
	} });
}
function getSupabaseUserClient(accessToken) {
	const supabaseUrl = "https://vfvcpxrmirlnsfdjuaaz.supabase.co";
	const publishableKey = "sb_publishable_so5bInU80pmX1chi5Fi33A_ZWK3L3Hp";
	if (!accessToken) return null;
	return createClient(supabaseUrl, publishableKey, {
		auth: {
			autoRefreshToken: false,
			persistSession: false
		},
		global: { headers: { Authorization: `Bearer ${accessToken}` } }
	});
}
//#endregion
export { getSupabaseUserClient as n, getSupabaseServerClient as t };
