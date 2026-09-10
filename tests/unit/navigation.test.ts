import assert from 'node:assert/strict';
import test from 'node:test';
import { safeInternalNextPath } from '../../src/lib/navigation.ts';

test('allows internal next paths with query and hash', () => {
	assert.equal(safeInternalNextPath('/submit'), '/submit');
	assert.equal(safeInternalNextPath('/projects/123/edit?mode=pbix#top'), '/projects/123/edit?mode=pbix#top');
});

test('rejects external or ambiguous next paths', () => {
	assert.equal(safeInternalNextPath('https://example.com/projects'), '/');
	assert.equal(safeInternalNextPath('//example.com/projects'), '/');
	assert.equal(safeInternalNextPath('javascript:alert(1)'), '/');
	assert.equal(safeInternalNextPath('/\\example.com'), '/');
	assert.equal(safeInternalNextPath('/projects\n/123'), '/');
});

test('rejects login loops and normalizes fallback', () => {
	assert.equal(safeInternalNextPath('/login'), '/');
	assert.equal(safeInternalNextPath('', '/my'), '/my');
	assert.equal(safeInternalNextPath('', 'https://example.com'), '/');
});
