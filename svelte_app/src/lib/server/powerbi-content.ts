import desktopCsv from '../../../../docs/curation/powerbi_desktop_download/all.csv?raw';
import updatesCsv from '../../../../docs/curation/powerbi_updates/all.csv?raw';
import changelogCsv from '../../../../docs/curation/powerbi_changelog/all.csv?raw';
import learningCsv from '../../../../docs/curation/powerbi_learning_videos/all.csv?raw';
import updateVideosCsv from '../../../../docs/curation/powerbi_update_videos/all.csv?raw';
import learningProgramsCsv from '../../../../docs/curation/powerbi_learning_programs/all.csv?raw';
import communityCsv from '../../../../docs/curation/powerbi_community_blog/all.csv?raw';
import type {
	PowerBIContentLink,
	PowerBIHubContent,
	PowerBIHubTopic,
	PowerBILearningGroup,
	PowerBINewsItem
} from '$lib/types';

const csvSources = {
	desktop: desktopCsv,
	updates: updatesCsv,
	changelog: changelogCsv,
	learning: learningCsv,
	updateVideos: updateVideosCsv,
	learningPrograms: learningProgramsCsv,
	community: communityCsv
};

const learningCategoryOrder = [
	'공식 학습',
	'한국 크리에이터',
	'DAX',
	'Power Query',
	'모델링',
	'시각화',
	'Fabric',
	'실무',
	'디자인'
];

export function normalizePowerBIHubTopic(value: string | null): PowerBIHubTopic {
	if (value === 'learning' || value === 'community' || value === 'certifications') {
		return value;
	}
	return 'news';
}

export async function loadPowerBIHubContent(topic: PowerBIHubTopic): Promise<PowerBIHubContent> {
	const [desktopRows, updateRows, changelogRows, learningRows, updateVideoRows, programRows, communityRows] =
		await Promise.all([
			readCsv(csvSources.desktop),
			readCsv(csvSources.updates),
			readCsv(csvSources.changelog),
			readCsv(csvSources.learning),
			readCsv(csvSources.updateVideos),
			readCsv(csvSources.learningPrograms),
			readCsv(csvSources.community)
		]);

	const news = buildNewsItems(updateRows, changelogRows, updateVideoRows);
	const learning = buildLearningGroups(learningRows, programRows);
	const community = communityRows
		.map(communityLink)
		.sort((first, second) => second.date.localeCompare(first.date));
	const certifications = certificationLinks();

	return {
		topic,
		desktop: desktopRows[0] ? desktopLink(desktopRows[0]) : null,
		news,
		learning,
		community,
		certifications,
		counts: {
			news: news.length,
			learning: learning.reduce((total, group) => total + group.programs.length + group.videos.length, 0),
			community: community.length,
			certifications: certifications.length
		}
	};
}

async function readCsv(text: string): Promise<Array<Record<string, string>>> {
	return parseCsv(text.replace(/^\uFEFF/, ''));
}

function parseCsv(text: string) {
	const rows: string[][] = [];
	let row: string[] = [];
	let cell = '';
	let inQuotes = false;

	for (let index = 0; index < text.length; index += 1) {
		const char = text[index];
		const next = text[index + 1];
		if (char === '"' && inQuotes && next === '"') {
			cell += '"';
			index += 1;
		} else if (char === '"') {
			inQuotes = !inQuotes;
		} else if (char === ',' && !inQuotes) {
			row.push(cell);
			cell = '';
		} else if ((char === '\n' || char === '\r') && !inQuotes) {
			if (char === '\r' && next === '\n') {
				index += 1;
			}
			row.push(cell);
			if (row.some((value) => value.trim())) {
				rows.push(row);
			}
			row = [];
			cell = '';
		} else {
			cell += char;
		}
	}
	if (cell || row.length) {
		row.push(cell);
		rows.push(row);
	}

	const [headers = [], ...records] = rows;
	return records.map((record) =>
		Object.fromEntries(headers.map((header, index) => [header, record[index] ?? '']))
	);
}

