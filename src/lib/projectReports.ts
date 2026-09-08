import { currentSession } from '$lib/auth';
import { getSupabaseClient } from '$lib/supabase';

export const PROJECT_REPORT_REASONS = [
	['embed_broken', '대시보드/임베딩이 열리지 않음'],
	['wrong_content', '제목이나 설명이 실제 내용과 다름'],
	['inappropriate', '부적절한 콘텐츠'],
	['other', '기타']
] as const;

export type ProjectReportReason = (typeof PROJECT_REPORT_REASONS)[number][0];

const REPORT_DETAIL_MAX_CHARS = 500;

export async function submitProjectReport(input: {
	projectId: string;
	reason: ProjectReportReason;
	details: string;
}) {
	const supabase = getSupabaseClient();
	const session = await currentSession();
	if (!supabase || !session) {
		return { ok: false, message: '로그인 후 신고할 수 있습니다.' };
	}

	const normalizedDetails = input.details.trim().replace(/\s+/g, ' ').slice(0, REPORT_DETAIL_MAX_CHARS) || null;
	const { error } = await supabase.from('content_reports').insert({
		project_id: input.projectId,
		reporter_id: session.user.id,
		reason: input.reason,
		details: normalizedDetails
	});

	if (error) {
		return { ok: false, message: '신고를 접수하지 못했습니다. 잠시 후 다시 시도하세요.' };
	}

	return { ok: true, message: '신고가 접수되었습니다. 확인 후 필요한 조치를 진행하겠습니다.' };
}