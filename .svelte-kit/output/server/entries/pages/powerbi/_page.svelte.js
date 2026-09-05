import { C as escape_html, a as ensure_array_like, i as derived, o as head, t as attr_class, x as attr } from "../../../chunks/server.js";
import { n as formatDate } from "../../../chunks/format.js";
//#region routes/powerbi/+page.svelte
function ContentCard($$renderer, item, variant) {
	$$renderer.push(`<a${attr_class("content-card", void 0, { "program": variant === "program" })}${attr("href", item.url)} target="_blank" rel="noreferrer">`);
	if (item.image_url) {
		$$renderer.push("<!--[0-->");
		$$renderer.push(`<img${attr("src", item.image_url)} alt="" loading="lazy"/>`);
	} else $$renderer.push("<!--[-1-->");
	$$renderer.push(`<!--]--> <span>${escape_html(item.source)} · ${escape_html(item.topic)}</span> <strong>${escape_html(item.title)}</strong> <em>${escape_html(item.summary)}</em></a>`);
}
function CommunityRow($$renderer, item) {
	$$renderer.push(`<article class="community-card"><div class="community-meta">${escape_html(formatDate(item.date))} · ${escape_html(item.source)}</div> <div class="community-title-row"><strong>${escape_html(item.title)}</strong> <a class="community-link"${attr("href", item.url)} target="_blank" rel="noreferrer">원문 보기</a></div> <div class="community-summary-row"><p>${escape_html(item.summary)}</p> <div class="content-tags" aria-label="분류"><span>${escape_html(item.topic)}</span></div></div></article>`);
}
function CertCard($$renderer, item) {
	$$renderer.push(`<a${attr_class("cert-card", void 0, {
		"pl300": item.source === "Microsoft Learn",
		"kcci": item.source === "KCCI"
	})}${attr("href", item.url)} target="_blank" rel="noreferrer"><div class="cert-logo" aria-hidden="true"><span>${escape_html(item.source === "Microsoft Learn" ? "Microsoft Certified" : "KCCI")}</span> <strong>${escape_html(item.source === "Microsoft Learn" ? "PL-300" : "BI Specialist")}</strong> <em>${escape_html(item.source === "Microsoft Learn" ? "Power BI Data Analyst" : "경영정보시각화능력")}</em></div> <div class="cert-name">${escape_html(item.title)}</div> <div class="cert-link">공식 페이지 바로가기</div></a>`);
}
function _page($$renderer, $$props) {
	$$renderer.component(($$renderer) => {
		let { data } = $$props;
		const NEWS_PAGE_SIZE = 10;
		const COMMUNITY_PAGE_SIZE = 10;
		let newsPageIndex = 0;
		let communityPageIndex = 0;
		const heroByTopic = {
			news: {
				eyebrow: "Power BI News",
				title: "Power BI 소식",
				body: "Power BI 분석가에게 필요한 Desktop 다운로드, 월간 기능 업데이트, 변경 로그를 원문 링크와 함께 모아 번역 및 요약합니다.",
				className: "powerbi-news-hero"
			},
			learning: {
				eyebrow: "Power BI Learning",
				title: "Power BI 학습 콘텐츠",
				body: "공식 채널과 실무 크리에이터의 Power BI 영상을 모아, DAX, 모델링, 시각화, Fabric 업데이트 흐름을 빠르게 살펴볼 수 있습니다.",
				className: "powerbi-learning-hero"
			},
			community: {
				eyebrow: "Power BI Community Blog",
				title: "Power BI 커뮤니티 소식",
				body: "Microsoft Fabric Community Blog의 최신 Power BI 글을 모아, 실무에 필요한 핵심만 한국어로 번역하고 요약합니다.",
				className: "powerbi-community-hero"
			},
			certifications: {
				eyebrow: "Power BI Certifications",
				title: "Power BI 자격증, 공식 경로로 바로 확인하세요.",
				body: "PL-300과 경영정보시각화능력은 Power BI 분석가의 역량을 보여줄 수 있는 대표 자격증입니다. 스터디 클럽에서 시험 준비와 포트폴리오 완성, 웹 배포 피드백까지 함께 이어갈 수 있습니다.",
				className: "powerbi-cert-hero"
			}
		};
		const hero = derived(() => heroByTopic[data.topic]);
		const newsTotalPages = derived(() => Math.max(Math.ceil(data.news.length / NEWS_PAGE_SIZE), 1));
		const visibleNews = derived(() => data.news.slice(0, 10));
		const communityTotalPages = derived(() => Math.max(Math.ceil(data.community.length / COMMUNITY_PAGE_SIZE), 1));
		const visibleCommunity = derived(() => data.community.slice(0, 10));
		head("pqok8w", $$renderer, ($$renderer) => {
			$$renderer.title(($$renderer) => {
				$$renderer.push(`<title>Power BI 콘텐츠 허브 | FOLIO</title>`);
			});
			$$renderer.push(`<meta name="description" content="Power BI 업데이트, 학습 콘텐츠, 커뮤니티 소식과 자격증 링크를 모아 봅니다."/>`);
		});
		$$renderer.push(`<section${attr_class(`powerbi-hero ${hero().className}`)}><div><div class="powerbi-eyebrow">${escape_html(hero().eyebrow)}</div> <div${attr_class("", void 0, { "powerbi-news-title-row": data.topic === "news" })}><h1>${escape_html(hero().title)}</h1> `);
		if (data.topic === "news" && data.desktop) {
			$$renderer.push("<!--[0-->");
			$$renderer.push(`<a class="powerbi-hero-cta compact"${attr("href", data.desktop.url)} target="_blank" rel="noreferrer">최신 Desktop 다운로드</a>`);
		} else $$renderer.push("<!--[-1-->");
		$$renderer.push(`<!--]--></div> <p>${escape_html(hero().body)}</p> `);
		if (data.topic === "certifications") {
			$$renderer.push("<!--[0-->");
			$$renderer.push(`<a class="powerbi-hero-cta" href="https://discord.gg/vKb9SKA3k" target="_blank" rel="noreferrer">스터디 클럽 참여하기</a>`);
		} else $$renderer.push("<!--[-1-->");
		$$renderer.push(`<!--]--></div> `);
		if (data.topic === "certifications") {
			$$renderer.push("<!--[0-->");
			$$renderer.push(`<div class="powerbi-cert-hero-visual" aria-label="Power BI 자격증"><img class="powerbi-cert-hero-badge" src="/cert-pl300.png" alt="Microsoft Certified Power BI Data Analyst Associate"/> <img class="powerbi-cert-hero-poster" src="/cert-bi-specialist.jpg" alt="경영정보시각화능력 BI Specialist"/></div>`);
		} else {
			$$renderer.push("<!--[-1-->");
			$$renderer.push(`<div class="powerbi-hero-visual"${attr("aria-label", hero().title)}><img src="/reference-powerbi-logo-cropped.webp" alt="Power BI"/></div>`);
		}
		$$renderer.push(`<!--]--></section> `);
		if (data.topic === "learning") {
			$$renderer.push("<!--[0-->");
			$$renderer.push(`<section class="learning-list">`);
			const each_array = ensure_array_like(data.learning);
			if (each_array.length !== 0) {
				$$renderer.push("<!--[-->");
				for (let index = 0, $$length = each_array.length; index < $$length; index++) {
					let group = each_array[index];
					$$renderer.push(`<details class="learning-section"${attr("open", index === 0, true)}><summary><span>${escape_html(group.category)}</span> <em>${escape_html(group.programs.length + group.videos.length)}개 콘텐츠</em></summary> <div class="content-grid"><!--[-->`);
					const each_array_1 = ensure_array_like(group.programs);
					for (let $$index = 0, $$length = each_array_1.length; $$index < $$length; $$index++) {
						let item = each_array_1[$$index];
						ContentCard($$renderer, item, "program");
					}
					$$renderer.push(`<!--]--> <!--[-->`);
					const each_array_2 = ensure_array_like(group.videos);
					for (let $$index_1 = 0, $$length = each_array_2.length; $$index_1 < $$length; $$index_1++) {
						let item = each_array_2[$$index_1];
						ContentCard($$renderer, item, "video");
					}
					$$renderer.push(`<!--]--></div></details>`);
				}
			} else {
				$$renderer.push("<!--[!-->");
				$$renderer.push(`<div class="empty-panel">아직 수집된 학습 콘텐츠가 없습니다.</div>`);
			}
			$$renderer.push(`<!--]--></section>`);
		} else if (data.topic === "community") {
			$$renderer.push("<!--[1-->");
			$$renderer.push(`<section class="content-list">`);
			const each_array_3 = ensure_array_like(visibleCommunity());
			if (each_array_3.length !== 0) {
				$$renderer.push("<!--[-->");
				for (let $$index_3 = 0, $$length = each_array_3.length; $$index_3 < $$length; $$index_3++) {
					let item = each_array_3[$$index_3];
					CommunityRow($$renderer, item);
				}
			} else {
				$$renderer.push("<!--[!-->");
				$$renderer.push(`<div class="empty-panel">아직 수집된 커뮤니티 소식이 없습니다.</div>`);
			}
			$$renderer.push(`<!--]--> `);
			if (data.community.length > COMMUNITY_PAGE_SIZE) {
				$$renderer.push("<!--[0-->");
				$$renderer.push(`<div class="news-pagination" aria-label="Power BI 커뮤니티 소식 페이지"><button type="button"${attr("disabled", true, true)} aria-label="이전 커뮤니티 소식">‹</button> <div class="news-page-indicator">${escape_html(1)} / ${escape_html(communityTotalPages())}</div> <button type="button"${attr("disabled", communityPageIndex >= communityTotalPages() - 1, true)} aria-label="다음 커뮤니티 소식">›</button></div>`);
			} else $$renderer.push("<!--[-1-->");
			$$renderer.push(`<!--]--></section>`);
		} else if (data.topic === "certifications") {
			$$renderer.push("<!--[2-->");
			$$renderer.push(`<section class="cert-grid"><!--[-->`);
			const each_array_4 = ensure_array_like(data.certifications);
			for (let $$index_4 = 0, $$length = each_array_4.length; $$index_4 < $$length; $$index_4++) {
				let item = each_array_4[$$index_4];
				CertCard($$renderer, item);
			}
			$$renderer.push(`<!--]--></section>`);
		} else {
			$$renderer.push("<!--[-1-->");
			$$renderer.push(`<section class="news-board">`);
			const each_array_5 = ensure_array_like(visibleNews());
			if (each_array_5.length !== 0) {
				$$renderer.push("<!--[-->");
				for (let index = 0, $$length = each_array_5.length; index < $$length; index++) {
					let item = each_array_5[index];
					$$renderer.push(`<details class="news-release-row"><summary><span class="news-row-index">${escape_html(data.news.length - (0 + index))}</span> <span class="news-row-label">${escape_html(item.label)}</span> <span class="news-expander-title">${escape_html(item.title)}</span> `);
					if (item.source_url) {
						$$renderer.push("<!--[0-->");
						$$renderer.push(`<a class="news-source-link"${attr("href", item.source_url)} target="_blank" rel="noreferrer">원문</a>`);
					} else $$renderer.push("<!--[-1-->");
					$$renderer.push(`<!--]--></summary> <div class="news-release-body">`);
					if (item.video) {
						$$renderer.push("<!--[0-->");
						$$renderer.push(`<a class="news-video-card"${attr("href", item.video.url)} target="_blank" rel="noreferrer"><span class="news-video-thumb">`);
						if (item.video.image_url) {
							$$renderer.push("<!--[0-->");
							$$renderer.push(`<img${attr("src", item.video.image_url)} alt="" loading="lazy"/>`);
						} else $$renderer.push("<!--[-1-->");
						$$renderer.push(`<!--]--></span> <span class="news-video-copy"><span>공식 업데이트 영상</span> <strong>${escape_html(item.video.title)}</strong></span> <span class="news-video-open">영상 보기</span></a>`);
					} else $$renderer.push("<!--[-1-->");
					$$renderer.push(`<!--]--> `);
					if (item.bullets.length > 0) {
						$$renderer.push("<!--[0-->");
						$$renderer.push(`<ul class="news-summary-list"><!--[-->`);
						const each_array_6 = ensure_array_like(item.bullets);
						for (let $$index_5 = 0, $$length = each_array_6.length; $$index_5 < $$length; $$index_5++) {
							let bullet = each_array_6[$$index_5];
							$$renderer.push(`<li>${escape_html(bullet)}</li>`);
						}
						$$renderer.push(`<!--]--></ul>`);
					} else $$renderer.push("<!--[-1-->");
					$$renderer.push(`<!--]--></div></details>`);
				}
			} else {
				$$renderer.push("<!--[!-->");
				$$renderer.push(`<div class="empty-panel">아직 수집된 Power BI 소식이 없습니다.</div>`);
			}
			$$renderer.push(`<!--]--> `);
			if (data.news.length > NEWS_PAGE_SIZE) {
				$$renderer.push("<!--[0-->");
				$$renderer.push(`<div class="news-pagination" aria-label="Power BI 소식 페이지"><button type="button"${attr("disabled", true, true)} aria-label="이전 소식">‹</button> <div class="news-page-indicator">${escape_html(1)} / ${escape_html(newsTotalPages())}</div> <button type="button"${attr("disabled", newsPageIndex >= newsTotalPages() - 1, true)} aria-label="다음 소식">›</button></div>`);
			} else $$renderer.push("<!--[-1-->");
			$$renderer.push(`<!--]--></section>`);
		}
		$$renderer.push(`<!--]-->`);
	});
}
//#endregion
export { _page as default };
