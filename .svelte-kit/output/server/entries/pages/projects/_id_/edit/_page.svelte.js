import "../../../../../chunks/index-server.js";
import { C as escape_html, i as derived, o as head } from "../../../../../chunks/server.js";
import "../../../../../chunks/auth.js";
import "../../../../../chunks/projects.js";
import "../../../../../chunks/client.js";
import { t as page } from "../../../../../chunks/state.js";
import "../../../../../chunks/navigation.js";
import { c as emptyProjectSubmitInput, l as previewTags } from "../../../../../chunks/projectBody.js";
//#region routes/projects/[id]/edit/+page.svelte
function _page($$renderer, $$props) {
	$$renderer.component(($$renderer) => {
		let input = emptyProjectSubmitInput();
		const projectId = derived(() => page.params.id ?? "");
		derived(() => ({
			id: projectId(),
			author_id: "",
			title: input.title.trim() || "프로젝트명이 여기에 표시됩니다.",
			one_liner: input.one_liner.trim() || "프로젝트 한 줄 소개가 표시됩니다.",
			problem: input.problem,
			dataset: input.dataset,
			process: input.process,
			insights: input.insights,
			tags: previewTags(input.tags, input.platform),
			thumbnail_url: input.delete_thumbnail ? null : input.thumbnail_mode === "manual_url" ? input.thumbnail_url.trim() || null : input.thumbnail_mode === "upload" ? input.thumbnail_url.trim() || null : input.thumbnail_mode === "capture" ? input.thumbnail_url.trim() || null : null,
			thumbnail_mode: input.delete_thumbnail ? "auto_cover" : input.thumbnail_mode,
			power_bi_url: input.delete_pbix ? null : input.power_bi_url.trim() || null,
			report_url: input.report_url.trim() || null,
			github_url: input.github_url.trim() || null,
			platform_key: input.platform === "other" ? null : input.platform,
			project_type: input.platform === "datastudio" ? "looker" : input.platform === "other" ? "other" : input.platform,
			status: "published",
			embed_status: !input.delete_pbix && input.power_bi_url.trim() ? "supported" : "external_only",
			is_public: input.is_public,
			view_count: 0,
			created_at: (/* @__PURE__ */ new Date()).toISOString(),
			updated_at: (/* @__PURE__ */ new Date()).toISOString(),
			author: { name: "작성자" },
			like_count: 0,
			comment_count: 0
		}));
		let $$settled = true;
		let $$inner_renderer;
		function $$render_inner($$renderer) {
			head("12koaxh", $$renderer, ($$renderer) => {
				$$renderer.title(($$renderer) => {
					$$renderer.push(`<title>${escape_html("프로젝트 수정")} | FOLIO</title>`);
				});
				$$renderer.push(`<meta name="description" content="FOLIO 프로젝트 정보를 수정합니다."/>`);
			});
			$$renderer.push("<!--[0-->");
			$$renderer.push(`<div class="comments-empty">프로젝트 정보를 불러오는 중입니다.</div>`);
			$$renderer.push(`<!--]-->`);
		}
		do {
			$$settled = true;
			$$inner_renderer = $$renderer.copy();
			$$render_inner($$inner_renderer);
		} while (!$$settled);
		$$renderer.subsume($$inner_renderer);
	});
}
//#endregion
export { _page as default };
