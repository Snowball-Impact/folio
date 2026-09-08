const VISITOR_ID_KEY = 'folio_visitor_id';

export function getOrCreateVisitorId() {
	const existing = localStorage.getItem(VISITOR_ID_KEY);
	if (existing && isUuid(existing)) {
		return existing;
	}

	const nextId = crypto.randomUUID();
	localStorage.setItem(VISITOR_ID_KEY, nextId);
	return nextId;
}

function isUuid(value: string) {
	return /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(
		value
	);
}
