import "../../../chunks/index-server.js";
import { i as derived, o as head } from "../../../chunks/server.js";
import "../../../chunks/auth.js";
import "../../../chunks/navigation.js";
import "../../../chunks/notifications.js";
import "../../../chunks/format.js";
//#region routes/notifications/+page.svelte
function _page($$renderer, $$props) {
	$$renderer.component(($$renderer) => {
		let notifications = [];
		const unreadCount = derived(() => notifications.filter((notification) => !notification.is_read).length);
		head("11vqhfc", $$renderer, ($$renderer) => {
			$$renderer.title(($$renderer) => {
				$$renderer.push(`<title>알림 | FOLIO</title>`);
			});
			$$renderer.push(`<meta name="description" content="FOLIO 프로젝트 댓글 알림을 확인합니다."/>`);
		});
		$$renderer.push(`<section class="notification-hero page-image-hero"><div class="page-image-hero-copy"><div class="page-image-hero-eyebrow">Notifications</div> <h1>알림</h1> <p>내 프로젝트에 새로 들어온 반응을 확인하세요.</p></div> <div class="page-image-hero-visual"><img src="/hero-my-page-v2.webp" alt="프로필 카드와 포트폴리오 통계를 표현한 일러스트"/></div></section> `);
		$$renderer.push("<!--[-1-->");
		$$renderer.push(`<section class="notifications-panel"><div class="section-header"><div><h2>최근 알림</h2> <p>알림 페이지를 열면 새 알림은 읽음 처리됩니다.</p></div> `);
		if (unreadCount() > 0) {
			$$renderer.push("<!--[0-->");
			$$renderer.push(`<button type="button">모두 읽음</button>`);
		} else $$renderer.push("<!--[-1-->");
		$$renderer.push(`<!--]--></div> `);
		$$renderer.push("<!--[-1-->");
		$$renderer.push(`<!--]--> `);
		$$renderer.push("<!--[-1-->");
		$$renderer.push(`<!--]--> `);
		$$renderer.push("<!--[0-->");
		$$renderer.push(`<div class="comments-empty">알림을 불러오는 중입니다.</div>`);
		$$renderer.push(`<!--]--></section>`);
		$$renderer.push(`<!--]-->`);
	});
}
//#endregion
export { _page as default };
