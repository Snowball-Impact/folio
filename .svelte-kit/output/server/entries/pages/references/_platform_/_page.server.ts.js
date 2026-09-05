import { s as loadReferenceProjects, t as REFERENCE_PLATFORMS } from "../../../../chunks/projects.js";
import { error } from "@sveltejs/kit";
//#region routes/references/[platform]/+page.server.ts
var sortValues = /* @__PURE__ */ new Set([
	"latest",
	"likes",
	"views"
]);
async function load({ params, url }) {
	const platformKey = params.platform;
	if (!(platformKey in REFERENCE_PLATFORMS)) throw error(404, "레퍼런스 플랫폼을 찾을 수 없습니다.");
	const requestedSort = url.searchParams.get("sort");
	const sort = requestedSort && sortValues.has(requestedSort) ? requestedSort : "latest";
	return await loadReferenceProjects(platformKey, sort);
}
//#endregion
export { load };
