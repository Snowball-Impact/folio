import { C as escape_html, o as head, x as attr } from "../../../chunks/server.js";
import { t as page } from "../../../chunks/state.js";
import "../../../chunks/navigation.js";
//#region routes/reset-password/+page.svelte
function _page($$renderer, $$props) {
	$$renderer.component(($$renderer) => {
		let email = page.url.searchParams.get("email") ?? "";
		let password = "";
		let passwordConfirm = "";
		let recovery = {
			code: "",
			tokenHash: "",
			accessToken: "",
			refreshToken: "",
			hasRecovery: false
		};
		let submitting = false;
		head("1nkjjjb", $$renderer, ($$renderer) => {
			$$renderer.title(($$renderer) => {
				$$renderer.push(`<title>비밀번호 재설정 | FOLIO</title>`);
			});
			$$renderer.push(`<meta name="description" content="FOLIO 계정 비밀번호를 재설정합니다."/>`);
		});
		$$renderer.push(`<section class="auth-shell"><div class="auth-card"><header class="auth-header"><div class="eyebrow">Password Reset</div> <h1>비밀번호 재설정</h1> <p>${escape_html(recovery.hasRecovery ? "새 비밀번호를 입력하세요." : "가입한 이메일로 재설정 링크를 보내드립니다.")}</p></header> `);
		$$renderer.push("<!--[-1-->");
		$$renderer.push(`<!--]--> `);
		if (recovery.hasRecovery) {
			$$renderer.push("<!--[0-->");
			$$renderer.push(`<form class="auth-form"><label><span>새 비밀번호</span> <input${attr("value", password)} type="password" placeholder="8자 이상 입력" autocomplete="new-password"/></label> <label><span>새 비밀번호 확인</span> <input${attr("value", passwordConfirm)} type="password" autocomplete="new-password"/></label> <button type="submit"${attr("disabled", submitting, true)}>${escape_html("비밀번호 변경")}</button></form>`);
		} else {
			$$renderer.push("<!--[-1-->");
			$$renderer.push(`<form class="auth-form"><label><span>이메일</span> <input${attr("value", email)} type="email" placeholder="name@example.com" autocomplete="email"/></label> <button type="submit"${attr("disabled", submitting, true)}>${escape_html("재설정 메일 받기")}</button></form>`);
		}
		$$renderer.push(`<!--]--> <div class="auth-links"><a href="/login">로그인으로 돌아가기</a></div></div></section>`);
	});
}
//#endregion
export { _page as default };
