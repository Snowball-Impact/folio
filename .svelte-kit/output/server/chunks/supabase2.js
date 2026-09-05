import { createClient } from "@supabase/supabase-js";
//#region lib/supabase.ts
var client = null;
function getSupabaseClient() {
	const supabaseUrl = "https://vfvcpxrmirlnsfdjuaaz.supabase.co";
	const publishableKey = "sb_publishable_so5bInU80pmX1chi5Fi33A_ZWK3L3Hp";
	if (!client) client = createClient(supabaseUrl, publishableKey);
	return client;
}
//#endregion
export { getSupabaseClient as t };
