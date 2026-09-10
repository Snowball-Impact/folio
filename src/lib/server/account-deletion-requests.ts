export const MAX_ACCOUNT_DELETION_NOTE_CHARS = 500;

export const ACTIVE_ACCOUNT_DELETION_REQUEST_STATUSES = ['open', 'reviewing'] as const;

export type AccountDeletionRequestStatus = 'open' | 'reviewing' | 'resolved' | 'cancelled';

export type AccountDeletionRequestRecord = {
	id: string;
	user_id: string;
	email: string | null;
	status: AccountDeletionRequestStatus;
	request_note: string | null;
	requested_at: string;
	updated_at: string | null;
};

export const accountDeletionRequestSelectColumns =
	'id,user_id,email,status,request_note,requested_at,updated_at';

export function normalizeAccountDeletionRequestNote(value: unknown) {
	const note = String(value ?? '')
		.replace(/\s+/g, ' ')
		.trim();
	if (!note) {
		return null;
	}
	return note.slice(0, MAX_ACCOUNT_DELETION_NOTE_CHARS);
}

export function accountDeletionRequestPayload(input: {
	userId: string;
	email?: string | null;
	requestNote?: string | null;
}) {
	return {
		user_id: input.userId,
		email: normalizedEmailOrNull(input.email),
		request_note: normalizeAccountDeletionRequestNote(input.requestNote),
		status: 'open' as const
	};
}

function normalizedEmailOrNull(value: string | null | undefined) {
	const email = String(value ?? '').trim().toLowerCase();
	return email || null;
}
