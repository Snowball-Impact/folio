//#region lib/format.ts
function formatCount(value) {
	return new Intl.NumberFormat("ko-KR").format(Number(value ?? 0));
}
function formatDate(value) {
	if (!value) return "정보 없음";
	return value.slice(0, 10);
}
function formatDateTime(value) {
	if (!value) return "정보 없음";
	const parsed = new Date(value);
	if (Number.isNaN(parsed.getTime())) return value.replace("T", " ").slice(0, 16);
	const parts = new Intl.DateTimeFormat("sv-SE", {
		year: "numeric",
		month: "2-digit",
		day: "2-digit",
		hour: "2-digit",
		minute: "2-digit",
		hourCycle: "h23"
	}).formatToParts(parsed);
	const values = Object.fromEntries(parts.map((part) => [part.type, part.value]));
	return `${values.year}-${values.month}-${values.day} ${values.hour}:${values.minute}`;
}
var PROJECT_HTML_ALLOWED_TAGS = /* @__PURE__ */ new Set([
	"a",
	"b",
	"blockquote",
	"br",
	"code",
	"div",
	"em",
	"h2",
	"h3",
	"h4",
	"h5",
	"h6",
	"hr",
	"h1",
	"img",
	"i",
	"li",
	"mark",
	"ol",
	"p",
	"pre",
	"s",
	"span",
	"sub",
	"sup",
	"strong",
	"u",
	"ul"
]);
function sanitizeProjectHtml(value, options = {}) {
	const raw = String(value ?? "").trim();
	if (!raw) return "";
	return (/<[a-z][\s\S]*>/i.test(raw) ? raw : plainTextToParagraphHtml(raw)).replace(/[\s\S]*?-->/g, "").replace(/<\s*(script|style|iframe|object|embed|form|input|button|svg|math|meta|link)[\s\S]*?<\s*\/\s*\1\s*>/gi, "").replace(/<\s*(script|style|iframe|object|embed|form|input|button|svg|math|meta|link)[^>]*\/?>/gi, "").replace(/<\/?([a-zA-Z0-9-]+)([^>]*)>/g, (match, tagName, attrs) => {
		const tag = String(tagName).toLowerCase();
		if (!PROJECT_HTML_ALLOWED_TAGS.has(tag)) return "";
		if (match.startsWith("</")) return `</${tag}>`;
		if (tag === "img") {
			const src = safeImageSrc(String(attrs ?? ""), options.allowLocalImages === true);
			if (!src) return "";
			const alt = safeAttribute(String(attrs ?? ""), "alt");
			return `<img src="${escapeHtml(src)}"${alt ? ` alt="${escapeHtml(alt)}"` : ""}>`;
		}
		if (tag === "div" || tag === "span" && isMathNode(String(attrs ?? ""))) {
			const type = mathNodeType(String(attrs ?? ""));
			const latex = safeAttribute(String(attrs ?? ""), "data-latex");
			return type && latex ? `<${tag} data-type="${type}" data-latex="${escapeHtml(latex)}">` : "";
		}
		if (tag === "a") {
			const href = safeHref(String(attrs ?? ""));
			return href ? `<a href="${escapeHtml(href)}" target="_blank" rel="noreferrer">` : "<a>";
		}
		if (tag === "span") return `<span${safeSpanStyle(String(attrs ?? ""))}>`;
		if (tag === "mark") return `<mark${safeMarkStyle(String(attrs ?? ""))}>`;
		if (tag === "p" || /^h[1-6]$/.test(tag)) {
			const indent = safeIndent(String(attrs ?? ""));
			return `<${tag}${indent ? ` data-indent="${indent}" style="margin-left: ${indent * 24}px"` : ""}>`;
		}
		return `<${tag}>`;
	});
}
function safeSpanStyle(attrs) {
	const styleMatch = attrs.match(/\bstyle\s*=\s*(?:"([^"]*)"|'([^']*)')/i);
	const style = (styleMatch?.[1] ?? styleMatch?.[2] ?? "").trim();
	const color = style.match(/(?:^|;)\s*color\s*:\s*(#[0-9a-f]{3,8}|rgba?\([^)]*\))\s*(?:;|$)/i)?.[1] ?? "";
	const styles = isSafeCssColor(color) ? [`color: ${color}`] : [];
	const family = (style.match(/(?:^|;)\s*font-family\s*:\s*([^;]+)\s*(?:;|$)/i)?.[1] ?? "").replace(/["']/g, "").trim().toLowerCase();
	if (family === "sans-serif" || family === "serif" || family === "monospace") styles.push(`font-family: ${family}`);
	const sizeMatch = style.match(/(?:^|;)\s*font-size\s*:\s*(0\.75em|1\.5em|2\.5em)\s*(?:;|$)/i);
	if (sizeMatch?.[1]) styles.push(`font-size: ${sizeMatch[1]}`);
	return styles.length ? ` style="${escapeHtml(styles.join("; "))}"` : "";
}
function safeIndent(attrs) {
	const dataIndent = safeAttribute(attrs, "data-indent");
	const classIndent = attrs.match(/(?:^|\s)class\s*=\s*["'][^"']*\bql-indent-([1-6])\b[^"']*["']/i)?.[1] ?? "";
	const indent = Number(dataIndent || classIndent);
	return Number.isInteger(indent) && indent >= 1 && indent <= 6 ? indent : 0;
}
function safeImageSrc(attrs, allowLocalImages = false) {
	const src = safeAttribute(attrs, "src").trim();
	if (/^https?:\/\/[^\s]+$/i.test(src)) return src;
	return allowLocalImages && /^blob:https?:\/\/[^\s]+$/i.test(src) ? src : "";
}
function safeAttribute(attrs, name) {
	const expression = new RegExp(`\\b${name}\\s*=\\s*(?:"([^"]*)"|'([^']*)'|([^\\s>]+))`, "i");
	const match = attrs.match(expression);
	return (match?.[1] ?? match?.[2] ?? match?.[3] ?? "").trim();
}
function isMathNode(attrs) {
	return Boolean(mathNodeType(attrs));
}
function mathNodeType(attrs) {
	const type = safeAttribute(attrs, "data-type");
	return type === "inline-math" || type === "block-math" ? type : "";
}
function safeMarkStyle(attrs) {
	const styleMatch = attrs.match(/\bstyle\s*=\s*(?:"([^"]*)"|'([^']*)')/i);
	const background = (styleMatch?.[1] ?? styleMatch?.[2] ?? "").trim().match(/(?:^|;)\s*background-color\s*:\s*(#[0-9a-f]{3,8}|rgba?\([^)]*\))\s*(?:;|$)/i)?.[1] ?? "";
	return isSafeCssColor(background) ? ` style="background-color: ${escapeHtml(background)}"` : "";
}
function isSafeCssColor(value) {
	return /^#[0-9a-f]{3,8}$/i.test(value) || /^rgba?\(\s*[\d.]+%?\s*,\s*[\d.]+%?\s*,\s*[\d.]+%?(?:\s*,\s*[\d.]+%?)?\s*\)$/i.test(value);
}
function plainTextToParagraphHtml(value) {
	return value.split(/\r?\n/).map((line) => line.trim()).filter(Boolean).map((line) => `<p>${escapeHtml(line)}</p>`).join("");
}
function safeHref(attrs) {
	const match = attrs.match(/\bhref\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+))/i);
	const href = (match?.[1] ?? match?.[2] ?? match?.[3] ?? "").trim();
	if (/^(https?:|mailto:)/i.test(href)) return href;
	return "";
}
function escapeHtml(value) {
	return value.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#39;");
}
//#endregion
export { sanitizeProjectHtml as i, formatDate as n, formatDateTime as r, formatCount as t };
