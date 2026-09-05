import { C as escape_html, i as derived, o as head, x as attr } from "../../../chunks/server.js";
import { t as page } from "../../../chunks/state.js";
import "../../../chunks/navigation.js";
//#region routes/login/+page.svelte
function _page($$renderer, $$props) {
	$$renderer.component(($$renderer) => {
		let email = "";
		let password = "";
		let submitting = false;
		const verified = derived(() => page.url.searchParams.get("verified") === "1");
		const reset = derived(() => page.url.searchParams.get("reset") === "1");
		derived(() => page.url.searchParams.get("next") || "/");
		head("1bc9zjt", $$renderer, ($$renderer) => {
			$$renderer.title(($$renderer) => {
				$$renderer.push(`<title>로그인 | FOLIO</title>`);
			});
			$$renderer.push(`<meta name="description" content="FOLIO 계정으로 로그인합니다."/>`);
		});
		$$renderer.push(`<section class="auth-shell"><div class="auth-card"><header class="auth-header"><div class="eyebrow">Login</div> <h1>로그인</h1> <p>등록한 프로젝트와 포트폴리오를 이어서 관리하세요.</p></header> `);
		if (verified()) {
			$$renderer.push("<!--[0-->");
			$$renderer.push(`<div class="notice compact">이메일 인증이 완료되었습니다. 로그인하세요.</div>`);
		} else $$renderer.push("<!--[-1-->");
		$$renderer.push(`<!--]--> `);
		if (reset()) {
			$$renderer.push("<!--[0-->");
			$$renderer.push(`<div class="notice compact">비밀번호가 변경되었습니다. 새 비밀번호로 로그인하세요.</div>`);
		} else $$renderer.push("<!--[-1-->");
		$$renderer.push(`<!--]--> `);
		$$renderer.push("<!--[-1-->");
		$$renderer.push(`<!--]--> <form class="auth-form"><label><span>이메일</span> <input${attr("value", email)} type="email" placeholder="name@example.com" autocomplete="email"/></label> <label><span>비밀번호</span> <input${attr("value", password)} type="password" autocomplete="current-password"/></label> <button type="submit"${attr("disabled", submitting, true)}>${escape_html("로그인")}</button></form> <div class="auth-links"><a href="/reset-password">비밀번호 찾기</a> <a href="/signup">회원가입하기</a></div></div></section>`);
	});
}
//#endregion
export { _page as default };
