import "../../../chunks/index-server.js";
import { C as escape_html, i as derived, o as head, t as attr_class } from "../../../chunks/server.js";
import "../../../chunks/auth.js";
import "../../../chunks/projects.js";
import "../../../chunks/navigation.js";
import { t as formatCount } from "../../../chunks/format.js";
//#region routes/my/+page.svelte
function _page($$renderer, $$props) {
	$$renderer.component(($$renderer) => {
		let projects = [];
		const MY_PROJECTS_PAGE_SIZE = 5;
		const stats = derived(() => ({
			projectCount: projects.length,
			publicCount: projects.filter((project) => project.is_public).length,
			viewCount: projects.reduce((total, project) => total + project.view_count, 0),
			likeCount: projects.reduce((total, project) => total + project.like_count, 0)
		}));
		derived(() => Math.max(Math.ceil(projects.length / MY_PROJECTS_PAGE_SIZE), 1));
		derived(() => projects.slice(0, 5));
		head("1yxxndk", $$renderer, ($$renderer) => {
			$$renderer.title(($$renderer) => {
				$$renderer.push(`<title>마이 페이지 | FOLIO</title>`);
			});
			$$renderer.push(`<meta name="description" content="FOLIO 프로필과 내 프로젝트를 관리합니다."/>`);
		});
		$$renderer.push(`<section class="my-hero page-image-hero"><div class="page-image-hero-copy"><div class="page-image-hero-eyebrow">My Page</div> <h1>마이 페이지</h1> <p>프로필과 포트폴리오를 한곳에서 관리하세요.</p></div> <div class="page-image-hero-visual"><img src="/hero-my-page-v2.webp" alt="프로필 카드와 포트폴리오 통계를 표현한 일러스트"/></div></section> `);
		$$renderer.push("<!--[-1-->");
		$$renderer.push(`<section class="profile-overview"><div class="profile-summary"><dl class="profile-fields"><div><dt>작성자</dt> <dd class="profile-name">${escape_html("사용자")}</dd></div> <div><dt>소속</dt> <dd${attr_class("", void 0, { "empty": true })}>${escape_html("소속을 추가해 나를 더 잘 소개해 보세요")}</dd></div> <div><dt>이메일</dt> <dd class="profile-email">${escape_html(void 0)}</dd></div></dl> <div class="profile-about"><p${attr_class("", void 0, { "empty": true })}>${escape_html("아직 자기소개가 없습니다. 어떤 관점으로 데이터를 바라보는지 들려주세요.")}</p></div> <div class="profile-stats" aria-label="내 프로젝트 통계"><span><small>전체 프로젝트</small><strong>${escape_html(formatCount(stats().projectCount))}</strong></span> <span><small>공개 프로젝트</small><strong>${escape_html(formatCount(stats().publicCount))}</strong></span> <span><small>누적 조회</small><strong>${escape_html(formatCount(stats().viewCount))}</strong></span> <span><small>총 좋아요</small><strong>${escape_html(formatCount(stats().likeCount))}</strong></span></div> <button type="button">프로필 편집</button></div></section> <section class="portfolio-section"><div class="section-header"><div><h2>내 프로젝트</h2> <p>등록한 프로젝트를 확인하고 수정하거나 삭제할 수 있습니다.</p></div></div> `);
		$$renderer.push("<!--[-1-->");
		$$renderer.push(`<!--]--> `);
		$$renderer.push("<!--[-1-->");
		$$renderer.push(`<!--]--> `);
		$$renderer.push("<!--[0-->");
		$$renderer.push(`<div class="comments-empty">내 프로젝트를 불러오는 중입니다.</div>`);
		$$renderer.push(`<!--]--></section>`);
		$$renderer.push(`<!--]--> `);
		$$renderer.push("<!--[-1-->");
		$$renderer.push(`<!--]-->`);
	});
}
//#endregion
export { _page as default };
