export type RecoveryParams = {
	code: string;
	tokenHash: string;
	accessToken: string;
	refreshToken: string;
	hasRecovery: boolean;
	errorMessage: string;
};

export function parseRecoveryParams(search: string, hashValue: string): RecoveryParams {
	const query = new URLSearchParams(search);
	const hash = new URLSearchParams(hashValue.replace(/^#/, ''));
	const errorCode = query.get('error_code') || hash.get('error_code') || query.get('error') || hash.get('error') || '';
	const errorDescription = query.get('error_description') || hash.get('error_description') || '';
	const recoveryType = query.get('type') || hash.get('type') || '';
	const tokenHash = query.get('token_hash') || query.get('token') || hash.get('token_hash') || hash.get('token') || '';
	const code = query.get('code') || hash.get('code') || '';
	const accessToken = query.get('access_token') || hash.get('access_token') || '';
	const refreshToken = query.get('refresh_token') || hash.get('refresh_token') || '';
	const validTokenHash = !recoveryType || recoveryType === 'recovery' ? tokenHash : '';

	return {
		code,
		tokenHash: validTokenHash,
		accessToken,
		refreshToken,
		hasRecovery: Boolean(code || validTokenHash || (accessToken && refreshToken)),
		errorMessage: errorCode || errorDescription ? recoveryCallbackError(errorCode, errorDescription) : ''
	};
}

export function authRetryAfterSeconds(message: string) {
	const match = message.match(/(?:after|in)\s+(\d+)\s*seconds?/i);
	if (!match) return 0;
	const seconds = Number(match[1]);
	return Number.isInteger(seconds) && seconds > 0 ? Math.min(seconds, 3600) : 0;
}

export function friendlyAuthError(action: string, message: string) {
	const lower = message.toLowerCase();
	const retryAfterSeconds = authRetryAfterSeconds(message);
	if (lower.includes('invalid login credentials')) return '이메일 또는 비밀번호를 확인하세요.';
	if (lower.includes('email not confirmed')) return '이메일 인증 후 로그인하세요.';
	if (lower.includes('already registered') || lower.includes('already exists')) return '이미 가입된 이메일입니다. 로그인 화면에서 로그인하세요.';
	if (
		lower.includes('rate limit') ||
		lower.includes('over_email_send_rate_limit') ||
		lower.includes('security purposes') ||
		retryAfterSeconds > 0
	) {
		return retryAfterSeconds > 0
			? `인증 메일은 ${retryAfterSeconds}초 후 다시 요청할 수 있습니다.`
			: '인증 메일 발송 요청이 잠시 제한되었습니다. 잠시 후 다시 시도하세요.';
	}
	if (lower.includes('redirect') && (lower.includes('not allowed') || lower.includes('invalid') || lower.includes('uri'))) {
		return 'Supabase Redirect URLs에 현재 앱 주소가 허용되어 있지 않습니다.';
	}
	if (lower.includes('otp') || lower.includes('token') || lower.includes('expired')) {
		return '비밀번호 재설정 링크가 만료되었거나 이미 사용되었습니다. 다시 요청하세요.';
	}
	if (lower.includes('same password') || lower.includes('different from the old password')) {
		return '기존 비밀번호와 다른 새 비밀번호를 입력하세요.';
	}
	if (lower.includes('password') && (lower.includes('weak') || lower.includes('short') || lower.includes('length'))) {
		return '비밀번호 보안 조건을 만족하지 못했습니다. 더 긴 비밀번호를 입력하세요.';
	}
	return `${action} 중 오류가 발생했습니다. 잠시 후 다시 시도하세요.`;
}

function recoveryCallbackError(code: string, description: string) {
	const value = `${code} ${description}`.toLowerCase();
	if (value.includes('expired') || value.includes('otp_expired')) {
		return '비밀번호 재설정 링크가 만료되었습니다. 새 링크를 요청하세요.';
	}
	if (value.includes('access_denied') || value.includes('invalid')) {
		return '비밀번호 재설정 링크가 유효하지 않거나 이미 사용되었습니다. 새 링크를 요청하세요.';
	}
	return '비밀번호 재설정 링크를 처리하지 못했습니다. 새 링크를 요청하세요.';
}
