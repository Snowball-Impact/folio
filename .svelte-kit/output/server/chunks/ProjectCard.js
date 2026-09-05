import { C as escape_html, a as ensure_array_like, i as derived, t as attr_class, x as attr } from "./server.js";
import { n as formatDate, t as formatCount } from "./format.js";
//#region lib/cover.ts
var ROUND_CONSTANTS = [
	1116352408,
	1899447441,
	3049323471,
	3921009573,
	961987163,
	1508970993,
	2453635748,
	2870763221,
	3624381080,
	310598401,
	607225278,
	1426881987,
	1925078388,
	2162078206,
	2614888103,
	3248222580,
	3835390401,
	4022224774,
	264347078,
	604807628,
	770255983,
	1249150122,
	1555081692,
	1996064986,
	2554220882,
	2821834349,
	2952996808,
	3210313671,
	3336571891,
	3584528711,
	113926993,
	338241895,
	666307205,
	773529912,
	1294757372,
	1396182291,
	1695183700,
	1986661051,
	2177026350,
	2456956037,
	2730485921,
	2820302411,
	3259730800,
	3345764771,
	3516065817,
	3600352804,
	4094571909,
	275423344,
	430227734,
	506948616,
	659060556,
	883997877,
	958139571,
	1322822218,
	1537002063,
	1747873779,
	1955562222,
	2024104815,
	2227730452,
	2361852424,
	2428436474,
	2756734187,
	3204031479,
	3329325298
];
var INITIAL_HASH = [
	1779033703,
	3144134277,
	1013904242,
	2773480762,
	1359893119,
	2600822924,
	528734635,
	1541459225
];
function rotateRight(value, bits) {
	return value >>> bits | value << 32 - bits;
}
function sha256(bytes) {
	const bitLength = bytes.length * 8;
	const paddedLength = Math.ceil((bytes.length + 9) / 64) * 64;
	const padded = new Uint8Array(paddedLength);
	padded.set(bytes);
	padded[bytes.length] = 128;
	const lengthOffset = padded.length - 8;
	for (let index = 0; index < 8; index += 1) padded[lengthOffset + index] = Math.floor(bitLength / 2 ** (56 - index * 8)) & 255;
	const hash = new Uint32Array(INITIAL_HASH);
	const schedule = /* @__PURE__ */ new Uint32Array(64);
	for (let offset = 0; offset < padded.length; offset += 64) {
		for (let index = 0; index < 16; index += 1) {
			const position = offset + index * 4;
			schedule[index] = padded[position] << 24 | padded[position + 1] << 16 | padded[position + 2] << 8 | padded[position + 3];
		}
		for (let index = 16; index < 64; index += 1) {
			const value = schedule[index - 15];
			const smallSigma0 = rotateRight(value, 7) ^ rotateRight(value, 18) ^ value >>> 3;
			const previous = schedule[index - 2];
			const smallSigma1 = rotateRight(previous, 17) ^ rotateRight(previous, 19) ^ previous >>> 10;
			schedule[index] = schedule[index - 16] + smallSigma0 + schedule[index - 7] + smallSigma1 >>> 0;
		}
		let [a, b, c, d, e, f, g, h] = hash;
		for (let index = 0; index < 64; index += 1) {
			const bigSigma1 = rotateRight(e, 6) ^ rotateRight(e, 11) ^ rotateRight(e, 25);
			const choice = e & f ^ ~e & g;
			const temporary1 = h + bigSigma1 + choice + ROUND_CONSTANTS[index] + schedule[index] >>> 0;
			const temporary2 = (rotateRight(a, 2) ^ rotateRight(a, 13) ^ rotateRight(a, 22)) + (a & b ^ a & c ^ b & c) >>> 0;
			[h, g, f, e, d, c, b, a] = [
				g,
				f,
				e,
				d + temporary1 >>> 0,
				c,
				b,
				a,
				temporary1 + temporary2 >>> 0
			];
		}
		hash[0] = hash[0] + a >>> 0;
		hash[1] = hash[1] + b >>> 0;
		hash[2] = hash[2] + c >>> 0;
		hash[3] = hash[3] + d >>> 0;
		hash[4] = hash[4] + e >>> 0;
		hash[5] = hash[5] + f >>> 0;
		hash[6] = hash[6] + g >>> 0;
		hash[7] = hash[7] + h >>> 0;
	}
	const digest = /* @__PURE__ */ new Uint8Array(32);
	hash.forEach((value, index) => {
		digest[index * 4] = value >>> 24;
		digest[index * 4 + 1] = value >>> 16;
		digest[index * 4 + 2] = value >>> 8;
		digest[index * 4 + 3] = value;
	});
	return digest;
}
function projectCoverVariant(project, variantCount = 24) {
	const seed = String(project.id || project.title || "folio");
	const digest = sha256(new TextEncoder().encode(seed));
	return (digest[0] << 8 | digest[1]) % variantCount;
}
//#endregion
//#region lib/components/ProjectCard.svelte
function ProjectCard($$renderer, $$props) {
	$$renderer.component(($$renderer) => {
		let { project, compact = false, preview = false } = $$props;
		const visibleTags = derived(() => project.tags.slice(0, 4));
		const extraTagCount = derived(() => Math.max(project.tags.length - visibleTags().length, 0));
		const coverVariant = derived(() => projectCoverVariant(project));
		const hasThumbnail = derived(() => Boolean(project.thumbnail_url));
		const showIconMetrics = derived(() => compact || preview);
		const activityLabel = derived(() => preview ? "" : projectActivityLabel(project));
		function projectActivityLabel(project) {
			const now = Date.now();
			const recentWindow = 6048e5;
			const createdAt = Date.parse(project.created_at);
			if (Number.isFinite(createdAt) && createdAt <= now && now - createdAt <= recentWindow) return "NEW";
			const latestCommentAt = Date.parse(project.latest_comment_at ?? "");
			return Number.isFinite(latestCommentAt) && latestCommentAt <= now && now - latestCommentAt <= recentWindow ? "댓글 NEW" : "";
		}
		function CardContent($$renderer) {
			if (activityLabel()) {
				$$renderer.push("<!--[0-->");
				$$renderer.push(`<span class="card-activity-badge"${attr("aria-label", activityLabel())}${attr("title", activityLabel())}>${escape_html(activityLabel())}</span>`);
			} else $$renderer.push("<!--[-1-->");
			$$renderer.push(`<!--]--> <div class="card-cover">`);
			if (project.thumbnail_url) {
				$$renderer.push("<!--[0-->");
				$$renderer.push(`<img${attr("src", project.thumbnail_url)}${attr("alt", `${project.title} 대표 이미지`)} loading="lazy"/>`);
			} else {
				$$renderer.push("<!--[-1-->");
				$$renderer.push(`<div${attr_class(`folio-auto-cover folio-auto-cover-${coverVariant()}`)} aria-hidden="true"><div class="folio-auto-cover-pattern"></div></div>`);
			}
			$$renderer.push(`<!--]--></div> <div class="card-body"><h3 class="card-title">${escape_html(project.title)}</h3> <p class="card-summary">${escape_html(project.one_liner ?? "프로젝트 소개가 없습니다.")}</p> <div class="tags card-tags" aria-label="태그"><!--[-->`);
			const each_array = ensure_array_like(visibleTags());
			for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
				let tag = each_array[$$index];
				$$renderer.push(`<span class="tag">#${escape_html(tag)}</span>`);
			}
			$$renderer.push(`<!--]--> `);
			if (extraTagCount() > 0) {
				$$renderer.push("<!--[0-->");
				$$renderer.push(`<span class="tag">+${escape_html(extraTagCount())}</span>`);
			} else $$renderer.push("<!--[-1-->");
			$$renderer.push(`<!--]--></div> <div class="card-footer"><div class="card-footer-meta">`);
			if (preview) {
				$$renderer.push("<!--[0-->");
				$$renderer.push(`<span class="card-preview-author">${escape_html(project.author.name ?? "작성자")}</span>`);
			} else {
				$$renderer.push("<!--[-1-->");
				$$renderer.push(`<span>${escape_html(formatDate(project.created_at))}</span> <span>${escape_html(project.author.name ?? "작성자")}${escape_html(project.author.organization ? ` · ${project.author.organization}` : "")}</span>`);
			}
			$$renderer.push(`<!--]--></div> <div class="card-meta card-meta-bottom">`);
			if (showIconMetrics()) {
				$$renderer.push("<!--[0-->");
				$$renderer.push(`<span title="조회수"${attr("aria-label", `조회수 ${formatCount(project.view_count)}`)}><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M2.5 12s3.5-6 9.5-6 9.5 6 9.5 6-3.5 6-9.5 6-9.5-6-9.5-6Z"></path><circle cx="12" cy="12" r="2.7"></circle></svg> ${escape_html(formatCount(project.view_count))}</span> <span title="좋아요"${attr("aria-label", `좋아요 ${formatCount(project.like_count)}`)}><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20.8 4.8a5.5 5.5 0 0 0-7.8 0L12 5.9l-1.1-1.1a5.5 5.5 0 0 0-7.8 7.8L12 21l8.8-8.4a5.5 5.5 0 0 0 0-7.8Z"></path></svg> ${escape_html(formatCount(project.like_count))}</span> <span title="댓글"${attr("aria-label", `댓글 ${formatCount(project.comment_count)}`)}><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M21 15a4 4 0 0 1-4 4H8l-5 3V7a4 4 0 0 1 4-4h10a4 4 0 0 1 4 4Z"></path></svg> ${escape_html(formatCount(project.comment_count))}</span>`);
			} else {
				$$renderer.push("<!--[-1-->");
				$$renderer.push(`<span>조회 ${escape_html(formatCount(project.view_count))}</span> <span>좋아요 ${escape_html(formatCount(project.like_count))}</span> <span>댓글 ${escape_html(formatCount(project.comment_count))}</span>`);
			}
			$$renderer.push(`<!--]--></div></div></div>`);
		}
		if (preview) {
			$$renderer.push("<!--[0-->");
			$$renderer.push(`<div${attr_class("project-card", void 0, {
				"has-thumbnail": hasThumbnail(),
				"compact": compact,
				"preview": preview
			})}${attr("aria-label", `${project.title} 미리보기`)}>`);
			CardContent($$renderer);
			$$renderer.push(`<!----></div>`);
		} else {
			$$renderer.push("<!--[-1-->");
			$$renderer.push(`<a${attr_class("project-card", void 0, {
				"has-thumbnail": hasThumbnail(),
				"compact": compact
			})}${attr("href", `/projects/${project.id}`)}${attr("aria-label", `${project.title} 상세 보기`)}>`);
			CardContent($$renderer);
			$$renderer.push(`<!----></a>`);
		}
		$$renderer.push(`<!--]-->`);
	});
}
//#endregion
export { ProjectCard as t };
