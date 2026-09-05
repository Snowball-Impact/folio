import { n as onDestroy } from "./index-server.js";
import { C as escape_html, S as clsx, a as ensure_array_like, i as derived, n as attr_style, r as bind_props, t as attr_class, x as attr } from "./server.js";
import { r as currentSession } from "./auth.js";
import "./projects.js";
import { t as ProjectCard } from "./ProjectCard.js";
import { t as ProjectRichContent } from "./ProjectRichContent.js";
//#region lib/components/RichEditorIcon.svelte
function RichEditorIcon($$renderer, $$props) {
	let { name } = $$props;
	$$renderer.push(`<svg class="editor-icon" viewBox="0 0 18 18" aria-hidden="true" focusable="false">`);
	if (name === "bold") {
		$$renderer.push("<!--[0-->");
		$$renderer.push(`<path d="M5 3.25h4.35c2.35 0 3.65 1.05 3.65 2.65 0 1.05-.62 1.88-1.72 2.25 1.55.3 2.35 1.25 2.35 2.62 0 1.95-1.52 3.23-4.12 3.23H5V3.25Zm2.25 1.82v2.44h1.83c1.05 0 1.62-.43 1.62-1.22 0-.8-.57-1.22-1.62-1.22H7.25Zm0 4.13v2.98h2.08c1.12 0 1.72-.52 1.72-1.49 0-.97-.6-1.49-1.72-1.49H7.25Z" fill="currentColor"></path>`);
	} else if (name === "italic") {
		$$renderer.push("<!--[1-->");
		$$renderer.push(`<path d="M10.9 3.25h2.25l-.35 1.8h-1.48l-1.92 7.6h1.48l-.45 1.8H5.95l.45-1.8h1.48l1.92-7.6H8.32l.45-1.8h2.13Z" fill="currentColor"></path>`);
	} else if (name === "underline") {
		$$renderer.push("<!--[2-->");
		$$renderer.push(`<path d="M5.1 3.25h2.15v4.48c0 1.68.63 2.55 1.75 2.55s1.75-.87 1.75-2.55V3.25h2.15v4.56c0 2.93-1.43 4.42-3.9 4.42S5.1 10.74 5.1 7.81V3.25Zm-.35 11.1h8v1.4h-8v-1.4Z" fill="currentColor"></path>`);
	} else if (name === "strike") {
		$$renderer.push("<!--[3-->");
		$$renderer.push(`<path d="M3.1 8.05h11.8v1.45H3.1V8.05Zm2.25-2.16c0-1.82 1.42-2.9 3.8-2.9 1.57 0 2.88.42 3.95 1.23l-.98 1.48c-.95-.63-1.9-.93-2.95-.93-1.02 0-1.58.36-1.58.97 0 .55.45.82 1.85 1.05l1.03.17c2.25.38 3.25 1.3 3.25 2.8 0 1.95-1.62 3.15-4.23 3.15-1.78 0-3.35-.5-4.4-1.4l1.02-1.5c.9.7 2.05 1.08 3.43 1.08 1.2 0 1.85-.4 1.85-1.1 0-.62-.5-.9-1.95-1.15l-1.02-.17c-2.08-.35-3.02-1.2-3.02-2.78Z" fill="currentColor"></path>`);
	} else if (name === "subscript") {
		$$renderer.push("<!--[4-->");
		$$renderer.push(`<path d="M2.9 4.2h2.2l1.8 2.2 1.8-2.2h2.2L8 8.3l2.9 3.5H8.7l-1.8-2.2-1.8 2.2H2.9l2.9-3.5-2.9-4.1Zm10.15 6.35h1.22c1.2 0 1.83.55 1.83 1.38 0 .62-.32 1.03-.98 1.43l-.75.46c-.2.13-.32.23-.38.35h2.14v1.08h-3.68c.03-.96.35-1.54 1.2-2.08l.67-.42c.38-.24.55-.42.55-.7 0-.3-.22-.45-.66-.45h-1.16v-1.05Z" fill="currentColor"></path>`);
	} else if (name === "superscript") {
		$$renderer.push("<!--[5-->");
		$$renderer.push(`<path d="M2.9 4.2h2.2l1.8 2.2 1.8-2.2h2.2L8 8.3l2.9 3.5H8.7l-1.8-2.2-1.8 2.2H2.9l2.9-3.5-2.9-4.1Zm10.22-1.25h1.22c1.2 0 1.83.55 1.83 1.38 0 .62-.32 1.03-.98 1.43l-.75.46c-.2.13-.32.23-.38.35h2.14v1.08h-3.68c.03-.96.35-1.54 1.2-2.08l.67-.42c.38-.24.55-.42.55-.7 0-.3-.22-.45-.66-.45h-1.16V2.95Z" fill="currentColor"></path>`);
	} else if (name === "ordered-list") {
		$$renderer.push("<!--[6-->");
		$$renderer.push(`<path d="M2.2 3.2h1.15v2.06h.72v.92H2.2v-.92h.48V4.2l-.48.22V3.65l.48-.2h-.48V3.2Zm0 4.3h1.35c.88 0 1.38.38 1.38 1.02 0 .34-.17.62-.48.82.42.16.65.48.65.9 0 .72-.58 1.12-1.56 1.12H2.2v-.92h1.15c.27 0 .4-.1.4-.28 0-.17-.13-.27-.4-.27H2.2v-.8h1.05c.22 0 .33-.08.33-.25 0-.15-.11-.23-.33-.23H2.2V7.5Zm0 4.3h2.84v.92l-1.55 1.36h1.59v.92H2.2v-.92l1.57-1.36H2.2v-.92Zm4.25-8.2h9.35v1.25H6.45V3.6Zm0 4.25h9.35V9.1H6.45V7.85Zm0 4.25h9.35v1.25H6.45V12.1Z" fill="currentColor"></path>`);
	} else if (name === "bullet-list") {
		$$renderer.push("<!--[7-->");
		$$renderer.push(`<path d="M2.4 3.6a1.1 1.1 0 1 1 0 2.2 1.1 1.1 0 0 1 0-2.2Zm0 4.3a1.1 1.1 0 1 1 0 2.2 1.1 1.1 0 0 1 0-2.2Zm0 4.3a1.1 1.1 0 1 1 0 2.2 1.1 1.1 0 0 1 0-2.2ZM5.2 4.08h10.4v1.24H5.2V4.08Zm0 4.3h10.4v1.24H5.2V8.38Zm0 4.3h10.4v1.24H5.2v-1.24Z" fill="currentColor"></path>`);
	} else if (name === "outdent" || name === "indent") {
		$$renderer.push("<!--[8-->");
		$$renderer.push(`<path d="M3.1 3.25h11.8v1.3H3.1v-1.3Zm0 5.1h11.8v1.3H3.1v-1.3Zm0 5.1h11.8v1.3H3.1v-1.3Z" fill="currentColor"></path>`);
		if (name === "outdent") {
			$$renderer.push("<!--[0-->");
			$$renderer.push(`<path d="m3.1 8.35 3.2-2.15v1.45h3.1v1.4H6.3v1.45L3.1 8.35Z" fill="currentColor"></path>`);
		} else {
			$$renderer.push("<!--[-1-->");
			$$renderer.push(`<path d="m14.9 8.35-3.2-2.15v1.45H8.6v1.4h3.1v1.45l3.2-2.15Z" fill="currentColor"></path>`);
		}
		$$renderer.push(`<!--]-->`);
	} else if (name === "align-left" || name === "align-center" || name === "align-right") {
		$$renderer.push("<!--[9-->");
		$$renderer.push(`<path d="M3 3.25h12v1.3H3v-1.3Zm0 5.1h12v1.3H3v-1.3Zm0 5.1h12v1.3H3v-1.3Z" fill="currentColor"></path>`);
		if (name === "align-center") {
			$$renderer.push("<!--[0-->");
			$$renderer.push(`<path d="M5 3.25h8v1.3H5v-1.3Zm-2 5.1h12v1.3H3v-1.3Zm2 5.1h8v1.3H5v-1.3Z" fill="currentColor"></path>`);
		} else if (name === "align-right") {
			$$renderer.push("<!--[1-->");
			$$renderer.push(`<path d="M7 3.25h8v1.3H7v-1.3ZM3 8.35h12v1.3H3v-1.3Zm4 5.1h8v1.3H7v-1.3Z" fill="currentColor"></path>`);
		} else $$renderer.push("<!--[-1-->");
		$$renderer.push(`<!--]-->`);
	} else if (name === "formula") {
		$$renderer.push("<!--[10-->");
		$$renderer.push(`<path d="M4.1 3.2h10v1.55H7.05l2.28 3.1-2.28 3.1h7.05v1.55h-10v-1.45l3.03-3.2-3.03-3.2V3.2Z" fill="currentColor"></path>`);
	} else if (name === "blockquote") {
		$$renderer.push("<!--[11-->");
		$$renderer.push(`<path d="M3.25 4.35h4.2v4.1c0 2.48-1.25 4.08-3.6 4.78l-.55-1.4c1.15-.43 1.75-1.1 1.9-2.05H3.25v-5.43Zm7.3 0h4.2v4.1c0 2.48-1.25 4.08-3.6 4.78l-.55-1.4c1.15-.43 1.75-1.1 1.9-2.05h-1.95v-5.43Z" fill="currentColor"></path>`);
	} else if (name === "code") {
		$$renderer.push("<!--[12-->");
		$$renderer.push(`<path d="m6.7 4.05-4 4.95 4 4.95 1.15-.95-3.22-4 3.22-4-1.15-.95Zm4.6 0-1.15.95 3.22 4-3.22 4 1.15.95 4-4.95-4-4.95Z" fill="currentColor"></path>`);
	} else if (name === "code-block") {
		$$renderer.push("<!--[13-->");
		$$renderer.push(`<path d="M2.75 3.25h12.5v11.5H2.75V3.25Zm1.5 1.5v8.5h9.5v-8.5h-9.5Zm3.35 1.7L5.1 8.95l2.5 2.5 1.05-1.05-1.45-1.45L8.65 7.5 7.6 6.45Zm3.25 0-1.05 1.05 1.45 1.45-1.45 1.45 1.05 1.05 2.5-2.5-2.5-2.5Z" fill="currentColor"></path>`);
	} else if (name === "rule") {
		$$renderer.push("<!--[14-->");
		$$renderer.push(`<path d="M2.75 8.05h12.5v1.9H2.75v-1.9Z" fill="currentColor"></path>`);
	} else if (name === "clear") {
		$$renderer.push("<!--[15-->");
		$$renderer.push(`<path d="m3.1 12.8 5.2-5.2-2.1-2.1 1.1-1.1 2.1 2.1 2.35-2.35 1.1 1.1L10.5 7.6l2.1 2.1-1.1 1.1-2.1-2.1-5.2 5.2H3.1v-1.1Zm0 1.8h11.8v1.15H3.1V14.6Z" fill="currentColor"></path>`);
	} else if (name === "link" || name === "unlink") {
		$$renderer.push("<!--[16-->");
		$$renderer.push(`<path d="M6.1 10.8 4.8 12.1a2.12 2.12 0 0 1-3-3l2.35-2.35a2.12 2.12 0 0 1 3-.02l.3.3-1.1 1.1-.3-.3a.57.57 0 0 0-.8 0L2.9 10.18a.57.57 0 0 0 .8.8L5 9.68l1.1 1.12Zm5.8-3.6 1.3-1.3a2.12 2.12 0 0 1 3 3l-2.35 2.35a2.12 2.12 0 0 1-3 .02l-.3-.3 1.1-1.1.3.3a.57.57 0 0 0 .8 0l2.35-2.35a.57.57 0 0 0-.8-.8L13 8.32l-1.1-1.12Z" fill="currentColor"></path><path d="M5.4 8.15h7.2v1.7H5.4v-1.7Z" fill="currentColor"></path>`);
		if (name === "unlink") {
			$$renderer.push("<!--[0-->");
			$$renderer.push(`<path d="m3.25 3.25 11.5 11.5-1 1-11.5-11.5 1-1Z" fill="currentColor"></path>`);
		} else $$renderer.push("<!--[-1-->");
		$$renderer.push(`<!--]-->`);
	} else if (name === "image" || name === "upload") {
		$$renderer.push("<!--[17-->");
		$$renderer.push(`<path d="M2.75 3.25h12.5v11.5H2.75V3.25Zm1.5 1.5v8.5h9.5v-8.5h-9.5Zm1.5 6.8 2.1-2.3 1.65 1.7 1.2-1.35 2.05 2.25H5.75Zm1.05-4.65a1.15 1.15 0 1 0 0 2.3 1.15 1.15 0 0 0 0-2.3Z" fill="currentColor"></path>`);
		if (name === "upload") {
			$$renderer.push("<!--[0-->");
			$$renderer.push(`<path d="M8.1 15.7V9.1H5.8L9 5.9l3.2 3.2H9.9v6.6H8.1Z" fill="currentColor"></path>`);
		} else $$renderer.push("<!--[-1-->");
		$$renderer.push(`<!--]-->`);
	} else if (name === "undo" || name === "redo") {
		$$renderer.push("<!--[18-->");
		$$renderer.push(`<path d="M8.05 4.1a5.2 5.2 0 1 1-4.65 7.55l1.35-.72A3.67 3.67 0 1 0 8.05 5.6H5.7l2.05 2.05-1.05 1.05L2.9 4.9l3.8-3.8 1.05 1.05L5.7 4.1h2.35Z" fill="currentColor"></path>`);
		if (name === "redo") {
			$$renderer.push("<!--[0-->");
			$$renderer.push(`<path d="M9.95 4.1H12.3l-2.05-2.05L11.3 1l3.8 3.8-3.8 3.8-1.05-1.05L12.3 5.6H9.95a3.67 3.67 0 1 0 3.3 5.33l1.35.72A5.2 5.2 0 1 1 9.95 4.1Z" fill="currentColor"></path>`);
		} else $$renderer.push("<!--[-1-->");
		$$renderer.push(`<!--]-->`);
	} else {
		$$renderer.push("<!--[-1-->");
		$$renderer.push(`<circle cx="9" cy="9" r="6" fill="none" stroke="currentColor" stroke-width="1.5"></circle>`);
	}
	$$renderer.push(`<!--]--></svg>`);
}
//#endregion
//#region lib/components/ProjectBodyEditor.svelte
function ProjectBodyEditor($$renderer, $$props) {
	$$renderer.component(($$renderer) => {
		let { value, onChange, onImageFile = () => void 0 } = $$props;
		let previewHtml = "";
		let blockFormat = "paragraph";
		onDestroy(() => {});
		function run(command) {
			return command();
		}
		function setBlockFormat(event) {
			blockFormat = event.currentTarget.value;
			run(() => {
				return false;
			});
		}
		$$renderer.push(`<div class="rich-editor-shell svelte-xu147b"><div class="rich-editor-toolbar svelte-xu147b" aria-label="본문 서식 도구"><div class="rich-editor-toolbar-group svelte-xu147b" aria-label="글자 서식"><button type="button" aria-label="굵게" title="굵게"${attr_class("svelte-xu147b", void 0, { "active": void 0 })}>`);
		RichEditorIcon($$renderer, { name: "bold" });
		$$renderer.push(`<!----></button> <button type="button" aria-label="기울임" title="기울임"${attr_class("svelte-xu147b", void 0, { "active": void 0 })}>`);
		RichEditorIcon($$renderer, { name: "italic" });
		$$renderer.push(`<!----></button> <button type="button" aria-label="밑줄" title="밑줄"${attr_class("svelte-xu147b", void 0, { "active": void 0 })}>`);
		RichEditorIcon($$renderer, { name: "underline" });
		$$renderer.push(`<!----></button></div> <div class="rich-editor-toolbar-group svelte-xu147b" aria-label="목록과 정렬"><button type="button" aria-label="번호 목록" title="번호 목록"${attr_class("svelte-xu147b", void 0, { "active": void 0 })}>`);
		RichEditorIcon($$renderer, { name: "ordered-list" });
		$$renderer.push(`<!----></button> <button type="button" aria-label="글머리 목록" title="글머리 목록"${attr_class("svelte-xu147b", void 0, { "active": void 0 })}>`);
		RichEditorIcon($$renderer, { name: "bullet-list" });
		$$renderer.push(`<!----></button> <button type="button" aria-label="왼쪽 정렬" title="왼쪽 정렬"${attr_class("svelte-xu147b", void 0, { "active": void 0 })}>`);
		RichEditorIcon($$renderer, { name: "align-left" });
		$$renderer.push(`<!----></button> <button type="button" aria-label="가운데 정렬" title="가운데 정렬"${attr_class("svelte-xu147b", void 0, { "active": void 0 })}>`);
		RichEditorIcon($$renderer, { name: "align-center" });
		$$renderer.push(`<!----></button> <button type="button" aria-label="오른쪽 정렬" title="오른쪽 정렬"${attr_class("svelte-xu147b", void 0, { "active": void 0 })}>`);
		RichEditorIcon($$renderer, { name: "align-right" });
		$$renderer.push(`<!----></button></div> <div class="rich-editor-toolbar-group svelte-xu147b" aria-label="문단 형식">`);
		$$renderer.select({
			class: "rich-editor-format-select",
			"aria-label": "문단 형식",
			value: blockFormat,
			onchange: setBlockFormat
		}, ($$renderer) => {
			$$renderer.option({ value: "paragraph" }, ($$renderer) => {
				$$renderer.push(`Normal`);
			});
			$$renderer.option({ value: "heading2" }, ($$renderer) => {
				$$renderer.push(`H2`);
			});
			$$renderer.option({ value: "heading3" }, ($$renderer) => {
				$$renderer.push(`H3`);
			});
		}, "svelte-xu147b");
		$$renderer.push(`</div> <div class="rich-editor-toolbar-group svelte-xu147b" aria-label="링크와 이미지"><button type="button" aria-label="링크" title="링크"${attr_class("svelte-xu147b", void 0, { "active": void 0 })}>`);
		RichEditorIcon($$renderer, { name: "link" });
		$$renderer.push(`<!----></button> <button type="button" aria-label="이미지 파일 업로드" title="이미지 파일 업로드" class="svelte-xu147b">`);
		RichEditorIcon($$renderer, { name: "upload" });
		$$renderer.push(`<!----></button> <button type="button" aria-label="되돌리기" title="되돌리기" class="svelte-xu147b">`);
		RichEditorIcon($$renderer, { name: "undo" });
		$$renderer.push(`<!----></button> <button type="button" aria-label="다시 실행" title="다시 실행" class="svelte-xu147b">`);
		RichEditorIcon($$renderer, { name: "redo" });
		$$renderer.push(`<!----></button></div></div> <input data-body-image-input="" type="file" accept="image/jpeg,image/png,image/webp" hidden=""/> <div class="rich-editor svelte-xu147b" aria-label="프로젝트 본문 편집기"></div> <details class="rich-editor-preview svelte-xu147b"><summary class="svelte-xu147b">본문 미리보기</summary> <div class="rich-editor-preview-content svelte-xu147b">`);
		ProjectRichContent($$renderer, {
			html: previewHtml,
			allowLocalImages: true
		});
		$$renderer.push(`<!----></div></details></div>`);
	});
}
//#endregion
//#region lib/components/ProjectHeroThumbnailPreview.svelte
function ProjectHeroThumbnailPreview($$renderer, $$props) {
	let { project } = $$props;
	$$renderer.push(`<div class="hero-thumbnail-preview" aria-label="프로젝트 카드 미리보기">`);
	ProjectCard($$renderer, {
		project,
		compact: true,
		preview: true
	});
	$$renderer.push(`<!----></div>`);
}
//#endregion
//#region lib/projectForm.ts
var PROJECT_PLATFORM_OPTIONS = [
	{
		key: "other",
		label: "기타"
	},
	{
		key: "tableau",
		label: "Tableau"
	},
	{
		key: "powerbi",
		label: "Power BI"
	},
	{
		key: "datastudio",
		label: "Data Studio"
	},
	{
		key: "streamlit",
		label: "Streamlit"
	}
];
function emptyProjectSubmitInput() {
	return {
		title: "",
		one_liner: "",
		tags: "",
		platform: "other",
		problem: "",
		dataset: "",
		process: "",
		insights: "",
		power_bi_url: "",
		report_url: "",
		github_url: "",
		thumbnail_url: "",
		thumbnail_mode: "auto_cover",
		delete_thumbnail: false,
		delete_pbix: false,
		is_public: true
	};
}
function projectInputFromProject(value) {
	return {
		title: value.title,
		one_liner: value.one_liner ?? "",
		tags: value.tags.join(", "),
		platform: value.platform_key ?? "other",
		problem: value.problem ?? "",
		dataset: value.dataset ?? "",
		process: value.process ?? "",
		insights: value.insights ?? "",
		power_bi_url: value.power_bi_url ?? "",
		report_url: value.report_url ?? "",
		github_url: value.github_url ?? "",
		thumbnail_url: value.thumbnail_url ?? "",
		thumbnail_mode: value.thumbnail_mode,
		delete_thumbnail: false,
		delete_pbix: false,
		is_public: value.is_public
	};
}
function previewTags(tags, platform) {
	const rawTags = tags.replaceAll("#", "").split(",").map((tag) => tag.trim()).filter(Boolean);
	const uniqueTags = [...new Set(rawTags)];
	if (platform === "other") return uniqueTags.slice(0, 5);
	const platformLabel = PROJECT_PLATFORM_OPTIONS.find((option) => option.key === platform)?.label ?? "";
	const platformAliases = new Set([
		platformLabel,
		platform,
		platform === "datastudio" ? "Data Studio" : "",
		platform === "datastudio" ? "Looker Studio" : "",
		platform === "powerbi" ? "PowerBI" : "",
		platform === "powerbi" ? "Power BI" : ""
	].filter(Boolean).map(normalizeProjectTag));
	return [platformLabel, ...uniqueTags.filter((tag) => !platformAliases.has(normalizeProjectTag(tag)))].slice(0, 5);
}
function projectFormTagLabel(tags, platform) {
	const rawTags = tags.replaceAll("#", "").split(",").map((tag) => tag.trim()).filter(Boolean);
	const platformOption = PROJECT_PLATFORM_OPTIONS.find((option) => option.key === platform);
	const platformTag = platformOption?.key === "other" ? "" : platformOption?.label ?? "";
	const platformAliases = new Set([
		platformOption?.label ?? "",
		platformOption?.key ?? "",
		platform === "datastudio" ? "Data Studio" : "",
		platform === "datastudio" ? "Looker Studio" : "",
		platform === "powerbi" ? "PowerBI" : "",
		platform === "powerbi" ? "Power BI" : ""
	].filter(Boolean).map(normalizeProjectTag));
	const visibleTags = [platformTag, ...rawTags.filter((tag) => !platformAliases.has(normalizeProjectTag(tag)))].filter(Boolean).filter((tag, index, values) => values.findIndex((value) => normalizeProjectTag(value) === normalizeProjectTag(tag)) === index).slice(0, 5);
	return visibleTags.length ? `태그 ${visibleTags.map((tag) => `#${tag}`).join(" ")}` : "태그";
}
function normalizeProjectTag(value) {
	return value.trim().toLowerCase().replaceAll(" ", "");
}
//#endregion
//#region lib/components/ProjectFormOverview.svelte
function ProjectFormOverview($$renderer, $$props) {
	$$renderer.component(($$renderer) => {
		let { input = void 0, platformOptions, onSelectThumbnail, onSelectPbix, hasPowerbiReport = false, hasExistingThumbnail = false } = $$props;
		const tagLabel = derived(() => projectFormTagLabel(input.tags, input.platform));
		$$renderer.push(`<section class="project-form-section project-form-overview-section"><div class="project-form-overview-grid"><div class="project-form-overview-column"><header class="project-form-section-heading"><h2>기본 정보</h2> <p>프로젝트를 한눈에 이해할 수 있는 정보를 입력하세요.</p></header> <label><span class="field-label-row"><span>프로젝트명 *</span><button class="field-help" type="button" title="홈 갤러리 카드 제목 영역에 맞춰 최대 48자까지 입력할 수 있습니다." aria-label="프로젝트명 도움말">?</button></span> <input${attr("value", input.title)} maxlength="48" placeholder="예: 서울시 청년 취업 데이터 분석"/></label> <label><span class="field-label-row"><span>프로젝트 한 줄 소개</span><button class="field-help" type="button" title="홈 갤러리 카드 요약 영역에 맞춰 최대 56자까지 입력할 수 있습니다." aria-label="프로젝트 한 줄 소개 도움말">?</button></span> <input${attr("value", input.one_liner)} maxlength="56" placeholder="핵심 메시지를 한 문장으로 적어주세요."/></label> <label><span class="field-label-row"><span>${escape_html(tagLabel())}</span><button class="field-help" type="button" title="#은 자동으로 제거되고 쉼표 기준으로 최대 5개까지 저장됩니다." aria-label="태그 도움말">?</button></span> <input${attr("value", input.tags)} placeholder="공공데이터, 시각화, 취업"/></label> <div class="platform-panel"><fieldset class="choice-panel"><legend>플랫폼</legend> <div class="segmented-options overview-radio-options"><!--[-->`);
		const each_array = ensure_array_like(platformOptions);
		for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
			let option = each_array[$$index];
			$$renderer.push(`<label><input type="radio"${attr("checked", input.platform === option.key, true)}${attr("value", option.key)}/> <span>${escape_html(option.label)}</span></label>`);
		}
		$$renderer.push(`<!--]--></div></fieldset> `);
		if (input.platform === "powerbi") {
			$$renderer.push("<!--[0-->");
			if (hasPowerbiReport) {
				$$renderer.push("<!--[0-->");
				$$renderer.push(`<label class="delete-option-row"><input type="checkbox"${attr("checked", input.delete_pbix, true)}/> <span>기존 Power BI 게시본 연결 삭제</span></label>`);
			} else $$renderer.push("<!--[-1-->");
			$$renderer.push(`<!--]--> `);
			if (!hasPowerbiReport || input.delete_pbix) {
				$$renderer.push("<!--[0-->");
				$$renderer.push(`<div class="overview-file-field pbix-upload-field"><label><span>PBIX 파일 업로드</span> <input type="file" accept=".pbix"/> <small>Cloudflare MVP 기본 최대 50MB / 파일 · PBIX</small></label> <p class="pbix-upload-warning">개인정보, 사내 데이터, 비공개 고객 정보가 포함된 PBIX는 업로드하지 마세요.</p></div>`);
			} else $$renderer.push("<!--[-1-->");
			$$renderer.push(`<!--]-->`);
		} else $$renderer.push("<!--[-1-->");
		$$renderer.push(`<!--]--></div></div> <div class="project-form-overview-column project-form-resource-column"><header class="project-form-section-heading"><h2>산출물 링크</h2> <p>공개 프로젝트에서 연결할 외부 산출물을 입력하세요.</p></header> <label><span class="field-label-row"><span>Embed Code</span><button class="field-help" type="button" title="iframe 코드 전체 또는 https URL을 입력할 수 있습니다." aria-label="Embed Code 도움말">?</button></span> <input${attr("value", input.power_bi_url)} placeholder="https://... 또는 iframe 코드"/></label> <label><span class="field-label-row"><span>GitHub URL</span><button class="field-help" type="button" title="http:// 또는 https://로 시작하는 주소를 입력하세요." aria-label="GitHub URL 도움말">?</button></span> <input${attr("value", input.github_url)} placeholder="https://github.com/..."/></label> <label><span class="field-label-row"><span>Web App URL</span><button class="field-help" type="button" title="http:// 또는 https://로 시작하는 주소를 입력하세요." aria-label="Web App URL 도움말">?</button></span> <input${attr("value", input.report_url)} placeholder="https://..."/></label> <div class="thumbnail-panel"><fieldset class="choice-panel thumbnail-choice-panel"><legend>썸네일 설정</legend> <div class="segmented-options overview-radio-options thumbnail-options"><label><input type="radio"${attr("checked", input.thumbnail_mode === "auto_cover", true)} value="auto_cover"/> <span>기본 커버</span></label> <label><input type="radio"${attr("checked", input.thumbnail_mode === "upload", true)} value="upload"/> <span>이미지 업로드</span></label> <label><input type="radio"${attr("checked", input.thumbnail_mode === "manual_url", true)} value="manual_url"/> <span>썸네일 CDN URL</span></label> <label><input type="radio"${attr("checked", input.thumbnail_mode === "capture", true)} value="capture"/> <span>임베드 대시보드 화면 자동 캡처</span></label></div></fieldset> `);
		if (hasExistingThumbnail) {
			$$renderer.push("<!--[0-->");
			$$renderer.push(`<label class="delete-option-row"><input type="checkbox"${attr("checked", input.delete_thumbnail, true)}/> <span>${escape_html(input.thumbnail_mode === "capture" ? "기존 캡처본 삭제 후 재캡처" : "기존 썸네일 삭제")}</span></label>`);
		} else $$renderer.push("<!--[-1-->");
		$$renderer.push(`<!--]--> `);
		if (input.thumbnail_mode === "upload" && (!hasExistingThumbnail || input.delete_thumbnail)) {
			$$renderer.push("<!--[0-->");
			$$renderer.push(`<label class="overview-file-field"><span>썸네일 이미지</span> <input type="file" accept="image/jpeg,image/png,image/webp"/> <small>최대 5MB / 파일 · JPG, PNG, WebP</small></label>`);
		} else $$renderer.push("<!--[-1-->");
		$$renderer.push(`<!--]--> `);
		if (input.thumbnail_mode === "manual_url") {
			$$renderer.push("<!--[0-->");
			$$renderer.push(`<label><span>썸네일 CDN URL</span> <input${attr("value", input.thumbnail_url)} placeholder="https://..."/></label>`);
		} else $$renderer.push("<!--[-1-->");
		$$renderer.push(`<!--]--> `);
		if (input.thumbnail_mode === "capture") {
			$$renderer.push("<!--[0-->");
			$$renderer.push(`<small>입력한 산출물 화면을 캡처해 프로젝트 대표 이미지로 사용합니다.</small>`);
		} else $$renderer.push("<!--[-1-->");
		$$renderer.push(`<!--]--></div></div></div></section>`);
		bind_props($$props, { input });
	});
}
//#endregion
//#region lib/components/OperationProgress.svelte
function OperationProgress($$renderer, $$props) {
	$$renderer.component(($$renderer) => {
		let { title = "작업 진행", progress = 0, steps = [], dismissLabel = "닫기", onDismiss } = $$props;
		const boundedProgress = derived(() => Math.max(0, Math.min(100, Math.round(progress))));
		const activeStep = derived(() => steps.find((step) => step.status === "error") ?? steps.find((step) => step.status === "active") ?? steps.at(-1));
		const canDismiss = derived(() => Boolean(onDismiss) && (boundedProgress() >= 100 || steps.some((step) => step.status === "error")));
		const actionLabel = derived(() => boundedProgress() >= 100 && !steps.some((step) => step.status === "error") ? "완료" : dismissLabel);
		let now = Date.now();
		let activeStepStartedAt = Date.now();
		const activeEstimateSeconds = derived(() => activeStep()?.status === "active" && activeStep().estimatedSeconds ? Math.max(activeStep().estimatedSeconds, 1) : 0);
		const elapsedSeconds = derived(() => Math.max(0, Math.floor((now - activeStepStartedAt) / 1e3)));
		const remainingSeconds = derived(() => Math.max(0, activeEstimateSeconds() - elapsedSeconds()));
		const timeEstimateText = derived(() => activeEstimateSeconds() ? remainingSeconds() > 0 ? `예상 남은 시간 약 ${formatDuration(remainingSeconds())} · 경과 ${formatDuration(elapsedSeconds())}` : `예상 대기 시간을 넘겼지만 계속 처리 중입니다. 경과 ${formatDuration(elapsedSeconds())}` : "");
		function formatDuration(totalSeconds) {
			const seconds = Math.max(0, Math.round(totalSeconds));
			if (seconds < 60) return `${seconds}초`;
			const minutes = Math.floor(seconds / 60);
			const remainder = seconds % 60;
			return remainder ? `${minutes}분 ${remainder}초` : `${minutes}분`;
		}
		if (steps.length > 0) {
			$$renderer.push("<!--[0-->");
			$$renderer.push(`<div class="operation-progress-layer" role="presentation"><div class="operation-progress-panel" role="dialog" aria-modal="true" aria-live="polite"${attr("aria-label", title)}><header><strong>${escape_html(title)}</strong> <span>${escape_html(boundedProgress())}%</span></header> <div class="operation-progress-track" role="progressbar" aria-valuemin="0" aria-valuemax="100"${attr("aria-valuenow", boundedProgress())}${attr("aria-valuetext", activeStep()?.detail ?? activeStep()?.label)}><div${attr_style(`width: ${boundedProgress()}%`)}></div></div> `);
			if (activeStep()) {
				$$renderer.push("<!--[0-->");
				$$renderer.push(`<p>${escape_html(activeStep().detail ?? activeStep().label)}</p>`);
			} else $$renderer.push("<!--[-1-->");
			$$renderer.push(`<!--]--> `);
			if (timeEstimateText()) {
				$$renderer.push("<!--[0-->");
				$$renderer.push(`<div class="operation-progress-estimate">${escape_html(timeEstimateText())}</div>`);
			} else $$renderer.push("<!--[-1-->");
			$$renderer.push(`<!--]--> <ol><!--[-->`);
			const each_array = ensure_array_like(steps);
			for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
				let step = each_array[$$index];
				$$renderer.push(`<li${attr_class(clsx(step.status))}><span></span> <em>${escape_html(step.label)}</em></li>`);
			}
			$$renderer.push(`<!--]--></ol> `);
			if (canDismiss()) {
				$$renderer.push("<!--[0-->");
				$$renderer.push(`<div class="operation-progress-actions"><button type="button">${escape_html(actionLabel())}</button></div>`);
			} else $$renderer.push("<!--[-1-->");
			$$renderer.push(`<!--]--></div></div>`);
		} else $$renderer.push("<!--[-1-->");
		$$renderer.push(`<!--]-->`);
	});
}
//#endregion
//#region lib/clientRuntimeConfig.ts
function publicConfigSeconds(name, fallbackSeconds) {
	const value = Number({
		"BASE_URL": "/",
		"DEV": false,
		"MODE": "production",
		"PROD": true,
		"PUBLIC_BODY_IMAGE_UPLOAD_TIMEOUT_SECONDS": "10",
		"PUBLIC_PBIX_PUBLISH_TIMEOUT_SECONDS": "30",
		"PUBLIC_SUPABASE_PUBLISHABLE_KEY": "sb_publishable_so5bInU80pmX1chi5Fi33A_ZWK3L3Hp",
		"PUBLIC_SUPABASE_URL": "https://vfvcpxrmirlnsfdjuaaz.supabase.co",
		"PUBLIC_THUMBNAIL_CAPTURE_TIMEOUT_SECONDS": "30",
		"PUBLIC_THUMBNAIL_UPLOAD_TIMEOUT_SECONDS": "10",
		"SSR": true
	}[name]);
	return Number.isFinite(value) && value > 0 ? value : fallbackSeconds;
}
function publicConfigMilliseconds(name, fallbackSeconds) {
	return publicConfigSeconds(name, fallbackSeconds) * 1e3;
}
publicConfigMilliseconds("PUBLIC_PBIX_PUBLISH_TIMEOUT_SECONDS", 30);
async function projectPbixExists(projectId) {
	const session = await currentSession();
	if (!session) return false;
	const response = await fetch(`/api/projects/${projectId}/powerbi-publish`, {
		method: "GET",
		headers: { Authorization: `Bearer ${session.access_token}` }
	});
	if (!response.ok) return false;
	const payload = await response.json().catch(() => ({}));
	return Boolean(payload.exists);
}
publicConfigMilliseconds("PUBLIC_THUMBNAIL_UPLOAD_TIMEOUT_SECONDS", 10);
publicConfigMilliseconds("PUBLIC_THUMBNAIL_CAPTURE_TIMEOUT_SECONDS", 30);
publicConfigMilliseconds("PUBLIC_THUMBNAIL_DELETE_TIMEOUT_SECONDS", 30);
publicConfigMilliseconds("PUBLIC_BODY_IMAGE_UPLOAD_TIMEOUT_SECONDS", 10);
publicConfigSeconds("PUBLIC_BODY_IMAGE_UPLOAD_TIMEOUT_SECONDS", 10);
publicConfigSeconds("PUBLIC_THUMBNAIL_UPLOAD_TIMEOUT_SECONDS", 10);
publicConfigSeconds("PUBLIC_PBIX_PUBLISH_TIMEOUT_SECONDS", 30);
publicConfigSeconds("PUBLIC_THUMBNAIL_CAPTURE_TIMEOUT_SECONDS", 30);
//#endregion
//#region lib/projectBody.ts
var PROJECT_BODY_TEMPLATE = `<h2>문제 정의</h2>
<p>이 프로젝트는 [대상/상황]에서 발생하는 [문제]를 다룹니다. 이를 분석한 이유는 [의사결정/개선 목표]를 더 명확히 하기 위해서입니다.</p>
<p><span style="color: rgb(138, 152, 173);">예시: 이 프로젝트는 청년 구직자가 교육 수료 후 취업까지 이어지는 과정에서 발생하는 이탈 문제를 다룹니다. 이를 분석한 이유는 어떤 요인이 취업 성과에 영향을 주는지 확인하기 위해서입니다.</span></p>
<h2>사용 데이터</h2>
<p>사용한 데이터는 [출처]의 [기간/범위] 데이터입니다. 주요 변수는 [변수1], [변수2], [변수3]이며, 핵심 지표는 [지표]입니다.</p>
<p><span style="color: rgb(138, 152, 173);">예시: 사용한 데이터는 교육 운영 시스템의 2025년 수강생 데이터입니다. 주요 변수는 수강 과정, 출석률, 과제 제출 여부이며, 핵심 지표는 수료율과 취업 연계율입니다.</span></p>
<h2>분석 과정</h2>
<p>먼저 [기준]으로 데이터를 나누어 비교했습니다. 이후 [분석 방법]을 통해 [패턴/차이]를 확인하고, [판단 기준]을 중심으로 결과를 해석했습니다.</p>
<p><span style="color: rgb(138, 152, 173);">예시: 먼저 과정별로 수료율과 취업 연계율을 비교했습니다. 이후 출석률 구간에 따라 성과 차이를 확인하고, 수료 여부와 취업 여부의 관계를 중심으로 결과를 해석했습니다.</span></p>
<h2>핵심 인사이트</h2>
<p>분석 결과 [핵심 발견]을 확인했습니다. 따라서 [대상/조직]은 [추천 행동]을 우선 검토할 필요가 있습니다.</p>
<p><span style="color: rgb(138, 152, 173);">예시: 분석 결과 출석률이 높은 수강생일수록 수료와 취업 연계 가능성이 함께 높아지는 경향을 확인했습니다. 따라서 교육 운영팀은 중도 이탈 위험이 높은 수강생을 조기에 발견하고 개입하는 방안을 우선 검토할 필요가 있습니다.</span></p>`;
var SECTION_TITLES = [
	["problem", "문제 정의"],
	["dataset", "사용 데이터"],
	["process", "분석 과정"],
	["insights", "핵심 인사이트"]
];
function projectBodyFromSections(sections) {
	if (!SECTION_TITLES.some(([key]) => plainTextFromHtml(sections[key]).trim())) return PROJECT_BODY_TEMPLATE;
	return SECTION_TITLES.map(([key, title]) => `<h2>${title}</h2>${formatBodyValue(sections[key])}`).join("");
}
function parseProjectBody(body) {
	const html = body.trim();
	const sections = {
		problem: "",
		dataset: "",
		process: "",
		insights: ""
	};
	if (!html) return sections;
	const root = new DOMParser().parseFromString(`<div>${html}</div>`, "text/html").body.firstElementChild;
	if (!root) {
		sections.problem = html;
		return sections;
	}
	let currentKey = null;
	let foundHeading = false;
	for (const node of Array.from(root.childNodes)) {
		if (node.nodeType === Node.ELEMENT_NODE) {
			const headingKey = headingSectionKey(node);
			if (headingKey) {
				currentKey = headingKey;
				foundHeading = true;
				continue;
			}
		}
		if (currentKey) sections[currentKey] += nodeToHtml(node);
	}
	if (!foundHeading && plainTextFromHtml(html)) sections.problem = html;
	return sections;
}
function plainTextFromHtml(value) {
	return value.replace(/<[^>]*>/g, " ").replace(/&nbsp;/g, " ").replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&quot;/g, "\"").replace(/&#39;/g, "'").replace(/\s+/g, " ").trim();
}
function headingSectionKey(element) {
	if (element.tagName.toLowerCase() !== "h2") return null;
	const heading = element.textContent?.trim() ?? "";
	if (heading === "문제 정의") return "problem";
	if (heading === "사용 데이터") return "dataset";
	if (heading === "분석 과정" || heading === "분석 및 시각화") return "process";
	if (heading === "핵심 인사이트" || heading === "주요 관찰 포인트") return "insights";
	return null;
}
function nodeToHtml(node) {
	if (node.nodeType === Node.TEXT_NODE) return node.textContent?.trim() ? `<p>${escapeHtml(node.textContent)}</p>` : "";
	if (node.nodeType === Node.ELEMENT_NODE) return node.outerHTML;
	return "";
}
function formatBodyValue(value) {
	const text = value?.trim() ?? "";
	if (!text) return "<p></p>";
	if (text.includes("<") && text.includes(">")) return text;
	return text.split(/\r?\n/).map((line) => line.trim()).filter(Boolean).map((line) => `<p>${escapeHtml(line)}</p>`).join("");
}
function escapeHtml(value) {
	return String(value ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#39;");
}
//#endregion
export { OperationProgress as a, emptyProjectSubmitInput as c, ProjectHeroThumbnailPreview as d, ProjectBodyEditor as f, projectPbixExists as i, previewTags as l, parseProjectBody as n, ProjectFormOverview as o, projectBodyFromSections as r, PROJECT_PLATFORM_OPTIONS as s, PROJECT_BODY_TEMPLATE as t, projectInputFromProject as u };
