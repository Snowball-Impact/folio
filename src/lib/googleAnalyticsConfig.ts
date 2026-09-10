export function normalizeGoogleAnalyticsMeasurementId(value: string | null | undefined) {
	const measurementId = String(value ?? '').trim().toUpperCase();
	return /^G-[A-Z0-9]+$/.test(measurementId) ? measurementId : '';
}
