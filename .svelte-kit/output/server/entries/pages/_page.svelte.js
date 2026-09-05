import { n as onDestroy } from "../../chunks/index-server.js";
import { C as escape_html, a as ensure_array_like, i as derived, l as html, n as attr_style, o as head, t as attr_class, x as attr } from "../../chunks/server.js";
import { t as ProjectCard } from "../../chunks/ProjectCard.js";
//#region lib/components/ProjectRail.svelte
function ProjectRail($$renderer, $$props) {
	$$renderer.component(($$renderer) => {
		let { title, description, projects, emptyMessage = "표시할 프로젝트가 아직 없습니다." } = $$props;
		let thumbWidth = 44;
		let thumbLeft = 0;
		const titleParts = derived(() => splitRailTitle(title));
		onDestroy(() => {
			endThumbDrag();
		});
		function dragThumb(event) {}
		function endThumbDrag() {
			if (typeof window !== "undefined") window.removeEventListener("pointermove", dragThumb);
		}
		function splitRailTitle(value) {
			const highlight = [
				"새로 공개",
				"조회수",
				"좋아요"
			].find((item) => value.includes(item));
			if (!highlight) return {
				before: value,
				highlight: "",
				after: ""
			};
			const index = value.indexOf(highlight);
			return {
				before: value.slice(0, index),
				highlight,
				after: value.slice(index + highlight.length)
			};
		}
		$$renderer.push(`<section class="project-rail-section"><div class="project-rail-head"><button class="rail-scroll-button" type="button"${attr("aria-label", `${description} 왼쪽으로 스크롤`)}>‹</button> <h2>${escape_html(titleParts().before)}<span>${escape_html(titleParts().highlight)}</span>${escape_html(titleParts().after)}</h2> <button class="rail-scroll-button" type="button"${attr("aria-label", `${description} 오른쪽으로 스크롤`)}>›</button></div> `);
		if (projects.length > 0) {
			$$renderer.push("<!--[0-->");
			$$renderer.push(`<div class="project-rail-wrap"><div${attr_class("project-rail-scrollbar", void 0, { "hidden": true })} aria-hidden="true"><button type="button" class="project-rail-thumb"${attr_style(`width: ${thumbWidth}px; transform: translateX(${thumbLeft}px);`)} aria-label="레일 스크롤바 이동"></button></div> <div class="project-rail-spacer" aria-hidden="true"></div> <div class="rail"><!--[-->`);
			const each_array = ensure_array_like(projects);
			for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
				let project = each_array[$$index];
				ProjectCard($$renderer, { project });
			}
			$$renderer.push(`<!--]--></div></div>`);
		} else {
			$$renderer.push("<!--[-1-->");
			$$renderer.push(`<div class="empty-panel">${escape_html(emptyMessage)}</div>`);
		}
		$$renderer.push(`<!--]--></section>`);
	});
}
//#endregion
//#region routes/+page.svelte
function _page($$renderer, $$props) {
	$$renderer.component(($$renderer) => {
		let { data } = $$props;
		const snapshot = derived(() => data.snapshot);
		const filters = derived(() => data.filters ?? {
			search: "",
			tag: ""
		});
		const visiblePopularTags = derived(() => (snapshot().popular_tag_counts?.length ? snapshot().popular_tag_counts : snapshot().popular_tags.map((label) => ({
			label,
			count: 0
		}))).slice(0, 10));
		const selectedTagCount = derived(() => visiblePopularTags().find((tag) => tag.label === filters().tag)?.count ?? 0);
		let displayedProjectCount = 0;
		const homeGuideSteps = [
			[
				"01",
				"공유",
				"결과물과 제작 맥락을 모두와 공유합니다."
			],
			[
				"02",
				"피드백",
				"댓글과 반응으로 새로운 관점을 발견합니다."
			],
			[
				"03",
				"발전",
				"다양한 관점이 모여 인사이트를 개선합니다."
			]
		];
		const powerBiSteps = [
			[
				"PBIX",
				"업로드",
				"보고서 파일을 올립니다."
			],
			[
				"WEB",
				"웹 배포",
				"브라우저에서 열 수 있게 게시합니다."
			],
			[
				"LINK",
				"공유",
				"포트폴리오 링크로 전달합니다."
			]
		];
		const studySteps = [
			[
				"01",
				"실습",
				"Power BI 과제"
			],
			[
				"02",
				"웹 배포 및 피드백",
				"동료 리뷰 반영"
			],
			[
				"03",
				"완성",
				"포트폴리오 정리"
			]
		];
		const heroSlides = [
			{
				eyebrow: "Project Portfolio Platform",
				titleHtml: "AI 시대에는 <em>휴먼 인사이트</em>가 자산이다.",
				bodyHtml: "FOLIO는 좋은 시각화를 발견하고,<br>직접 경험하며 토론하고 함께 성장하는 커뮤니티입니다.",
				visual: "preview",
				cta: "내 프로젝트 등록하기",
				href: "/submit",
				target: "_self"
			},
			{
				eyebrow: "Collective Insight",
				titleHtml: "인사이트는 <em>공유할수록 깊어집니다.</em>",
				bodyHtml: "각자의 시각화 경험을 나누고,<br>댓글과 피드백으로 더 나은 관점을 만들어갑니다.",
				visual: "guide",
				cta: "내 프로젝트 등록하기",
				href: "/submit",
				target: "_self"
			},
			{
				eyebrow: "Power BI 무료 웹 게시",
				titleHtml: "Power BI 보고서를 <em>무료로 웹에 게시하세요.</em>",
				bodyHtml: "PBIX 파일을 간편하게 게시하고,<br>누구나 열어볼 수 있는 보고서 페이지로 프로젝트를 공유합니다.",
				visual: "powerbi",
				cta: "PBIX 보고서 무료 게시하기",
				href: "/submit",
				target: "_self"
			},
			{
				eyebrow: "Snowball Impact Study Club",
				titleHtml: "Power BI 데이터 시각화, <em>함께 공부해요.</em>",
				bodyHtml: "스터디 클럽에서 함께 실습하고,<br>보고서 디자인과 DAX, 경영정보시각화 실기를 토론하며 성장합니다.",
				visual: "study",
				cta: "스터디 클럽 참여하기",
				href: "https://discord.gg/vKb9SKA3k",
				target: "_blank"
			}
		];
		const heroTrackSlides = derived(() => [...heroSlides, heroSlides[0]]);
		head("qv4brr", $$renderer, ($$renderer) => {
			$$renderer.title(($$renderer) => {
				$$renderer.push(`<title>FOLIO</title>`);
			});
			$$renderer.push(`<meta name="description" content="좋은 데이터 시각화 프로젝트를 발견하고 직접 경험하는 FOLIO 공개 갤러리"/>`);
		});
		$$renderer.push(`<section class="home-hero-shell" aria-label="FOLIO 홈 소개"><div class="home-hero-viewport"><div class="home-hero-track"><!--[-->`);
		const each_array = ensure_array_like(heroTrackSlides());
		for (let $$index_3 = 0, $$length = each_array.length; $$index_3 < $$length; $$index_3++) {
			let slide = each_array[$$index_3];
			$$renderer.push(`<section${attr_class("home-hero-slide", void 0, { "home-guide-hero": slide.visual === "guide" })}><div class="home-copy"><div class="home-eyebrow">${escape_html(slide.eyebrow)}</div> <h1>${html(slide.titleHtml)}</h1> <p>${html(slide.bodyHtml)}</p> <div class="home-actions"><a class="home-primary-cta"${attr("href", slide.href)}${attr("target", slide.target)}${attr("rel", slide.target === "_blank" ? "noopener" : void 0)}>${escape_html(slide.cta)}</a></div></div> `);
			if (slide.visual === "preview") {
				$$renderer.push("<!--[0-->");
				$$renderer.push(`<div class="home-hero-preview"><img class="home-hero-preview-image" src="/hero-preview-home.jpg" alt="데이터 분석 대시보드와 인사이트 미리보기"/></div>`);
			} else if (slide.visual === "guide") {
				$$renderer.push("<!--[1-->");
				$$renderer.push(`<div class="home-guide-flow" aria-label="프로젝트 발전 단계"><!--[-->`);
				const each_array_1 = ensure_array_like(homeGuideSteps);
				for (let $$index = 0, $$length = each_array_1.length; $$index < $$length; $$index++) {
					let step = each_array_1[$$index];
					$$renderer.push(`<div class="home-guide-step"><div class="home-guide-node">${escape_html(step[0])}</div> <div class="home-guide-card"><strong>${escape_html(step[1])}</strong> <p>${escape_html(step[2])}</p></div></div>`);
				}
				$$renderer.push(`<!--]--></div>`);
			} else if (slide.visual === "powerbi") {
				$$renderer.push("<!--[2-->");
				$$renderer.push(`<div class="home-guide-flow home-powerbi-flow" aria-label="Power BI 웹 게시 단계"><!--[-->`);
				const each_array_2 = ensure_array_like(powerBiSteps);
				for (let $$index_1 = 0, $$length = each_array_2.length; $$index_1 < $$length; $$index_1++) {
					let step = each_array_2[$$index_1];
					$$renderer.push(`<div class="home-guide-step"><div class="home-guide-node">${escape_html(step[0])}</div> <div class="home-guide-card"><strong>${escape_html(step[1])}</strong> <p>${escape_html(step[2])}</p></div></div>`);
				}
				$$renderer.push(`<!--]--></div>`);
			} else {
				$$renderer.push("<!--[-1-->");
				$$renderer.push(`<div class="home-guide-flow home-study-flow" aria-label="Power BI 스터디 진행 단계"><!--[-->`);
				const each_array_3 = ensure_array_like(studySteps);
				for (let $$index_2 = 0, $$length = each_array_3.length; $$index_2 < $$length; $$index_2++) {
					let step = each_array_3[$$index_2];
					$$renderer.push(`<div class="home-guide-step"><div class="home-guide-node">${escape_html(step[0])}</div> <div class="home-guide-card"><strong>${escape_html(step[1])}</strong> <p>${escape_html(step[2])}</p></div></div>`);
				}
				$$renderer.push(`<!--]--></div>`);
			}
			$$renderer.push(`<!--]--></section>`);
		}
		$$renderer.push(`<!--]--></div></div> <div class="home-hero-dots" aria-hidden="true"><!--[-->`);
		const each_array_4 = ensure_array_like(heroSlides);
		for (let $$index_4 = 0, $$length = each_array_4.length; $$index_4 < $$length; $$index_4++) {
			each_array_4[$$index_4];
			$$renderer.push(`<span></span>`);
		}
		$$renderer.push(`<!--]--></div></section> `);
		if (data.error) {
			$$renderer.push("<!--[0-->");
			$$renderer.push(`<div class="notice">${escape_html(data.error)}</div>`);
		} else $$renderer.push("<!--[-1-->");
		$$renderer.push(`<!--]--> <section class="home-browse-panel" aria-label="홈 갤러리 검색과 태그 필터"><form method="GET" class="home-browse-form"><div class="home-search-heading"><h2><span>${escape_html(displayedProjectCount.toLocaleString("ko-KR"))}</span>개의 휴먼 인사이트 프로젝트가 FOLIO에 쌓이고 있어요.</h2></div> <div class="home-search-row"><input type="search" name="q"${attr("value", filters().search)} placeholder="프로젝트명, 태그, 작성자 검색" aria-label="프로젝트 검색"/> `);
		if (filters().tag) {
			$$renderer.push("<!--[0-->");
			$$renderer.push(`<input type="hidden" name="tag"${attr("value", filters().tag)}/>`);
		} else $$renderer.push("<!--[-1-->");
		$$renderer.push(`<!--]--> <button type="submit">검색</button></div></form> <div class="home-tag-row" aria-label="인기 태그 TOP10"><div class="home-tag-list"><a${attr("href", filters().search ? `/?q=${encodeURIComponent(filters().search)}` : "/")}${attr_class("", void 0, { "active": !filters().tag })}>전체</a> <!--[-->`);
		const each_array_5 = ensure_array_like(visiblePopularTags());
		for (let $$index_5 = 0, $$length = each_array_5.length; $$index_5 < $$length; $$index_5++) {
			let tag = each_array_5[$$index_5];
			$$renderer.push(`<a${attr("href", `/?${new URLSearchParams({
				...filters().search ? { q: filters().search } : {},
				tag: tag.label
			}).toString()}`)}${attr_class("", void 0, { "active": filters().tag === tag.label })}><span>${escape_html(tag.label)}</span> <small>${escape_html(tag.count.toLocaleString("ko-KR"))}</small></a>`);
		}
		$$renderer.push(`<!--]--></div> <div class="home-popular-tag-label">${escape_html(filters().tag ? `${filters().tag} ${selectedTagCount().toLocaleString("ko-KR")}개` : "인기 태그 TOP10")}</div></div></section> `);
		ProjectRail($$renderer, {
			title: "새로 공개된 프로젝트",
			description: "최근 등록된 Power BI 프로젝트를 먼저 살펴보세요.",
			projects: snapshot().recent_projects,
			emptyMessage: "아직 공개된 프로젝트가 없습니다. 첫 프로젝트를 등록해 갤러리를 열어보세요."
		});
		$$renderer.push(`<!----> `);
		ProjectRail($$renderer, {
			title: "조회수가 높은 프로젝트",
			description: "많이 열린 프로젝트를 빠르게 훑어보세요.",
			projects: snapshot().viewed_projects,
			emptyMessage: "조회수 순위는 프로젝트가 공개되면 자동으로 채워집니다."
		});
		$$renderer.push(`<!----> `);
		ProjectRail($$renderer, {
			title: "좋아요를 받은 프로젝트",
			description: "반응이 쌓인 프로젝트를 이어서 확인해보세요.",
			projects: snapshot().liked_projects,
			emptyMessage: "좋아요를 받은 프로젝트가 아직 없습니다. 좋은 시각화에 첫 반응을 남겨보세요."
		});
		$$renderer.push(`<!---->`);
	});
}
//#endregion
export { _page as default };
