import "../../chunks/index-server.js";
import "../../chunks/shared-server.js";
import { i as derived, o as head, t as attr_class, x as attr } from "../../chunks/server.js";
import "../../chunks/supabase2.js";
import "../../chunks/auth.js";
import "../../chunks/client.js";
import { t as page } from "../../chunks/state.js";
import "../../chunks/navigation.js";
import "../../chunks/notifications.js";
import "../../chunks/onboarding.js";
//#region lib/components/AuthNav.svelte
function AuthNav($$renderer, $$props) {
	$$renderer.component(($$renderer) => {
		let powerBiOpen = false;
		let mobileNavOpen = false;
		const pathname = derived(() => page.url.pathname);
		const topic = derived(() => page.url.searchParams.get("topic") ?? "news");
		function isPathActive(target) {
			if (target === "/") return pathname() === "/";
			return pathname() === target || pathname().startsWith(`${target}/`);
		}
		function isPowerBiActive() {
			return pathname() === "/powerbi" || pathname() === "/references/powerbi";
		}
		function isPowerBiTopicActive(targetTopic) {
			return pathname() === "/powerbi" && topic() === targetTopic;
		}
		$$renderer.push(`<button type="button" class="mobile-nav-toggle"${attr("aria-expanded", mobileNavOpen)} aria-controls="primary-navigation"><span aria-hidden="true"></span> 메뉴</button> <nav id="primary-navigation"${attr_class("nav", void 0, { "open": mobileNavOpen })} aria-label="주요 메뉴"><a${attr("aria-current", isPathActive("/") ? "page" : void 0)} href="/"${attr_class("", void 0, { "active": isPathActive("/") })}>홈 갤러리</a> <a${attr("aria-current", isPathActive("/about") ? "page" : void 0)} href="/about"${attr_class("", void 0, { "active": isPathActive("/about") })}>서비스 소개</a> <div${attr_class("nav-menu powerbi-menu", void 0, { "open": powerBiOpen })}><button type="button"${attr_class("nav-menu-trigger", void 0, { "active": isPowerBiActive() })}${attr("aria-current", isPowerBiActive() ? "page" : void 0)}${attr("aria-expanded", powerBiOpen)} aria-haspopup="menu">Power BI <span class="nav-caret" aria-hidden="true"></span></button> <div class="nav-submenu" aria-label="Power BI 콘텐츠 메뉴"><a href="/powerbi"${attr_class("", void 0, { "active": isPowerBiTopicActive("news") })}>업데이트 소식</a> <a href="/powerbi?topic=community"${attr_class("", void 0, { "active": isPowerBiTopicActive("community") })}>커뮤니티 소식</a> <a href="/powerbi?topic=learning"${attr_class("", void 0, { "active": isPowerBiTopicActive("learning") })}>학습 콘텐츠</a> <a href="/powerbi?topic=certifications"${attr_class("", void 0, { "active": isPowerBiTopicActive("certifications") })}>자격증</a> <a href="/references/powerbi"${attr_class("", void 0, { "active": pathname() === "/references/powerbi" })}>레퍼런스</a></div></div> <a${attr("aria-current", isPathActive("/submit") ? "page" : void 0)} href="/submit"${attr_class("", void 0, { "active": isPathActive("/submit") })}>프로젝트 등록</a> `);
		$$renderer.push("<!--[-1-->");
		$$renderer.push(`<a${attr("aria-current", isPathActive("/login") ? "page" : void 0)} href="/login"${attr_class("", void 0, { "active": isPathActive("/login") })}>로그인</a>`);
		$$renderer.push(`<!--]--></nav>`);
	});
}
//#endregion
//#region lib/components/OnboardingGate.svelte
function OnboardingGate($$renderer, $$props) {
	$$renderer.component(($$renderer) => {});
}
//#endregion
//#region routes/+layout.svelte
function _layout($$renderer, $$props) {
	$$renderer.component(($$renderer) => {
		let { children } = $$props;
		const isThumbnailCapture = derived(() => page.url.searchParams.get("capture") === "thumbnail");
		head("q8odwi", $$renderer, ($$renderer) => {
			$$renderer.push(`<link rel="icon" href="/logo.webp"/>`);
		});
		$$renderer.push(`<div class="app-shell">`);
		if (!isThumbnailCapture()) {
			$$renderer.push("<!--[0-->");
			OnboardingGate($$renderer, {});
			$$renderer.push(`<!----> <header class="site-header"><div class="site-header-inner"><a class="brand" href="/" aria-label="FOLIO 홈으로 이동"><img src="/logo.webp" alt="FOLIO"/></a> `);
			AuthNav($$renderer, {});
			$$renderer.push(`<!----></div></header>`);
		} else $$renderer.push("<!--[-1-->");
		$$renderer.push(`<!--]--> <main${attr_class("page-shell", void 0, { "thumbnail-capture-page": isThumbnailCapture() })}>`);
		children($$renderer);
		$$renderer.push(`<!----></main> `);
		if (!isThumbnailCapture()) {
			$$renderer.push("<!--[0-->");
			$$renderer.push(`<footer class="site-footer"><div class="site-footer-inner"><span>Copyright © 2026 Snowball Impact. All rights reserved.</span> <span class="site-footer-version">v2026.09.01.01</span> <nav aria-label="푸터 링크"><a href="/policy/terms">이용약관</a> <a href="/policy/privacy">개인정보 처리방침</a> <a href="mailto:admin@foilo.it.kr?subject=FOLIO%20%EC%84%9C%EB%B9%84%EC%8A%A4%20%EB%AC%B8%EC%9D%98">문의</a></nav></div></footer>`);
		} else $$renderer.push("<!--[-1-->");
		$$renderer.push(`<!--]--></div>`);
	});
}
//#endregion
export { _layout as default };
