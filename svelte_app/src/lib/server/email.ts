import { env } from '$env/dynamic/private';
import net from 'node:net';
import tls from 'node:tls';

type ProfileRecord = {
	email: string | null;
	name: string | null;
};

type ProjectRecord = {
	id: string;
	title: string | null;
};

type CommentRecord = {
	body: string | null;
};

type SendCommentEmailInput = {
	recipient: ProfileRecord;
	actor: ProfileRecord | null;
	project: ProjectRecord;
	comment: CommentRecord;
};

type SmtpSocket = net.Socket | tls.TLSSocket;
const DEFAULT_SMTP_TIMEOUT_MS = 8000;

export function isEmailConfigured() {
	return Boolean(env.SMTP_HOST && env.SMTP_FROM_EMAIL);
}

export async function sendProjectCommentEmail(input: SendCommentEmailInput) {
	if (!isEmailConfigured()) {
		return { ok: true, skipped: true, message: '이메일 알림 설정이 없어 발송을 건너뜁니다.' };
	}
	const recipientEmail = input.recipient.email?.trim();
	if (!recipientEmail) {
		return { ok: false, skipped: false, message: '수신자 이메일을 찾지 못했습니다.' };
	}

	const projectTitle = input.project.title?.trim() || '프로젝트';
	const actorName = input.actor?.name?.trim() || '사용자';
	const commentPreview = (input.comment.body || '').trim().slice(0, 240);
	const subject = `[FOLIO] ${projectTitle}에 새 댓글이 남겨졌습니다.`;
	const projectUrl = `${appUrl().replace(/\/$/, '')}/projects/${encodeURIComponent(input.project.id)}`;
	const message = buildMessage({
		to: recipientEmail,
		subject,
		text: [
			`${projectTitle}에 새 댓글이 남겨졌습니다.`,
			'',
			`작성자: ${actorName}`,
			`댓글: ${commentPreview}`,
			'',
			`프로젝트 보기: ${projectUrl}`
		].join('\n'),
		html: [
			`<p><strong>${escapeHtml(projectTitle)}</strong>에 새 댓글이 남겨졌습니다.</p>`,
			`<p><strong>작성자</strong>: ${escapeHtml(actorName)}</p>`,
			`<p>${escapeHtml(commentPreview)}</p>`,
			`<p><a href="${escapeHtml(projectUrl)}">프로젝트 보기</a></p>`
		].join('\n')
	});

	await sendSmtpMessage(recipientEmail, message);
	return { ok: true, skipped: false, message: '이메일 알림을 발송했습니다.' };
}

async function sendSmtpMessage(to: string, message: string) {
	const host = env.SMTP_HOST?.trim();
	if (!host) {
		throw new Error('SMTP host is missing.');
	}
	const port = Number(env.SMTP_PORT || 587);
	const from = env.SMTP_FROM_EMAIL?.trim();
	if (!from) {
		throw new Error('SMTP from email is missing.');
	}

	let socket: SmtpSocket = shouldUseDirectTls(port)
		? tls.connect({ host, port, servername: host })
		: net.connect({ host, port });
	const reader = smtpReader(socket);
	try {
		await reader.expect(undefined, 'SMTP greeting');
		await command(socket, reader, `EHLO ${smtpClientName()}`, undefined, 'SMTP EHLO');
		if (shouldUseStartTls(port)) {
			await command(socket, reader, 'STARTTLS', undefined, 'SMTP STARTTLS');
			socket = tls.connect({ socket, servername: host });
			const tlsReader = smtpReader(socket);
			await command(socket, tlsReader, `EHLO ${smtpClientName()}`, undefined, 'SMTP TLS EHLO');
			await authenticate(socket, tlsReader);
			await sendEnvelope(socket, tlsReader, from, to, message);
			return;
		}
		await authenticate(socket, reader);
		await sendEnvelope(socket, reader, from, to, message);
	} finally {
		socket.end();
	}
}

async function sendEnvelope(socket: SmtpSocket, reader: ReturnType<typeof smtpReader>, from: string, to: string, message: string) {
	await command(socket, reader, `MAIL FROM:<${from}>`, undefined, 'SMTP MAIL FROM');
	await command(socket, reader, `RCPT TO:<${to}>`, undefined, 'SMTP RCPT TO');
	await command(socket, reader, 'DATA', 354, 'SMTP DATA');
	socket.write(`${message}\r\n.\r\n`);
	await reader.expect(undefined, 'SMTP message body');
	await command(socket, reader, 'QUIT', 221, 'SMTP QUIT');
}

