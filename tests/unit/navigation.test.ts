import assert from 'node:assert/strict';
import test from 'node:test';
import { safeInternalNextPath } from '../../src/lib/navigation.ts';

test('allows only safe internal next paths', () => {
	assert.equal(safeInternalNextPath('/projects/123/edit?mode=pbix#top'), '/projects/123/edit?mode=pbix#top');
	assert.equal(safeInternalNextPath('https://example.com'), '/');
	assert.equal(safeInternalNextPath('//example.com'), '/');
	assert.equal(safeInternalNextPath('/\\example.com'), '/');
});
