import assert from 'node:assert/strict';
import test from 'node:test';
import {
	MAX_ACCOUNT_DELETION_NOTE_CHARS,
	accountDeletionRequestPayload,
	normalizeAccountDeletionRequestNote
} from '../../src/lib/server/account-deletion-requests.ts';

test('normalizes account deletion request notes', () => {
	assert.equal(normalizeAccountDeletionRequestNote('  탈퇴 사유를\n남깁니다.  '), '탈퇴 사유를 남깁니다.');
	assert.equal(normalizeAccountDeletionRequestNote('   '), null);
	assert.equal(normalizeAccountDeletionRequestNote(null), null);
});

test('limits account deletion request notes', () => {
	const value = 'a'.repeat(MAX_ACCOUNT_DELETION_NOTE_CHARS + 20);
	assert.equal(normalizeAccountDeletionRequestNote(value)?.length, MAX_ACCOUNT_DELETION_NOTE_CHARS);
});

test('builds account deletion request payload with normalized email', () => {
	assert.deepEqual(
		accountDeletionRequestPayload({
			userId: 'user-1',
			email: ' USER@Example.COM ',
			requestNote: '  확인 부탁드립니다. '
		}),
		{
			user_id: 'user-1',
			email: 'user@example.com',
			request_note: '확인 부탁드립니다.',
			status: 'open'
		}
	);
});
