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
	if (value === 'cert') {
		return 'certifications';
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
	const matchedVideoKeys = new Set<string>();
	const items: PowerBINewsItem[] = [];
	let latestUpdateDate = '';

	for (const [releaseLabel, rows] of groupBy(updateRows, 'release_label')) {
		const overview = rows.find((row) => row.section?.toLowerCase() === 'overview') ?? rows[0] ?? {};
		const releaseKey = releaseMatchKey(releaseLabel);
		const videoRow = videoByRelease.get(releaseKey);
		const version = firstValue(rows, 'version');
		const date = releaseSortDate(releaseLabel);
		if (videoRow) {
			matchedVideoKeys.add(releaseKey);
		}
		if (!latestUpdateDate || date > latestUpdateDate) {
			latestUpdateDate = date;
		}
		items.push({
			label: '월간 정기 업데이트',
			title: [localizeReleaseLabel(releaseLabel), version ? `v${version}` : ''].filter(Boolean).join(' · '),
			date,
			source_url: overview.source_url || '',
			bullets: releaseSummaryBullets(rows),
			video: videoRow ? videoLink(videoRow) : null
		});
	}

	items.push(...standaloneUpdateVideoItems(updateVideoRows, matchedVideoKeys, latestUpdateDate));

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
			bullets: changelogSummaryBullets(rows),
			video: null
		});
	}

	return items.sort((first, second) => second.date.localeCompare(first.date));
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

function standaloneUpdateVideoItems(
	rows: Array<Record<string, string>>,
	matchedVideoKeys: Set<string>,
	latestUpdateDate: string
): PowerBINewsItem[] {
	const items: PowerBINewsItem[] = [];
	for (const row of rows) {
		const key = releaseMatchKey(row.title_en || row.title_ko);
		if (!key || matchedVideoKeys.has(key)) {
			continue;
		}
		const date = releaseSortDate(`${titleCase(key)} update`);
		if (latestUpdateDate && date <= latestUpdateDate) {
			continue;
		}
		items.push({
			label: '공식 업데이트 영상',
			title: `${localizeReleaseLabel(`${titleCase(key)} update`)} 공식 영상`,
			date,
			source_url: row.source_url || row.video_url || '',
			bullets: [row.summary_ko || 'Microsoft Power BI 공식 채널에 게시된 월간 업데이트 영상입니다.'],
			video: videoLink(row)
		});
	}
	return items;
}

function releaseSummaryBullets(rows: Array<Record<string, string>>) {
	const bullets: string[] = [];
	const seen = new Set<string>();
	for (const row of rows) {
		if (row.section?.toLowerCase() === 'overview') {
			continue;
		}
		const bullet = releaseSummaryBullet(row);
		if (!bullet || seen.has(bullet)) {
			continue;
		}
		seen.add(bullet);
		bullets.push(bullet);
		if (bullets.length >= 5) {
			break;
		}
	}
	return bullets;
}

function changelogSummaryBullets(rows: Array<Record<string, string>>) {
	const bullets: string[] = [];
	const seen = new Set<string>();
	for (const row of rows) {
		const bullet = localizeFix(row.fix_en || row.summary_ko);
		if (!bullet || seen.has(bullet)) {
			continue;
		}
		seen.add(bullet);
		bullets.push(bullet);
		if (bullets.length >= 5) {
			break;
		}
	}
	return bullets;
}