function buildNewsItems(
	updateRows: Array<Record<string, string>>,
	changelogRows: Array<Record<string, string>>,
	updateVideoRows: Array<Record<string, string>>
) {
	const videoByRelease = new Map(updateVideoRows.map((row) => [releaseMatchKey(row.title_en || row.title_ko), row]));
	const items: PowerBINewsItem[] = [];

	for (const [releaseLabel, rows] of groupBy(updateRows, 'release_label')) {
		const overview = rows.find((row) => row.section?.toLowerCase() === 'overview') ?? rows[0] ?? {};
		const videoRow = videoByRelease.get(releaseMatchKey(releaseLabel));
		const version = firstValue(rows, 'version');
		items.push({
			label: '월간 정기 업데이트',
			title: [localizeReleaseLabel(releaseLabel), version ? `v${version}` : ''].filter(Boolean).join(' · '),
			date: releaseSortDate(releaseLabel),
			source_url: overview.source_url || '',
			bullets: releaseSummaryBullets(rows),
			video: videoRow ? videoLink(videoRow) : null
		});
	}

	for (const [releaseLabel, rows] of groupBy(changelogRows, 'release_label')) {
		const releasedAt = firstValue(rows, 'released_at');
		const version = firstValue(rows, 'version');
		items.push({
			label: '패치 로그',
			title: [localizeReleaseLabel(releaseLabel), version ? `v${version}` : '', localizeDate(releasedAt)]
				.filter(Boolean)
				.join(' · '),
			date: normalizeDate(releasedAt) || releaseSortDate(releaseLabel),
			source_url: rows[0]?.source_url || '',
			bullets: rows
				.map((row) => row.summary_ko || row.fix_en || '')
				.filter(Boolean)
				.slice(0, 5),
			video: null
		});
	}

	return items.sort((first, second) => second.date.localeCompare(first.date)).slice(0, 24);
}

function buildLearningGroups(
	learningRows: Array<Record<string, string>>,
	programRows: Array<Record<string, string>>
): PowerBILearningGroup[] {
	const videos = learningRows
		.filter((row) => !row.title_en?.toLowerCase().includes('power bi update'))
		.map(videoLink);
	const programs = programRows.map(programLink);
	const categories = [...new Set([...learningCategoryOrder, ...programs.map((item) => item.topic), ...videos.map((item) => item.topic)])];

	return categories
		.map((category) => ({
			category,
			programs: programs.filter((item) => item.topic === category),
			videos: videos.filter((item) => item.topic === category).slice(0, 9)
		}))
		.filter((group) => group.programs.length || group.videos.length);
}

function desktopLink(row: Record<string, string>): PowerBIContentLink {
	return {
		title: row.title || 'Microsoft Power BI Desktop',
		summary: row.summary_ko || row.description_ko || 'Power BI Desktop 최신 다운로드 정보를 확인합니다.',
		url: row.source_url || '',
		source: row.source || 'Microsoft Download Center',
		date: row.published_at || '',
		topic: row.version ? `v${row.version}` : 'Power BI Desktop',
		image_url: firstImage(row.image_urls)
	};
}

function videoLink(row: Record<string, string>): PowerBIContentLink {
	return {
		title: row.title_ko || row.title_en || 'Power BI 영상',
		summary: row.summary_ko || 'Power BI 학습에 참고할 수 있는 영상입니다.',
		url: row.video_url || row.source_url || '',
		source: row.channel_name || row.source || 'YouTube',
		date: row.published_at || '',
		topic: row.topic || row.channel_type || '학습',
		image_url: row.thumbnail_url || youtubeThumbnail(row.video_url)
	};
}

function programLink(row: Record<string, string>): PowerBIContentLink {
	return {
		title: row.title_ko || row.title || 'Power BI 학습 과정',
		summary: row.summary_ko || 'Power BI 학습 과정을 확인합니다.',
		url: row.playlist_url || row.first_video_url || '',
		source: row.provider || 'Power BI',
		date: row.video_count ? `${row.video_count} videos` : '',
		topic: row.topic || row.program_type || '공식 학습',
		image_url: row.thumbnail_url || youtubeThumbnail(row.first_video_url)
	};
}

