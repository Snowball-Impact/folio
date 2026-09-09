import assert from 'node:assert/strict';
import test from 'node:test';
import { sanitizeProjectHtml } from '../../src/lib/format.ts';

test('preserves rich editor parity formatting through sanitizer', () => {
	const sanitized = sanitizeProjectHtml(
		[
			'<h6 data-indent="1" style="margin-left: 24px">작은 제목</h6>',
			'<p><span style="color: #1459c8; font-family: serif; font-size: 1.5em">강조</span></p>',
			'<p><mark style="background-color: #fff2a8">하이라이트</mark><sup>2</sup><sub>n</sub></p>'
		].join('')
	);

	assert.match(sanitized, /<h6 data-indent="1" style="margin-left: 24px">작은 제목<\/h6>/);
	assert.match(sanitized, /color: #1459c8/);
	assert.match(sanitized, /font-family: serif/);
	assert.match(sanitized, /font-size: 1.5em/);
	assert.match(sanitized, /<mark style="background-color: #fff2a8">하이라이트<\/mark>/);
	assert.match(sanitized, /<sup>2<\/sup>/);
	assert.match(sanitized, /<sub>n<\/sub>/);
});
