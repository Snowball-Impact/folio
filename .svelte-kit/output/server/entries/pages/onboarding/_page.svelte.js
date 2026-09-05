import "../../../chunks/index-server.js";
import { C as escape_html, i as derived, o as head } from "../../../chunks/server.js";
import "../../../chunks/auth.js";
import "../../../chunks/client.js";
import { t as page } from "../../../chunks/state.js";
import "../../../chunks/navigation.js";
import "../../../chunks/onboarding.js";
//#region routes/onboarding/+page.svelte
function _page($$renderer, $$props) {
	$$renderer.component(($$renderer) => {
		derived(() => page.url.searchParams.get("next") || "/");
		const isPolicyUpdate = derived(() => Boolean(void 0));
		const effectiveDate = derived(() => "");
		head("1qry2wt", $$renderer, ($$renderer) => {
			$$renderer.title(($$renderer) => {
				$$renderer.push(`<title>정책 동의 | FOLIO</title>`);
			});
			$$renderer.push(`<meta name="description" content="FOLIO 서비스 이용을 위한 필수 정책 동의 화면입니다."/>`);
		});
		$$renderer.push(`<section class="onboarding-hero"><span>${escape_html(isPolicyUpdate() ? "정책 업데이트" : "서비스 시작")}</span> <h1>${escape_html(isPolicyUpdate() ? "이용약관이 새롭게 개정되었어요" : "서비스 이용을 시작하기 전")}</h1> <p>${escape_html(isPolicyUpdate() ? "서비스를 계속 이용하시려면 변경된 정책을 확인하고 다시 동의해 주세요." : "서비스 이용약관과 개인정보 처리방침을 확인하고 동의해 주세요.")}</p> `);
		if (isPolicyUpdate() && effectiveDate()) {
			$$renderer.push("<!--[0-->");
			$$renderer.push(`<em>${escape_html(effectiveDate())}부터 적용되는 내용입니다.</em>`);
		} else $$renderer.push("<!--[-1-->");
		$$renderer.push(`<!--]--></section> <section class="onboarding-card">`);
		$$renderer.push("<!--[0-->");
		$$renderer.push(`<div class="comments-empty">온보딩 정보를 불러오는 중입니다.</div>`);
		$$renderer.push(`<!--]--></section>`);
	});
}
//#endregion
export { _page as default };
