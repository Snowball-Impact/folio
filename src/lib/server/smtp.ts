/**
 * Encodes a complete RFC 5321 DATA payload. SMTP uses a single dot on its own
 * line as an end-of-message marker, so every body line starting with a dot
 * must be dot-stuffed before it reaches the socket.
 */
export function encodeSmtpData(message: string) {
	const canonicalLines = message.replace(/\r\n|\r|\n/g, '\r\n');
	const dotStuffed = canonicalLines.replace(/(^|\r\n)\./g, '$1..');
	return `${dotStuffed}\r\n.\r\n`;
}