function releaseSummaryBullet(row: Record<string, string>) {
	const rawTitle = row.feature_title_en || row.feature_title_ko || row.title_en || row.title_ko || '';
	const title = rawTitle.toLowerCase();
	const section = localizeSection(row.section);

	if (title.includes('dataviz world championship')) return 'Power BI 커뮤니티 시각화 대회 일정이 공개되었습니다.';
	if (title.includes('fabcon')) return 'Fabric 및 Power BI 컨퍼런스 등록과 세션 정보가 업데이트되었습니다.';
	if (title.includes('fabric apps') && title.includes('semantic')) return '의미 체계 모델을 기반으로 업무용 데이터 앱을 만드는 Fabric 앱 기능이 미리 보기로 추가되었습니다.';
	if (title.includes('copilot') && title.includes('web modeling')) return '웹 모델링 화면에서 Copilot이 모델 작성과 수정 작업을 보조합니다.';
	if (title.includes('report authoring agent')) return 'AI가 보고서 작성 과정의 일부를 대신 수행하도록 에이전트 기능이 미리 보기로 추가되었습니다.';
	if (title.includes('data answering') && title.includes('m365')) return 'Microsoft 365 Copilot Chat에서 데이터 질문에 답하는 기능이 실험적으로 제공됩니다.';
	if (title.includes('data answering')) return 'Fabric Skills와 협업 도구에서 데이터 질문에 답하는 기능이 실험적으로 제공됩니다.';
	if (title.includes('explore improvements')) return 'Copilot 기반 데이터 탐색 흐름이 개선되어 필요한 인사이트를 더 빠르게 찾을 수 있습니다.';
	if (title.includes('summary shortcut')) return 'Copilot 요약을 바로 실행할 수 있는 단축 기능이 추가되었습니다.';
	if (title.includes('shape map')) return 'Shape Map 시각적 개체가 정식 기능으로 전환되어 지도 기반 표현을 더 안정적으로 사용할 수 있습니다.';
	if (title.includes('date picker') || title.includes('slicer')) return '슬라이서에 날짜 선택 기능이 추가되어 기간 필터를 더 쉽게 설정할 수 있습니다.';
	if (title.includes('user-defined function') || title.includes('udf')) return 'DAX 사용자 정의 함수가 확장되어 반복 계산 로직을 더 깔끔하게 관리할 수 있습니다.';
	if (title.includes('matrix')) return '행렬 시각적 개체의 표시와 상호작용 기능이 개선되었습니다.';
	if (title.includes('visual calculation') && title.includes('custom total')) return '시각적 계산과 사용자 지정 합계가 정식 제공되어 보고서 안에서 계산 결과를 더 유연하게 보여줄 수 있습니다.';
	if (title.includes('custom total')) return '사용자 지정 합계 옵션이 늘어나 합계 행을 보고서 의도에 맞게 조정할 수 있습니다.';
	if (title.includes('scatter')) return '분산형 차트에서 데이터 포인트를 더 잘 비교할 수 있도록 시각화 옵션이 개선되었습니다.';
	if (title.includes('bar') || title.includes('column')) return '막대 및 열 차트의 표현 옵션이 보강되었습니다.';
	if (title.includes('card')) return '카드 시각적 개체에서 핵심 지표를 보여주는 방식이 개선되었습니다.';
	if (title.includes('azure map') || title.includes('maps')) return 'Azure 지도와 지도 시각화 관련 표시 옵션이 개선되었습니다.';
	if (title.includes('tooltip')) return '도구 설명에서 보조 정보를 보여주는 방식이 개선되었습니다.';
	if (title.includes('model')) return '데이터 모델링 작업을 더 쉽게 관리할 수 있는 기능이 추가되었습니다.';
	if (title.includes('connector') || title.includes('data connectivity')) return '외부 데이터 연결과 커넥터 관련 기능이 업데이트되었습니다.';
	if (title.includes('preview')) return `${section} 영역에 새 미리 보기 기능이 추가되었습니다.`;
	if (title.includes('general availability') || title.includes('generally available')) return `${section} 영역의 미리 보기 기능이 정식 기능으로 전환되었습니다.`;

	const localizedTitle = localizeTitle(rawTitle);
	return section && localizedTitle ? `${section}: ${localizedTitle}` : localizedTitle;
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

function localizeSection(value: string | undefined) {
	const section = String(value ?? '').trim();
	const sectionMap: Record<string, string> = {
		Overview: '요약',
		General: '일반',
		'Copilot and AI': 'Copilot 및 AI',
		Reporting: '보고서',
		Modeling: '모델링',
		'Data connectivity': '데이터 연결',
		Visualizations: '시각화',
		Other: '기타'
	};
	return sectionMap[section] ?? localizeTitle(section);
}

function localizeTitle(value: string | undefined) {
	let text = String(value ?? '').trim();
	const replacements: Record<string, string> = {
		update: '업데이트',
		announcement: '공지',
		registration: '등록',
		Preview: '미리 보기',
		'General Availability': '정식 제공',
		'Semantic Models': '의미 체계 모델',
		'semantic models': '의미 체계 모델',
		modeling: '모델링',
		visual: '시각적 개체',
		visuals: '시각적 개체',
		slicer: '슬라이서',
		Slicer: '슬라이서',
		Maps: '지도',
		'Azure Maps': 'Azure 지도',
		Matrix: '행렬',
		Card: '카드',
		Tooltip: '도구 설명',
		tooltips: '도구 설명',
		DAX: 'DAX',
		'Fabric Apps': 'Fabric 앱',
		Copilot: 'Copilot',
		'Power BI': 'Power BI'
	};
	for (const [source, target] of Object.entries(replacements)) {
		text = text.replaceAll(source, target);
	}
	return text;
}

function localizeFix(value: string | undefined) {
	const original = String(value ?? '').trim().replace(/\.$/, '');
	if (!original) {
		return '변경 로그 항목';
	}
	const title = original.toLowerCase();
	if (title.includes('data label positioning') && title.includes('column chart')) return '열 차트에서 데이터 레이블 위치가 어긋나던 문제가 수정되었습니다.';
	if (title.includes('native queries') && title.includes('export queries')) return '쿼리 내보내기에서 네이티브 쿼리를 출력 대상으로 저장할 때 실패하던 문제가 수정되었습니다.';
	if (title.includes('selected marker fill color') && title.includes('azure maps')) return 'Azure 지도에서 선택한 마커 채우기 색상이 적용되지 않던 문제가 수정되었습니다.';
	if (title.includes('adbc driver assemblies')) return 'ADBC 드라이버 어셈블리가 누락되던 문제가 수정되었습니다.';
	if (title.includes('view switcher icons')) return 'Power BI Desktop에서 보기 전환 아이콘이 올바르게 표시되지 않던 문제가 수정되었습니다.';
	if (title.includes('empty schema') && title.includes('multimodel')) return '여러 모델을 함께 작성할 때 스키마가 비어 있는 것으로 처리되어 Copilot이나 모델 작성 화면에서 오류가 나던 문제가 수정되었습니다.';
	if (title.includes('calculated tables') && title.includes('refresh')) return '계산 테이블이 새로 고침 과정에서 누락되던 문제가 수정되었습니다.';
	if (title.includes('treat calculated tables as refreshable')) return '계산 테이블도 새로 고침 대상에 포함되도록 동작이 업데이트되었습니다.';
	if (title.includes('snowflake connector') && title.includes('directquery')) return 'Snowflake 커넥터를 DirectQuery 모드로 사용할 때 지원되지 않는 쿼리 오류가 발생하던 문제가 수정되었습니다.';
	if (title.includes('pbip files') && title.includes('hangs')) return '연결 또는 파일 오류가 있는 PBIP 파일을 열 때 Power BI Desktop이 멈추던 문제가 수정되었습니다.';
	if (title.includes('copilot orchestration throttling')) return 'Copilot 오케스트레이션 제한 오류가 사용자 오류로 올바르게 분류되도록 수정되었습니다.';
	if (title.includes('queries') && title.includes('powerquery editor')) return 'Power Query 편집기에서 쿼리 섹션이 보이지 않던 문제가 수정되었습니다.';
	if (title.includes('column or measure not found')) return "저장 시 '열 또는 측정값을 모델에서 찾을 수 없음' 오류가 발생하던 문제가 수정되었습니다.";
	if (title.includes('databricks sql endpoint')) return 'Databricks SQL Endpoint 연결 문제가 수정되었습니다.';
	if (title.includes('dataflow refresh')) return 'Power BI Desktop에서 Dataflow 새로 고침이 실패하던 문제가 수정되었습니다.';
	if (title.includes('incremental refresh validation')) return '여러 데이터 원본을 참조하는 테이블의 증분 새로 고침 검증 문제가 수정되었습니다.';
	return `${localizeTitle(original)} 문제가 수정되었습니다.`;
}

function titleCase(value: string) {
	return value
		.split(' ')
		.filter(Boolean)
		.map((part) => part.charAt(0).toUpperCase() + part.slice(1))
		.join(' ');
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
