export type CaptureUrlPolicy = {
	allowedHosts?: string;
	appUrl?: string;
	provider: string;
	requestOrigin: string;
};

export function normalizeCaptureUrl(value: string, policy: CaptureUrlPolicy) {
	let rawValue = value.trim();
	if (!rawValue) {
		return null;
	}
	if (rawValue.toLowerCase().startsWith('<iframe')) {
		const match = rawValue.match(/\ssrc=["']([^"']+)["']/i);
		rawValue = match?.[1]?.trim() || rawValue;
	}
	try {
		const url = new URL(rawValue);
		if (!url.hostname || url.username || url.password) {
			return null;
		}
		const isFirstParty = trustedCaptureOrigins(policy).has(url.origin);
		const isLocalFirstParty = isFirstParty && policy.provider === 'local' && isLoopbackHost(url.hostname);
		if ((!isFirstParty && !allowedCaptureHosts(policy).has(url.hostname.toLowerCase())) || (isPrivateNetworkHost(url.hostname) && !isLocalFirstParty)) {
			return null;
		}
		if (url.protocol !== 'https:' && !isLocalFirstParty) {
			return null;
		}
		return url.toString();
	} catch {
		return null;
	}
}

function allowedCaptureHosts(policy: CaptureUrlPolicy) {
	return new Set(
		(policy.allowedHosts ?? '')
			.split(',')
			.map((host) => host.trim().toLowerCase())
			.filter(Boolean)
	);
}

function trustedCaptureOrigins(policy: CaptureUrlPolicy) {
	const origins = new Set([policy.requestOrigin]);
	if (!policy.appUrl?.trim()) {
		return origins;
	}
	try {
		origins.add(new URL(policy.appUrl).origin);
	} catch {
		// An invalid APP_URL must not widen the capture allowlist.
	}
	return origins;
}

function isLoopbackHost(hostname: string) {
	const normalized = hostname.toLowerCase();
	return normalized === 'localhost' || normalized === '127.0.0.1' || normalized === '::1' || normalized.endsWith('.localhost');
}

function isPrivateNetworkHost(hostname: string) {
	const normalized = hostname.toLowerCase();
	if (isLoopbackHost(normalized)) {
		return true;
	}
	const ipv4 = normalized.match(/^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$/);
	if (!ipv4) {
		return false;
	}
	const octets = ipv4.slice(1).map(Number);
	if (octets.some((octet) => octet > 255)) {
		return true;
	}
	return octets[0] === 0 || octets[0] === 10 || octets[0] === 127 || octets[0] >= 224 ||
		(octets[0] === 169 && octets[1] === 254) ||
		(octets[0] === 172 && octets[1] >= 16 && octets[1] <= 31) ||
		(octets[0] === 192 && octets[1] === 168);
}
