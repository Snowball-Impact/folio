import { s as loadReferenceProjects } from "../../../../chunks/projects.js";
//#region routes/references/powerbi/+page.server.ts
var sortValues = /* @__PURE__ */ new Set([
	"latest",
	"likes",
	"views"
]);
async function load({ url }) {
	const requestedSort = url.searchParams.get("sort");
	const sort = requestedSort && sortValues.has(requestedSort) ? requestedSort : "latest";
	return await loadReferenceProjects("powerbi", sort);
}
//#endregion
export { load };
