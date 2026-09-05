import "../../../../chunks/index-server.js";
import { C as escape_html, a as ensure_array_like, i as derived, o as head, t as attr_class, x as attr } from "../../../../chunks/server.js";
import "../../../../chunks/supabase2.js";
import "../../../../chunks/auth.js";
import "../../../../chunks/projects.js";
import { t as page } from "../../../../chunks/state.js";
import "../../../../chunks/navigation.js";
import { n as formatDate, t as formatCount } from "../../../../chunks/format.js";
import { t as ProjectCard } from "../../../../chunks/ProjectCard.js";
import { t as ProjectRichContent } from "../../../../chunks/ProjectRichContent.js";
//#region lib/projectInput.ts
function normalizeOptionalUrl(value) {
	const rawValue = value.trim();
	if (!rawValue) return null;
	try {
		const url = new URL(rawValue);
		return ["http:", "https:"].includes(url.protocol) && url.hostname ? rawValue : null;
	} catch {
		return null;
	}
}
function normalizePowerBIEmbedUrl(value) {
	let rawValue = (value ?? "").trim();
	if (!rawValue) return null;
	if (rawValue.toLowerCase().startsWith("<iframe")) rawValue = rawValue.match(/\ssrc=["']([^"']+)["']/i)?.[1]?.trim() || rawValue;
	return normalizeOptionalUrl(rawValue);
}
//#endregion
//#region lib/components/ProjectComments.svelte
function ProjectComments($$renderer, $$props) {
	$$renderer.component(($$renderer) => {
		let { projectId, projectAuthorId, projectTitle, initialCommentCount } = $$props;
		let comments = [];
		let commentCount = 0;
		let currentPage = 1;
		const COMMENTS_PAGE_SIZE = 20;
		const totalPages = derived(() => Math.max(1, Math.ceil(comments.length / COMMENTS_PAGE_SIZE)));
		derived(() => comments.slice(0, 20));
		$$renderer.push(`<section id="project-comments" class="comments-panel"><div class="comments-heading"><h2>댓글 ${escape_html(commentCount)}개</h2> <p>프로젝트에 대한 의견이나 질문을 남겨보세요.</p></div> `);
		$$renderer.push("<!--[-1-->");
		$$renderer.push(`<!--]--> `);
		$$renderer.push("<!--[-1-->");
		$$renderer.push(`<!--]--> `);
		$$renderer.push("<!--[-1-->");
		$$renderer.push(`<div class="comments-login-note"><span>로그인 후 댓글을 작성할 수 있습니다.</span> <a${attr("href", `/login?next=/projects/${projectId}`)}>로그인하기</a></div>`);
		$$renderer.push(`<!--]--> <div class="comments-divider"></div> `);
		$$renderer.push("<!--[0-->");
		$$renderer.push(`<div class="comments-empty">댓글을 불러오는 중입니다.</div>`);
		$$renderer.push(`<!--]--> <div class="comments-pagination" aria-label="댓글 페이지 이동">`);
		if (totalPages() > 1) {
			$$renderer.push("<!--[0-->");
			$$renderer.push(`<button type="button"${attr("disabled", true, true)}>이전</button>`);
		} else $$renderer.push("<!--[-1-->");
		$$renderer.push(`<!--]--> <span class="comments-page-status">${escape_html(totalPages() <= 1 ? currentPage : `${currentPage} / ${totalPages()}`)}</span> `);
		if (totalPages() > 1) {
			$$renderer.push("<!--[0-->");
			$$renderer.push(`<button type="button"${attr("disabled", currentPage >= totalPages(), true)}>다음</button>`);
		} else $$renderer.push("<!--[-1-->");
		$$renderer.push(`<!--]--></div></section>`);
	});
}
//#endregion
//#region lib/components/ProjectLikeButton.svelte
function ProjectLikeButton($$renderer, $$props) {
	$$renderer.component(($$renderer) => {
		let { projectId, initialLikeCount } = $$props;
		$$renderer.push(`<div class="like-control"><button type="button"${attr("disabled", true, true)}${attr_class("", void 0, { "liked": false })}><span aria-hidden="true">${escape_html("♡")}</span> 좋아요 ${escape_html(formatCount(0))}</button> `);
		$$renderer.push("<!--[-1-->");
		$$renderer.push(`<!--]--></div>`);
	});
}
//#endregion
//#region routes/projects/[id]/+page.svelte
function _page($$renderer, $$props) {
	$$renderer.component(($$renderer) => {
		let { data } = $$props;
		const project = derived(() => data.project);
		let embedError = "";
		let shareLabel = "링크 복사";
		const reportSections = derived(() => [
			["문제 정의", project().problem],
			["사용 데이터", project().dataset],
			["분석 및 시각화", project().process],
			["주요 관찰 포인트", project().insights]
		].filter((section) => Boolean(section[1])));
		const dashboardUrl = derived(() => normalizePowerBIEmbedUrl(project().power_bi_url));
		const resourceActions = derived(() => [
			{
				label: "대시보드 열기 ↗",
				url: dashboardUrl()
			},
			{
				label: "보고서 보기 ↗",
				url: project().report_url
			},
			{
				label: "GitHub 보기 ↗",
				url: project().github_url
			}
		]);
		derived(() => project().status === "published" && project().project_type === "powerbi");
		const hasDashboardUrl = derived(() => Boolean(dashboardUrl()));
		const hasExternalResource = derived(() => Boolean(project().report_url || project().github_url));
		const canRenderDashboardFrame = derived(hasDashboardUrl);
		const hasVisualOutput = derived(() => true);
		const isTableauOutput = derived(() => project().platform_key === "tableau" || project().project_type === "tableau" || (dashboardUrl() ?? "").includes("public.tableau.com"));
		const isExternalOnlyOutput = derived(() => project().embed_status === "external_only" && !canRenderDashboardFrame());
		const isEmbedFailedOutput = derived(() => project().embed_status === "failed" || Boolean(embedError) || false);
		const backPlatform = derived(() => normalizeBackPlatform(page.url.searchParams.get("platform")));
		const fromReferences = derived(() => page.url.searchParams.get("from") === "references");
		const backHref = derived(() => fromReferences() ? `/references/${backPlatform()}` : "/");
		const backLabel = derived(() => fromReferences() ? "레퍼런스로 돌아가기" : "홈 갤러리로 돌아가기");
		const isThumbnailCapture = derived(() => page.url.searchParams.get("capture") === "thumbnail");
		function normalizeBackPlatform(platform) {
			return [
				"powerbi",
				"tableau",
				"datastudio",
				"streamlit"
			].includes(platform ?? "") ? platform : "powerbi";
		}
		head("1dc2p70", $$renderer, ($$renderer) => {
			$$renderer.title(($$renderer) => {
				$$renderer.push(`<title>${escape_html(project().title)} | FOLIO</title>`);
			});
			$$renderer.push(`<meta name="description"${attr("content", project().one_liner ?? project().title)}/>`);
		});
		if (!isThumbnailCapture()) {
			$$renderer.push("<!--[0-->");
			$$renderer.push(`<section class="detail-hero project-detail-image-hero"><div class="detail-hero-copy"><div class="detail-hero-eyebrow">프로젝트 상세</div> <h1>${escape_html(project().title)}</h1> <p>${escape_html(project().one_liner ?? "프로젝트 소개가 없습니다.")}</p></div> <div class="detail-card-preview">`);
			ProjectCard($$renderer, {
				project: project(),
				compact: true
			});
			$$renderer.push(`<!----></div></section>`);
		} else $$renderer.push("<!--[-1-->");
		$$renderer.push(`<!--]--> `);
		if (!isThumbnailCapture()) {
			$$renderer.push("<!--[0-->");
			$$renderer.push(`<section class="detail-footer-row" aria-label="프로젝트 메타 및 액션"><div class="detail-meta" aria-label="프로젝트 메타 정보"><span class="pill meta-line">작성자 ${escape_html(project().author.name ?? "작성자")}</span> `);
			if (project().author.organization) {
				$$renderer.push("<!--[0-->");
				$$renderer.push(`<span class="pill meta-line">소속 ${escape_html(project().author.organization)}</span>`);
			} else $$renderer.push("<!--[-1-->");
			$$renderer.push(`<!--]--> <span class="pill meta-line">등록일 ${escape_html(formatDate(project().created_at))}</span> <span class="pill metric-pill">조회 ${escape_html(formatCount(project().view_count))}</span> <span class="pill metric-pill">좋아요 ${escape_html(formatCount(project().like_count))}</span> <span class="pill metric-pill">댓글 ${escape_html(formatCount(project().comment_count))}</span> <span class="pill visibility-pill">${escape_html(project().is_public ? "공개" : "비공개")}</span></div> <div class="detail-action-bar"><div class="detail-action-group"><button type="button" class="button-link share-button" aria-label="공유 링크 복사"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M10 13a5 5 0 0 0 7.07 0l2.83-2.83a5 5 0 0 0-7.07-7.07L11.5 4.43"></path><path d="M14 11a5 5 0 0 0-7.07 0L4.1 13.83a5 5 0 0 0 7.07 7.07l1.33-1.33"></path></svg> <span>${escape_html(shareLabel)}</span></button> `);
			ProjectLikeButton($$renderer, {
				projectId: project().id,
				initialLikeCount: project().like_count
			});
			$$renderer.push(`<!----> `);
			$$renderer.push("<!--[-1-->");
			$$renderer.push(`<button type="button" class="button-link">신고</button>`);
			$$renderer.push(`<!--]--></div></div> `);
			$$renderer.push("<!--[-1-->");
			$$renderer.push(`<!--]--> `);
			$$renderer.push("<!--[-1-->");
			$$renderer.push(`<!--]--> `);
			$$renderer.push("<!--[-1-->");
			$$renderer.push(`<!--]--></section>`);
		} else $$renderer.push("<!--[-1-->");
		$$renderer.push(`<!--]--> `);
		if (hasVisualOutput()) {
			$$renderer.push("<!--[0-->");
			$$renderer.push(`<section id="project-output"${attr_class("visual-panel", void 0, {
				"thumbnail-capture-output": isThumbnailCapture(),
				"tableau-output": isTableauOutput(),
				"external-only-output": isExternalOnlyOutput(),
				"embed-failed-output": isEmbedFailedOutput() || project().status === "failed"
			})}>`);
			if (!isThumbnailCapture()) {
				$$renderer.push("<!--[0-->");
				$$renderer.push(`<div class="visual-panel-head"><h2>대표 결과물</h2></div>`);
			} else $$renderer.push("<!--[-1-->");
			$$renderer.push(`<!--]--> `);
			if (project().status === "processing") {
				$$renderer.push("<!--[0-->");
				$$renderer.push(`<div class="embed-empty embed-loading-state">Power BI 보고서를 게시하는 중입니다. 잠시 후 다시 확인하세요.</div>`);
			} else if (project().status === "failed") {
				$$renderer.push("<!--[1-->");
				$$renderer.push(`<div class="embed-empty embed-failed-state">Power BI 보고서 게시에 실패했습니다. 프로젝트 작성자는 마이페이지에서 상태를 확인하세요.</div>`);
			} else if (canRenderDashboardFrame() && dashboardUrl()) {
				$$renderer.push("<!--[4-->");
				$$renderer.push(`<iframe class="dashboard-frame"${attr("title", `${project().title} 대표 결과물`)}${attr("src", dashboardUrl())}></iframe> `);
				if (!isThumbnailCapture()) {
					$$renderer.push("<!--[0-->");
					$$renderer.push(`<p class="visual-caption">화면이 표시되지 않으면 원본 대시보드를 새 탭에서 확인하세요.</p>`);
				} else $$renderer.push("<!--[-1-->");
				$$renderer.push(`<!--]-->`);
			} else if (project().embed_status === "failed" || embedError) {
				$$renderer.push("<!--[5-->");
				$$renderer.push(`<div class="embed-empty embed-failed-state">${escape_html("Power BI 보고서를 불러오지 못했습니다. 프로젝트 작성자는 마이페이지에서 상태를 확인하세요.")}</div>`);
			} else if (hasExternalResource()) {
				$$renderer.push("<!--[6-->");
				$$renderer.push(`<div class="embed-empty embed-external-state">연결된 산출물을 새 탭에서 확인하세요.</div>`);
			} else {
				$$renderer.push("<!--[-1-->");
				$$renderer.push(`<div class="embed-empty">표시할 대시보드가 없습니다.</div>`);
			}
			$$renderer.push(`<!--]--> `);
			if (!isThumbnailCapture()) {
				$$renderer.push("<!--[0-->");
				$$renderer.push(`<div class="actions" aria-label="외부 산출물 링크"><!--[-->`);
				const each_array_1 = ensure_array_like(resourceActions());
				for (let $$index_1 = 0, $$length = each_array_1.length; $$index_1 < $$length; $$index_1++) {
					let action = each_array_1[$$index_1];
					if (action.url) {
						$$renderer.push("<!--[0-->");
						$$renderer.push(`<a class="button-link"${attr("href", action.url)} target="_blank" rel="noreferrer">${escape_html(action.label)}</a>`);
					} else {
						$$renderer.push("<!--[-1-->");
						$$renderer.push(`<button type="button" class="button-link" disabled="" aria-disabled="true">${escape_html(action.label)}</button>`);
					}
					$$renderer.push(`<!--]-->`);
				}
				$$renderer.push(`<!--]--></div>`);
			} else $$renderer.push("<!--[-1-->");
			$$renderer.push(`<!--]--></section>`);
		} else $$renderer.push("<!--[-1-->");
		$$renderer.push(`<!--]--> `);
		if (!isThumbnailCapture() && reportSections().length > 0) {
			$$renderer.push("<!--[0-->");
			$$renderer.push(`<article id="project-report" class="report"><div class="report-head"><h2>프로젝트 리포트</h2></div> <!--[-->`);
			const each_array_2 = ensure_array_like(reportSections());
			for (let $$index_2 = 0, $$length = each_array_2.length; $$index_2 < $$length; $$index_2++) {
				let [, body] = each_array_2[$$index_2];
				$$renderer.push(`<section class="report-section"><div class="report-section-content">`);
				ProjectRichContent($$renderer, {
					html: body,
					emptyMessage: "아직 작성된 프로젝트 설명이 없습니다."
				});
				$$renderer.push(`<!----></div></section>`);
			}
			$$renderer.push(`<!--]--></article>`);
		} else if (!isThumbnailCapture()) {
			$$renderer.push("<!--[1-->");
			$$renderer.push(`<div class="empty-panel">아직 작성된 프로젝트 설명이 없습니다.</div>`);
		} else $$renderer.push("<!--[-1-->");
		$$renderer.push(`<!--]--> `);
		if (!isThumbnailCapture()) {
			$$renderer.push("<!--[0-->");
			ProjectComments($$renderer, {
				projectId: project().id,
				projectAuthorId: project().author_id,
				projectTitle: project().title,
				initialCommentCount: project().comment_count
			});
			$$renderer.push(`<!----> <div class="detail-back-action-row"><a class="button-link"${attr("href", backHref())}>← ${escape_html(backLabel())}</a></div>`);
		} else $$renderer.push("<!--[-1-->");
		$$renderer.push(`<!--]-->`);
	});
}
//#endregion
export { _page as default };
