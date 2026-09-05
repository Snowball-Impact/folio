import { C as escape_html, a as ensure_array_like, i as derived, o as head, t as attr_class, x as attr } from "../../../../chunks/server.js";
import { t as ProjectCard } from "../../../../chunks/ProjectCard.js";
//#region routes/references/[platform]/+page.svelte
function _page($$renderer, $$props) {
	$$renderer.component(($$renderer) => {
		const PAGE_SIZE = 24;
		let { data } = $$props;
		let visibleCount = PAGE_SIZE;
		const projects = derived(() => data.projects);
		const visibleProjects = derived(() => projects().slice(0, visibleCount));
		const remainingCount = derived(() => Math.max(projects().length - visibleCount, 0));
		const referencePlatforms = [
			{
				key: "powerbi",
				label: "Power BI",
				href: "/references/powerbi"
			},
			{
				key: "tableau",
				label: "Tableau",
				href: "/references/tableau"
			},
			{
				key: "datastudio",
				label: "Data Studio",
				href: "/references/datastudio"
			},
			{
				key: "streamlit",
				label: "Streamlit",
				href: "/references/streamlit"
			}
		];
		const sortItems = [
			{
				key: "latest",
				label: "최신순"
			},
			{
				key: "likes",
				label: "좋아요순"
			},
			{
				key: "views",
				label: "조회수순"
			}
		];
		head("1h7mi2", $$renderer, ($$renderer) => {
			$$renderer.title(($$renderer) => {
				$$renderer.push(`<title>${escape_html(data.platform.label)} 레퍼런스 | FOLIO</title>`);
			});
			$$renderer.push(`<meta name="description"${attr("content", data.platform.description)}/>`);
		});
		$$renderer.push(`<section class="reference-hero"><div class="reference-hero-copy"><div class="eyebrow">Reference Library</div> <h1 class="reference-hero-title"><span class="reference-hero-count">${escape_html(projects().length.toLocaleString("ko-KR"))}</span><span class="reference-hero-title-text">개의 레퍼런스를 참고해보세요.</span></h1> <p>${escape_html(data.platform.description)}</p></div> <div class="reference-hero-visual"${attr("aria-label", data.platform.label)}><div class="reference-hero-logo"><img${attr_class(`reference-logo-image reference-logo-image-${data.platform.key}`)}${attr("src", `/reference-${data.platform.key}-logo-cropped.webp`)} alt=""/></div> <nav class="reference-hero-tabs" aria-label="레퍼런스 플랫폼"><!--[-->`);
		const each_array = ensure_array_like(referencePlatforms);
		for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
			let platform = each_array[$$index];
			$$renderer.push(`<a${attr("href", platform.href)}${attr("aria-current", platform.key === data.platform.key ? "page" : void 0)}${attr_class("", void 0, { "active": platform.key === data.platform.key })}>${escape_html(platform.label)}</a>`);
		}
		$$renderer.push(`<!--]--></nav></div></section> <section class="reference-toolbar" aria-label="레퍼런스 정렬"><span>정렬</span> <nav><!--[-->`);
		const each_array_1 = ensure_array_like(sortItems);
		for (let $$index_1 = 0, $$length = each_array_1.length; $$index_1 < $$length; $$index_1++) {
			let item = each_array_1[$$index_1];
			$$renderer.push(`<a${attr("href", `/references/${data.platform.key}?sort=${item.key}`)}${attr_class("", void 0, { "active": item.key === data.sort })}>${escape_html(item.label)}</a>`);
		}
		$$renderer.push(`<!--]--></nav></section> `);
		if (data.error) {
			$$renderer.push("<!--[0-->");
			$$renderer.push(`<div class="notice">${escape_html(data.error)}</div>`);
		} else if (visibleProjects().length > 0) {
			$$renderer.push("<!--[1-->");
			$$renderer.push(`<section class="reference-grid" aria-label="레퍼런스 카드 목록"><!--[-->`);
			const each_array_2 = ensure_array_like(visibleProjects());
			for (let $$index_2 = 0, $$length = each_array_2.length; $$index_2 < $$length; $$index_2++) {
				let project = each_array_2[$$index_2];
				ProjectCard($$renderer, { project });
			}
			$$renderer.push(`<!--]--></section> `);
			if (remainingCount() > 0) {
				$$renderer.push("<!--[0-->");
				$$renderer.push(`<div class="load-more"><button type="button">${escape_html(Math.min(PAGE_SIZE, remainingCount()))}개 더 보기</button> <span>${escape_html(remainingCount())}개 더 볼 수 있습니다.</span></div>`);
			} else {
				$$renderer.push("<!--[-1-->");
				$$renderer.push(`<div class="reference-end">모든 레퍼런스를 불러왔습니다.</div>`);
			}
			$$renderer.push(`<!--]-->`);
		} else {
			$$renderer.push("<!--[-1-->");
			$$renderer.push(`<div class="empty-panel">아직 표시할 레퍼런스가 없습니다.</div>`);
		}
		$$renderer.push(`<!--]-->`);
	});
}
//#endregion
export { _page as default };
