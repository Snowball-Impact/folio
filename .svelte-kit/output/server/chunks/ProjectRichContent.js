import "./index-server.js";
import { l as html } from "./server.js";
import { i as sanitizeProjectHtml } from "./format.js";
//#region lib/components/ProjectRichContent.svelte
function ProjectRichContent($$renderer, $$props) {
	$$renderer.component(($$renderer) => {
		let { html: html$1, emptyMessage = "입력한 본문이 여기에 표시됩니다.", allowLocalImages = false } = $$props;
		$$renderer.push(`<div class="project-rich-content">${html(sanitizeProjectHtml(html$1, { allowLocalImages }) || `<p>${emptyMessage}</p>`)}</div>`);
	});
}
//#endregion
export { ProjectRichContent as t };
