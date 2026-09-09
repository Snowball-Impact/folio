export function publicConfigSeconds(name: string, fallbackSeconds: number) {
	const env = import.meta.env as Record<string, string | undefined>;
	const value = Number(env[name]);
	return Number.isFinite(value) && value > 0 ? value : fallbackSeconds;
}

export function publicConfigMilliseconds(name: string, fallbackSeconds: number) {
	return publicConfigSeconds(name, fallbackSeconds) * 1000;
}
