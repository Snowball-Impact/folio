import { C as escape_html, i as derived, o as head, x as attr } from "../../../../chunks/server.js";
//#region routes/policy/[type]/+page.svelte
function _page($$renderer, $$props) {
	$$renderer.component(($$renderer) => {
		let { data } = $$props;
		const meta = derived(() => [data.policy?.version ? `버전 ${data.policy.version}` : "", data.policy?.effective_at ? `시행일 ${String(data.policy.effective_at).slice(0, 10)}` : ""].filter(Boolean));
		head("1v86xo3", $$renderer, ($$renderer) => {
			$$renderer.title(($$renderer) => {
				$$renderer.push(`<title>${escape_html(data.label)} | FOLIO</title>`);
			});
			$$renderer.push(`<meta name="description"${attr("content", `FOLIO ${data.label}`)}/>`);
		});
		$$renderer.push(`<section class="policy-page-hero"><div class="eyebrow">FOLIO POLICY</div> <h1>${escape_html(data.label)}</h1> `);
		if (meta().length > 0) {
			$$renderer.push("<!--[0-->");
			$$renderer.push(`<p>${escape_html(meta().join(" · "))}</p>`);
		} else $$renderer.push("<!--[-1-->");
		$$renderer.push(`<!--]--></section> <section class="policy-document">`);
		if (data.error) {
			$$renderer.push("<!--[0-->");
			$$renderer.push(`<div class="notice compact">${escape_html(data.error)}</div>`);
		} else if (data.policy) {
			$$renderer.push("<!--[1-->");
			if (data.policy.summary) {
				$$renderer.push("<!--[0-->");
				$$renderer.push(`<div class="policy-summary"><strong>요약</strong> <p>${escape_html(data.policy.summary)}</p></div>`);
			} else $$renderer.push("<!--[-1-->");
			$$renderer.push(`<!--]--> <div class="policy-body">${escape_html(data.policy.content || "정책 본문이 아직 등록되지 않았습니다.")}</div> `);
			if (data.policy.content_url) {
				$$renderer.push("<!--[0-->");
				$$renderer.push(`<a class="button-link"${attr("href", data.policy.content_url)} target="_blank" rel="noreferrer">전문 링크</a>`);
			} else $$renderer.push("<!--[-1-->");
			$$renderer.push(`<!--]-->`);
		} else $$renderer.push("<!--[-1-->");
		$$renderer.push(`<!--]--></section>`);
	});
}
//#endregion
export { _page as default };