async function authenticate(socket: SmtpSocket, reader: ReturnType<typeof smtpReader>) {
	const username = env.SMTP_USERNAME?.trim();
	const password = env.SMTP_PASSWORD ?? '';
	if (!username && !password) {
		return;
	}
	const token = Buffer.from(`\0${username}\0${password}`).toString('base64');
	await command(socket, reader, `AUTH PLAIN ${token}`, 235, 'SMTP AUTH');
}

function smtpReader(socket: SmtpSocket) {
	let buffer = '';
	socket.setEncoding('utf8');
	return {
		expect(expectedCode?: number, label = 'SMTP command') {
			return new Promise<string>((resolve, reject) => {
				const timer = setTimeout(() => {
					cleanup();
					socket.destroy(new Error(`${label} timed out after ${smtpTimeoutMs()}ms.`));
					reject(new Error(`${label} timed out after ${smtpTimeoutMs()}ms.`));
				}, smtpTimeoutMs());
				const cleanup = () => {
					clearTimeout(timer);
					socket.off('data', onData);
					socket.off('error', onError);
				};
				const onData = (chunk: string) => {
					buffer += chunk;
					const lines = buffer.split(/\r?\n/).filter(Boolean);
					const lastLine = lines.at(-1) ?? '';
					const match = lastLine.match(/^(\d{3})\s/);
					if (!match) {
						return;
					}
					cleanup();
					const code = Number(match[1]);
					if (expectedCode && code !== expectedCode) {
						reject(new Error(`${label} expected ${expectedCode}, got ${code}.`));
						return;
					}
					if (!expectedCode && code >= 400) {
						reject(new Error(`${label} failed with ${code}.`));
						return;
					}
					buffer = '';
					resolve(lines.join('\n'));
				};
				const onError = (error: Error) => {
					cleanup();
					reject(error);
				};
				socket.on('data', onData);
				socket.once('error', onError);
			});
		}
	};
}

async function command(
	socket: SmtpSocket,
	reader: ReturnType<typeof smtpReader>,
	value: string,
	expectedCode?: number,
	label?: string
) {
	socket.write(`${value}\r\n`);
	return reader.expect(expectedCode, label);
}

function buildMessage({ to, subject, text, html }: { to: string; subject: string; text: string; html: string }) {
	const boundary = `folio-${Date.now().toString(36)}`;
	const fromEmail = env.SMTP_FROM_EMAIL?.trim() || '';
	const fromName = env.SMTP_FROM_NAME?.trim() || 'FOLIO';
	return [
		`From: ${encodedHeader(fromName)} <${fromEmail}>`,
		`To: <${to}>`,
		`Subject: ${encodedHeader(subject)}`,
		'MIME-Version: 1.0',
		`Content-Type: multipart/alternative; boundary="${boundary}"`,
		'',
		`--${boundary}`,
		'Content-Type: text/plain; charset=UTF-8',
		'Content-Transfer-Encoding: 8bit',
		'',
		text,
		`--${boundary}`,
		'Content-Type: text/html; charset=UTF-8',
		'Content-Transfer-Encoding: 8bit',
		'',
		html,
		`--${boundary}--`
	].join('\r\n');
}

function encodedHeader(value: string) {
	return `=?UTF-8?B?${Buffer.from(value).toString('base64')}?=`;
}

function shouldUseStartTls(port: number) {
	return env.SMTP_USE_TLS !== 'false' && port !== 465;
}

function shouldUseDirectTls(port: number) {
	return env.SMTP_USE_TLS !== 'false' && port === 465;
}

function smtpClientName() {
	return (env.APP_URL || 'localhost').replace(/^https?:\/\//, '').replace(/[:/].*$/, '') || 'localhost';
}

function appUrl() {
	return env.APP_URL || 'http://localhost:5173';
}

function smtpTimeoutMs() {
	const configured = Number(env.SMTP_TIMEOUT_MS || DEFAULT_SMTP_TIMEOUT_MS);
	return Number.isFinite(configured) && configured > 0 ? configured : DEFAULT_SMTP_TIMEOUT_MS;
}

function escapeHtml(value: string) {
	return value
		.replaceAll('&', '&amp;')
		.replaceAll('<', '&lt;')
		.replaceAll('>', '&gt;')
		.replaceAll('"', '&quot;')
		.replaceAll("'", '&#39;');
}
