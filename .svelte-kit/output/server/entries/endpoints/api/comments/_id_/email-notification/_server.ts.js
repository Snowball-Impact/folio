import { t as private_env } from "../../../../../../chunks/shared-server.js";
import { n as authenticateBearerRequest, t as authFailureResponse } from "../../../../../../chunks/request-auth.js";
import { json } from "@sveltejs/kit";
//#region lib/server/email.ts
var DEFAULT_SMTP_TIMEOUT_MS = 8e3;
function isEmailConfigured() {
	return Boolean(private_env.SMTP_HOST && private_env.SMTP_FROM_EMAIL);
}
async function sendProjectCommentEmail(input) {
	if (!isEmailConfigured()) return {
		ok: true,
		skipped: true,
		message: "이메일 알림 설정이 없어 발송을 건너뜁니다."
	};
	const recipientEmail = input.recipient.email?.trim();
	if (!recipientEmail) return {
		ok: false,
		skipped: false,
		message: "수신자 이메일을 찾지 못했습니다."
	};
	const projectTitle = input.project.title?.trim() || "프로젝트";
	const actorName = input.actor?.name?.trim() || "사용자";
	const commentPreview = (input.comment.body || "").trim().slice(0, 240);
	const subject = `[FOLIO] ${projectTitle}에 새 댓글이 남겨졌습니다.`;
	const projectUrl = `${appUrl().replace(/\/$/, "")}/projects/${encodeURIComponent(input.project.id)}`;
	await sendSmtpMessage(recipientEmail, buildMessage({
		to: recipientEmail,
		subject,
		text: [
			`${projectTitle}에 새 댓글이 남겨졌습니다.`,
			"",
			`작성자: ${actorName}`,
			`댓글: ${commentPreview}`,
			"",
			`프로젝트 보기: ${projectUrl}`
		].join("\n"),
		html: [
			`<p><strong>${escapeHtml(projectTitle)}</strong>에 새 댓글이 남겨졌습니다.</p>`,
			`<p><strong>작성자</strong>: ${escapeHtml(actorName)}</p>`,
			`<p>${escapeHtml(commentPreview)}</p>`,
			`<p><a href="${escapeHtml(projectUrl)}">프로젝트 보기</a></p>`
		].join("\n")
	}));
	return {
		ok: true,
		skipped: false,
		message: "이메일 알림을 발송했습니다."
	};
}
async function sendSmtpMessage(to, message) {
	const host = private_env.SMTP_HOST?.trim();
	if (!host) throw new Error("SMTP host is missing.");
	const port = Number(private_env.SMTP_PORT || 587);
	const from = private_env.SMTP_FROM_EMAIL?.trim();
	if (!from) throw new Error("SMTP from email is missing.");
	const { connect } = await loadCloudflareSockets();
	let session = createSmtpSession(connect({
		hostname: host,
		port
	}, { secureTransport: shouldUseDirectTls(port) ? "on" : shouldUseStartTls(port) ? "starttls" : "off" }));
	try {
		await withTimeout(session.socket.opened, "SMTP connect");
		await session.reader.expect(void 0, "SMTP greeting");
		await command(session, `EHLO ${smtpClientName()}`, void 0, "SMTP EHLO");
		if (shouldUseStartTls(port)) {
			await command(session, "STARTTLS", void 0, "SMTP STARTTLS");
			session.reader.releaseLock();
			session.writer.releaseLock();
			session = createSmtpSession(session.socket.startTls());
			await withTimeout(session.socket.opened, "SMTP TLS connect");
			await command(session, `EHLO ${smtpClientName()}`, void 0, "SMTP TLS EHLO");
			await authenticate(session);
			await sendEnvelope(session, from, to, message);
			return;
		}
		await authenticate(session);
		await sendEnvelope(session, from, to, message);
	} finally {
		session.reader.releaseLock();
		session.writer.releaseLock();
		await session.socket.close().catch(() => void 0);
	}
}
async function loadCloudflareSockets() {
	return await import(
		/* @vite-ignore */
		"cloudflare:sockets"
);
}
async function sendEnvelope(session, from, to, message) {
	await command(session, `MAIL FROM:<${from}>`, void 0, "SMTP MAIL FROM");
	await command(session, `RCPT TO:<${to}>`, void 0, "SMTP RCPT TO");
	await command(session, "DATA", 354, "SMTP DATA");
	await writeSmtp(session, `${message}\r\n.\r\n`, "SMTP message write");
	await session.reader.expect(void 0, "SMTP message body");
	await command(session, "QUIT", 221, "SMTP QUIT");
}
async function authenticate(session) {
	const username = private_env.SMTP_USERNAME?.trim();
	const password = private_env.SMTP_PASSWORD ?? "";
	if (!username && !password) return;
	await command(session, `AUTH PLAIN ${Buffer.from(`\0${username}\0${password}`).toString("base64")}`, 235, "SMTP AUTH");
}
function createSmtpSession(socket) {
	return {
		socket,
		reader: smtpReader(socket.readable.getReader()),
		writer: socket.writable.getWriter()
	};
}
function smtpReader(reader) {
	let buffer = "";
	const decoder = new TextDecoder();
	return {
		async expect(expectedCode, label = "SMTP command") {
			while (true) {
				const lines = buffer.split(/\r?\n/).filter(Boolean);
				const match = (lines.at(-1) ?? "").match(/^(\d{3})\s/);
				if (match) {
					buffer = "";
					const code = Number(match[1]);
					const response = sanitizeSmtpResponse(lines.join("\n"));
					if (expectedCode && code !== expectedCode) throw new Error(`${label} expected ${expectedCode}, got ${code}: ${response}`);
					if (!expectedCode && code >= 400) throw new Error(`${label} failed with ${code}: ${response}`);
					return lines.join("\n");
				}
				const result = await withTimeout(reader.read(), label);
				if (result.done) throw new Error(`${label} ended before SMTP response.`);
				buffer += decoder.decode(result.value, { stream: true });
			}
		},
		releaseLock() {
			reader.releaseLock();
		}
	};
}
async function command(session, value, expectedCode, label) {
	await writeSmtp(session, `${value}\r\n`, `${label ?? "SMTP command"} write`);
	return session.reader.expect(expectedCode, label);
}
async function writeSmtp(session, value, label) {
	await withTimeout(session.writer.write(new TextEncoder().encode(value)), label);
}
function buildMessage({ to, subject, text, html }) {
	const boundary = `folio-${Date.now().toString(36)}`;
	const fromEmail = private_env.SMTP_FROM_EMAIL?.trim() || "";
	return [
		`From: ${encodedHeader(private_env.SMTP_FROM_NAME?.trim() || "FOLIO")} <${fromEmail}>`,
		`To: <${to}>`,
		`Subject: ${encodedHeader(subject)}`,
		"MIME-Version: 1.0",
		`Content-Type: multipart/alternative; boundary="${boundary}"`,
		"",
		`--${boundary}`,
		"Content-Type: text/plain; charset=UTF-8",
		"Content-Transfer-Encoding: 8bit",
		"",
		text,
		`--${boundary}`,
		"Content-Type: text/html; charset=UTF-8",
		"Content-Transfer-Encoding: 8bit",
		"",
		html,
		`--${boundary}--`
	].join("\r\n");
}
function encodedHeader(value) {
	return `=?UTF-8?B?${Buffer.from(value).toString("base64")}?=`;
}
function shouldUseStartTls(port) {
	return private_env.SMTP_USE_TLS !== "false" && port !== 465;
}
function shouldUseDirectTls(port) {
	return private_env.SMTP_USE_TLS !== "false" && port === 465;
}
function smtpClientName() {
	return (private_env.APP_URL || "localhost").replace(/^https?:\/\//, "").replace(/[:/].*$/, "") || "localhost";
}
function appUrl() {
	return private_env.APP_URL || "http://localhost:5173";
}
function smtpTimeoutMs() {
	const configured = Number(private_env.SMTP_TIMEOUT_MS || DEFAULT_SMTP_TIMEOUT_MS);
	return Number.isFinite(configured) && configured > 0 ? configured : DEFAULT_SMTP_TIMEOUT_MS;
}
function sanitizeSmtpResponse(response) {
	return response.replace(/[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/gi, "[email]").replace(/\s+/g, " ").trim().slice(0, 500);
}
async function withTimeout(promise, label) {
	let timer;
	try {
		return await Promise.race([promise, new Promise((_, reject) => {
			timer = setTimeout(() => reject(/* @__PURE__ */ new Error(`${label} timed out after ${smtpTimeoutMs()}ms.`)), smtpTimeoutMs());
		})]);
	} finally {
		if (timer) clearTimeout(timer);
	}
}
function escapeHtml(value) {
	return value.replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll("\"", "&quot;").replaceAll("'", "&#39;");
}
//#endregion
//#region routes/api/comments/[id]/email-notification/+server.ts
var POST = async ({ params, request }) => {
	const commentId = params.id;
	if (!commentId) return json({ error: "댓글 ID가 없습니다." }, { status: 400 });
	const auth = await authenticateBearerRequest(request);
	if (!auth.ok) return authFailureResponse(auth, {
		missingToken: "로그인 후 이메일 알림을 요청할 수 있습니다.",
		unavailable: "이메일 알림 서버 환경 변수가 설정되지 않았습니다.",
		invalidSession: "로그인 세션을 확인하지 못했습니다."
	});
	const { data: comment, error: commentError } = await auth.serviceClient.from("comments").select("id,project_id,author_id,body").eq("id", commentId).maybeSingle();
	if (commentError || !comment) return json({ error: "댓글을 찾을 수 없습니다." }, { status: 404 });
	if (comment.author_id !== auth.user.id) return json({ error: "본인이 작성한 댓글만 이메일 알림을 요청할 수 있습니다." }, { status: 403 });
	const { data: project, error: projectError } = await auth.serviceClient.from("projects").select("id,author_id,title").eq("id", comment.project_id).maybeSingle();
	if (projectError || !project || project.author_id === auth.user.id) return json({
		ok: true,
		skipped: true,
		message: "이메일 알림 대상이 없습니다."
	});
	const [{ data: recipient }, { data: actor }] = await Promise.all([auth.serviceClient.from("profiles").select("id,email,name").eq("id", project.author_id).maybeSingle(), auth.serviceClient.from("profiles").select("id,email,name").eq("id", auth.user.id).maybeSingle()]);
	try {
		const result = await sendProjectCommentEmail({
			recipient: recipient ?? {
				id: project.author_id,
				email: null,
				name: null
			},
			actor: actor ?? null,
			project,
			comment
		});
		return json(result, { status: result.ok ? 200 : 202 });
	} catch (error) {
		console.warn("Failed to send comment email notification", error);
		return json({
			ok: false,
			skipped: false,
			message: "이메일 알림 발송에 실패했습니다."
		}, { status: 202 });
	}
};
//#endregion
export { POST };
