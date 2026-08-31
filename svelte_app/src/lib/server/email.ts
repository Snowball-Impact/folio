import { env } from '$env/dynamic/private';

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

type Socket = {
	readable: ReadableStream<Uint8Array>;
	writable: WritableStream<Uint8Array>;
	opened: Promise<unknown>;
	close(): Promise<void>;
	startTls(): Socket;
};

type SocketModule = {
	connect(
		address: { hostname: string; port: number },
		options?: { secureTransport?: 'off' | 'on' | 'starttls' }
	): Socket;
};

type SmtpSession = {
	socket: Socket;
	reader: ReturnType<typeof smtpReader>;
	writer: WritableStreamDefaultWriter<Uint8Array>;
};
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

	const { connect } = await loadCloudflareSockets();
	let session = createSmtpSession(
		connect(
			{ hostname: host, port },
			{ secureTransport: shouldUseDirectTls(port) ? 'on' : shouldUseStartTls(port) ? 'starttls' : 'off' }
		)
	);
	try {
		await withTimeout(session.socket.opened, 'SMTP connect');
		await session.reader.expect(undefined, 'SMTP greeting');
		await command(session, `EHLO ${smtpClientName()}`, undefined, 'SMTP EHLO');
		if (shouldUseStartTls(port)) {
			await command(session, 'STARTTLS', undefined, 'SMTP STARTTLS');
			session.reader.releaseLock();
			session.writer.releaseLock();
			session = createSmtpSession(session.socket.startTls());
			await withTimeout(session.socket.opened, 'SMTP TLS connect');
			await command(session, `EHLO ${smtpClientName()}`, undefined, 'SMTP TLS EHLO');
			await authenticate(session);
			await sendEnvelope(session, from, to, message);
			return;
		}
		await authenticate(session);
		await sendEnvelope(session, from, to, message);
	} finally {
		session.reader.releaseLock();
		session.writer.releaseLock();
		await session.socket.close().catch(() => undefined);
	}
}

async function loadCloudflareSockets() {
	const moduleName = 'cloudflare:sockets';
	return (await import(/* @vite-ignore */ moduleName)) as SocketModule;
}

async function sendEnvelope(session: SmtpSession, from: string, to: string, message: string) {
	await command(session, `MAIL FROM:<${from}>`, undefined, 'SMTP MAIL FROM');
	await command(session, `RCPT TO:<${to}>`, undefined, 'SMTP RCPT TO');
	await command(session, 'DATA', 354, 'SMTP DATA');
	await writeSmtp(session, `${message}\r\n.\r\n`, 'SMTP message write');
	await session.reader.expect(undefined, 'SMTP message body');
	await command(session, 'QUIT', 221, 'SMTP QUIT');
}

async function authenticate(session: SmtpSession) {
	const username = env.SMTP_USERNAME?.trim();
	const password = env.SMTP_PASSWORD ?? '';
	if (!username && !password) {
		return;
	}
	const token = Buffer.from(`\0${username}\0${password}`).toString('base64');
	await command(session, `AUTH PLAIN ${token}`, 235, 'SMTP AUTH');
}

function createSmtpSession(socket: Socket): SmtpSession {
	return {
		socket,
		reader: smtpReader(socket.readable.getReader()),
		writer: socket.writable.getWriter()
	};
}

function smtpReader(reader: ReadableStreamDefaultReader<Uint8Array>) {
	let buffer = '';
	const decoder = new TextDecoder();
	return {
		async expect(expectedCode?: number, label = 'SMTP command') {
			while (true) {
				const lines = buffer.split(/\r?\n/).filter(Boolean);
				const lastLine = lines.at(-1) ?? '';
				const match = lastLine.match(/^(\d{3})\s/);
				if (match) {
					buffer = '';
					const code = Number(match[1]);
					if (expectedCode && code !== expectedCode) {
						throw new Error(`${label} expected ${expectedCode}, got ${code}.`);
					}
					if (!expectedCode && code >= 400) {
						throw new Error(`${label} failed with ${code}.`);
					}
					return lines.join('\n');
				}

				const result = await withTimeout(reader.read(), label);
				if (result.done) {
					throw new Error(`${label} ended before SMTP response.`);
				}
				buffer += decoder.decode(result.value, { stream: true });
			}
		},
		releaseLock() {
			reader.releaseLock();
		}
	};
}

async function command(
	session: SmtpSession,
	value: string,
	expectedCode?: number,
	label?: string
) {
	await writeSmtp(session, `${value}\r\n`, `${label ?? 'SMTP command'} write`);
	return session.reader.expect(expectedCode, label);
}

async function writeSmtp(session: SmtpSession, value: string, label: string) {
	await withTimeout(session.writer.write(new TextEncoder().encode(value)), label);
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

async function withTimeout<T>(promise: Promise<T>, label: string) {
	let timer: ReturnType<typeof setTimeout> | undefined;
	try {
		return await Promise.race([
			promise,
			new Promise<never>((_, reject) => {
				timer = setTimeout(() => reject(new Error(`${label} timed out after ${smtpTimeoutMs()}ms.`)), smtpTimeoutMs());
			})
		]);
	} finally {
		if (timer) {
			clearTimeout(timer);
		}
	}
}

function escapeHtml(value: string) {
	return value
		.replaceAll('&', '&amp;')
		.replaceAll('<', '&lt;')
		.replaceAll('>', '&gt;')
		.replaceAll('"', '&quot;')
		.replaceAll("'", '&#39;');
}
