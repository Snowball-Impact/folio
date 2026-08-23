import type { Session, User } from '@supabase/supabase-js';
import { getSupabaseClient } from '$lib/supabase';

export type AuthProfile = {
	id: string;
	email: string;
	name: string;
	organization: string | null;
};

export type AuthResult = {
	ok: boolean;
	message: string;
};

export function normalizeEmail(email: string) {
	return email.trim().toLowerCase();
}

export function isValidEmail(email: string) {
	const [local, domain] = email.split('@');
	return Boolean(local && domain?.includes('.') && !domain.startsWith('.') && !domain.endsWith('.'));
}

export async function currentSession(): Promise<Session | null> {
	const supabase = getSupabaseClient();
	if (!supabase) {
		return null;
	}
	const { data } = await supabase.auth.getSession();
	return data.session;
}

export async function currentProfile(user: User): Promise<AuthProfile> {
	const supabase = getSupabaseClient();
	const fallback = profileFromUser(user);
	if (!supabase) {
		return fallback;
	}

	const { data } = await supabase
		.from('profiles')
		.select('id,email,name,organization')
		.eq('id', user.id)
		.maybeSingle();
	if (!data) {
		return fallback;
	}
	return {
		id: String(data.id ?? user.id),
		email: String(data.email ?? user.email ?? ''),
		name: String(data.name ?? fallback.name),
		organization: nullableString(data.organization)
	};
}

export async function signInWithEmail(email: string, password: string): Promise<AuthResult> {
	const supabase = getSupabaseClient();
	if (!supabase) {
		return { ok: false, message: 'Supabase 환경 변수가 설정되지 않았습니다.' };
	}
	const normalizedEmail = normalizeEmail(email);
	if (!normalizedEmail || !password) {
		return { ok: false, message: '이메일과 비밀번호를 입력하세요.' };
	}
	if (!isValidEmail(normalizedEmail)) {
		return { ok: false, message: '올바른 이메일 주소를 입력하세요.' };
	}

	const { error } = await supabase.auth.signInWithPassword({
		email: normalizedEmail,
		password
	});
	if (error) {
		return { ok: false, message: friendlyAuthError('로그인', error.message) };
	}
	return { ok: true, message: '로그인되었습니다.' };
}

export async function signUpWithEmail(input: {
	email: string;
	password: string;
	passwordConfirm: string;
	name: string;
	organization: string;
}): Promise<AuthResult> {
	const supabase = getSupabaseClient();
	if (!supabase) {
		return { ok: false, message: 'Supabase 환경 변수가 설정되지 않았습니다.' };
	}

	const email = normalizeEmail(input.email);
	const name = input.name.trim();
	const organization = input.organization.trim();
	if (!email || !input.password || !input.passwordConfirm || !name || !organization) {
		return { ok: false, message: '필수 입력값을 모두 입력하세요.' };
	}
	if (!isValidEmail(email)) {
		return { ok: false, message: '올바른 이메일 주소를 입력하세요.' };
	}
	if (input.password.length < 8) {
		return { ok: false, message: '비밀번호는 최소 8자 이상으로 입력하세요.' };
	}
	if (input.password !== input.passwordConfirm) {
		return { ok: false, message: '비밀번호와 비밀번호 확인이 일치하지 않습니다.' };
	}

	const { data, error } = await supabase.auth.signUp({
		email,
		password: input.password,
		options: {
			emailRedirectTo: `${window.location.origin}/login?verified=1`,
			data: {
				name,
				organization,
				consented_policy_version_ids: []
			}
		}
	});

	if (error) {
		return { ok: false, message: friendlyAuthError('회원가입', error.message) };
	}
	if (data.user?.identities?.length === 0) {
		return { ok: false, message: '이미 가입된 이메일입니다. 로그인 화면에서 로그인하세요.' };
	}
	if (data.session) {
		return { ok: true, message: '회원가입이 완료되었습니다.' };
	}
	return { ok: true, message: '회원가입 요청을 처리했습니다. 메일함을 확인하세요.' };
}

export async function signOut() {
	const supabase = getSupabaseClient();
	if (supabase) {
		await supabase.auth.signOut();
	}
}

function profileFromUser(user: User): AuthProfile {
	const metadata = user.user_metadata ?? {};
	return {
		id: user.id,
		email: user.email ?? '',
		name: String(metadata.name ?? user.email?.split('@')[0] ?? '사용자'),
		organization: nullableString(metadata.organization)
	};
}

function nullableString(value: unknown) {
	const text = String(value ?? '').trim();
	return text || null;
}

function friendlyAuthError(action: string, message: string) {
	const lower = message.toLowerCase();
	if (lower.includes('invalid login credentials')) {
		return '이메일 또는 비밀번호를 확인하세요.';
	}
	if (lower.includes('email not confirmed')) {
		return '이메일 인증 후 로그인하세요.';
	}
	if (lower.includes('already registered') || lower.includes('already exists')) {
		return '이미 가입된 이메일입니다. 로그인 화면에서 로그인하세요.';
	}
	return `${action} 중 오류가 발생했습니다. 잠시 후 다시 시도하세요.`;
}
