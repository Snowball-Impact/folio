import { redirect } from "@sveltejs/kit";
//#region routes/policy/+page.server.ts
var load = async ({ url }) => {
	const type = url.searchParams.get("type") === "terms" ? "terms" : "privacy";
	throw redirect(301, `/policy/${type}`);
};
//#endregion
export { load };
