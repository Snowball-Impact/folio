import assert from 'node:assert/strict';
import test from 'node:test';
import { encodeSmtpData } from '../../src/lib/server/smtp.ts';

test('canonicalizes line endings and dot-stuffs every SMTP DATA line', () => {
	const encoded = encodeSmtpData('첫 줄\n.\r\n..\r\n마지막 줄');
	assert.equal(encoded, '첫 줄\r\n..\r\n...\r\n마지막 줄\r\n.\r\n');
	assert.equal(encoded.slice(0, -5).includes('\r\n.\r\n'), false);
});
