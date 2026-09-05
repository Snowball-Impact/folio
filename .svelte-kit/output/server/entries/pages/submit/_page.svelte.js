import "../../../chunks/index-server.js";
import { i as derived, o as head } from "../../../chunks/server.js";
import "../../../chunks/auth.js";
import "../../../chunks/client.js";
import "../../../chunks/navigation.js";
import { c as emptyProjectSubmitInput, d as ProjectHeroThumbnailPreview, l as previewTags } from "../../../chunks/projectBody.js";
//#region routes/submit/+page.svelte
function _page($$renderer, $$props) {
	$$renderer.component(($$renderer) => {
		let input = emptyProjectSubmitInput();
		let thumbnailPreviewUrl = null;
		const previewProject = derived(() => ({
			id: "submit-preview",
			author_id: "",
			title: input.title.trim() || "프로젝트명이 여기에 표시됩니다.",
			one_liner: input.one_liner.trim() || "프로젝트 한 줄 소개가 표시됩니다.",
			problem: input.problem,
			dataset: input.dataset,
			process: input.process,
			insights: input.insights,
			tags: previewTags(input.tags, input.platform),
			thumbnail_url: input.thumbnail_mode === "manual_url" ? input.thumbnail_url.trim() || null : input.thumbnail_mode === "upload" ? thumbnailPreviewUrl : input.thumbnail_mode === "capture" ? input.thumbnail_url.trim() || null : null,
			thumbnail_mode: input.thumbnail_mode,
			power_bi_url: input.power_bi_url.trim() || null,
			report_url: input.report_url.trim() || null,
			github_url: input.github_url.trim() || null,
			platform_key: input.platform === "other" ? null : input.platform,
			project_type: input.platform === "datastudio" ? "looker" : input.platform === "other" ? "other" : input.platform,
			status: "published",
			embed_status: input.power_bi_url.trim() ? "supported" : "external_only",
			is_public: true,
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
			head("16zjrm6", $$renderer, ($$renderer) => {
				$$renderer.title(($$renderer) => {
					$$renderer.push(`<title>새 프로젝트 등록 | FOLIO</title>`);
				});
				$$renderer.push(`<meta name="description" content="FOLIO에 데이터 분석 프로젝트를 등록합니다."/>`);
			});
			$$renderer.push(`<section class="submit-hero submit-preview-hero"><div><div class="eyebrow">Submit</div> <h1>새 프로젝트 등록</h1> <p>당신의 데이터 분석 프로젝트를 포트폴리오로 공개하세요.</p></div> `);
			ProjectHeroThumbnailPreview($$renderer, { project: previewProject() });
			$$renderer.push(`<!----></section> `);
			$$renderer.push("<!--[-1-->");
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
