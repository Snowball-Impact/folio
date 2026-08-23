export function formatCount(value: number | null | undefined) {
	return new Intl.NumberFormat('ko-KR').format(Number(value ?? 0));
}

export function formatDate(value: string | null | undefined) {
	if (!value) {
		return '정보 없음';
	}
	return value.slice(0, 10);
}

export function platformLabel(platformKey: string | null | undefined, projectType?: string) {
	if (platformKey === 'powerbi' || projectType === 'powerbi') {
		return 'Power BI';
	}
	if (platformKey === 'tableau' || projectType === 'tableau') {
		return 'Tableau';
	}
	if (platformKey === 'datastudio' || projectType === 'looker') {
		return 'Data Studio';
	}
	if (platformKey === 'streamlit' || projectType === 'streamlit') {
		return 'Streamlit';
	}
	return 'Other';
}

export function plainTextFromHtml(value: string) {
	return value
		.replace(/<[^>]*>/g, ' ')
		.replace(/&nbsp;/g, ' ')
		.replace(/&amp;/g, '&')
		.replace(/&lt;/g, '<')
		.replace(/&gt;/g, '>')
		.replace(/&quot;/g, '"')
		.replace(/&#39;/g, "'")
		.replace(/\s+/g, ' ')
		.trim();
}