function communityLink(row: Record<string, string>): PowerBIContentLink {
	return {
		title: row.title_ko || row.title_en || 'Power BI 커뮤니티 소식',
		summary: row.summary_ko || 'Power BI 커뮤니티에서 공유된 최신 글입니다.',
		url: row.source_url || '',
		source: row.author ? `${row.source || 'Community'} · ${row.author}` : row.source || 'Community',
		date: row.published_at || '',
		topic: row.topic || '실무 팁',
		image_url: row.image_url || null
	};
}

function certificationLinks(): PowerBIContentLink[] {
	return [
		{
			title: 'PL-300 Power BI Data Analyst',
			summary: 'Microsoft 공식 Power BI Data Analyst Associate 시험 가이드를 확인합니다.',
			url: 'https://learn.microsoft.com/en-us/credentials/certifications/resources/study-guides/pl-300',
			source: 'Microsoft Learn',
			date: '',
			topic: 'Microsoft Certified',
			image_url: null
		},
		{
			title: '경영정보시각화능력',
			summary: '대한상공회의소 BI Specialist 자격 안내를 확인합니다.',
			url: 'https://license.korcham.net/co/examguide.do?mm=28&cd=0108',
			source: 'KCCI',
			date: '',
			topic: 'BI Specialist',
			image_url: null
		}
	];
}

function releaseSummaryBullets(rows: Array<Record<string, string>>) {
	return rows
		.filter((row) => row.section?.toLowerCase() !== 'overview')
		.map((row) => row.feature_description_ko || row.summary_ko || row.feature_title_ko || row.feature_title_en || '')
		.filter(Boolean)
		.slice(0, 5);
}

function groupBy(rows: Array<Record<string, string>>, key: string) {
	const groups = new Map<string, Array<Record<string, string>>>();
	for (const row of rows) {
		const label = row[key] || '기타';
		groups.set(label, [...(groups.get(label) ?? []), row]);
	}
	return groups;
}

function firstValue(rows: Array<Record<string, string>>, key: string) {
	return rows.find((row) => row[key])?.[key] ?? '';
}

function releaseMatchKey(value: string | undefined) {
	return String(value ?? '')
		.toLowerCase()
		.replace('power bi update', '')
		.replace('update', '')
		.replace(/[-:]/g, ' ')
		.trim()
		.replace(/\s+/g, ' ');
}

function releaseSortDate(value: string | undefined) {
	const text = String(value ?? '');
	const year = firstYear(text) ?? 1900;
	const month = monthNumber(text) ?? 1;
	return `${year.toString().padStart(4, '0')}-${month.toString().padStart(2, '0')}-01`;
}

function normalizeDate(value: string | undefined) {
	const text = String(value ?? '').trim();
	if (!text) {
		return '';
	}
	const parsed = Date.parse(text);
	if (!Number.isNaN(parsed)) {
		return new Date(parsed).toISOString().slice(0, 10);
	}
	return text;
}

function localizeReleaseLabel(value: string | undefined) {
	let text = String(value ?? '').trim();
	for (const [english, korean] of Object.entries(monthLabels)) {
		text = text.replace(english, korean);
	}
	return text.replace('update', '업데이트');
}

function localizeDate(value: string | undefined) {
	let text = String(value ?? '').trim();
	for (const [english, korean] of Object.entries(monthLabels)) {
		text = text.replace(english, korean);
	}
	return text;
}

function monthNumber(value: string) {
	for (const [month, label] of Object.keys(monthLabels).entries()) {
		if (value.includes(label)) {
			return month + 1;
		}
	}
	return null;
}

function firstYear(value: string) {
	const match = value.match(/\b(20\d{2}|19\d{2})\b/);
	return match ? Number(match[1]) : null;
}

function firstImage(value: string | undefined) {
	return String(value ?? '').split(';')[0]?.trim() || null;
}

function youtubeThumbnail(url: string | undefined) {
	const text = String(url ?? '');
	const videoId = text.includes('v=') ? text.split('v=', 2)[1]?.split('&', 1)[0] : '';
	return videoId ? `https://i.ytimg.com/vi/${videoId}/hqdefault.jpg` : null;
}

const monthLabels: Record<string, string> = {
	January: '1월',
	February: '2월',
	March: '3월',
	April: '4월',
	May: '5월',
	June: '6월',
	July: '7월',
	August: '8월',
	September: '9월',
	October: '10월',
	November: '11월',
	December: '12월'
};
