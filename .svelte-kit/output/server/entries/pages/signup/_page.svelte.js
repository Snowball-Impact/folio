import "../../../chunks/index-server.js";
import { C as escape_html, i as derived, o as head, x as attr } from "../../../chunks/server.js";
import "../../../chunks/onboarding.js";
//#region routes/signup/+page.svelte
function _page($$renderer, $$props) {
	$$renderer.component(($$renderer) => {
		let email = "";
		let password = "";
		let passwordConfirm = "";
		let name = "";
		let organization = "";
		let policies = [];
		let policyLoading = true;
		derived(() => policies.map((policy) => policy.id));
		const sharedPolicyEffectiveDate = derived(() => sharedEffectiveDate(policies));
		function sharedEffectiveDate(values) {
			const dates = [...new Set(values.map((policy) => policy.effective_at?.slice(0, 10)).filter(Boolean))];
			return dates.length === 1 ? dates[0] : "";
		}
		head("yfi10e", $$renderer, ($$renderer) => {
			$$renderer.title(($$renderer) => {
				$$renderer.push(`<title>회원가입 | FOLIO</title>`);
			});
			$$renderer.push(`<meta name="description" content="FOLIO 계정을 만들고 프로젝트를 공유합니다."/>`);
		});
		$$renderer.push(`<section class="auth-shell"><div class="auth-card signup"><header class="auth-header"><div class="eyebrow">Sign Up</div> <h1>회원가입</h1> <p>이메일 인증 후 프로젝트를 등록하고 공유할 수 있습니다.</p></header> <form class="auth-form"><label><span>이메일 *</span> <input${attr("value", email)} type="email" placeholder="name@example.com" autocomplete="email"/></label> <label><span>비밀번호 *</span> <input${attr("value", password)} type="password" placeholder="8자 이상 입력" autocomplete="new-password"/></label> <label><span>비밀번호 확인 *</span> <input${attr("value", passwordConfirm)} type="password" autocomplete="new-password"/></label> <label><span>이름 *</span> <input${attr("value", name)} type="text" placeholder="홍길동" autocomplete="name"/></label> <label><span>소속 *</span> <input${attr("value", organization)} type="text" placeholder="개인, 학원, 학교, 기관, 회사명을 입력하세요" autocomplete="organization"/></label> <section class="signup-policy-panel" aria-label="필수 정책 동의"><div class="signup-policy-heading"><div><strong>필수 동의</strong> <p>서비스 이용을 위해 아래 항목에 동의해 주세요.`);
		if (sharedPolicyEffectiveDate()) {
			$$renderer.push("<!--[0-->");
			$$renderer.push(`<span>${escape_html(sharedPolicyEffectiveDate())} 시행</span>`);
		} else $$renderer.push("<!--[-1-->");
		$$renderer.push(`<!--]--></p></div></div> `);
		$$renderer.push("<!--[0-->");
		$$renderer.push(`<p>정책 정보를 불러오는 중입니다.</p>`);
		$$renderer.push(`<!--]--></section> <button type="submit"${attr("disabled", policyLoading, true)}>${escape_html("회원가입")}</button> `);
		$$renderer.push("<!--[-1-->");
		$$renderer.push(`<!--]--></form> <div class="auth-links"><a href="/login">이미 계정이 있다면 로그인하기</a></div></div></section>`);
	});
}
//#endregion
export { _page as default };
