export type ProjectBodySections = {
	problem: string;
	dataset: string;
	process: string;
	insights: string;
};

export const PROJECT_BODY_TEMPLATE = `<h2>문제 정의</h2>
<p>이 프로젝트는 [대상/상황]에서 발생하는 [문제]를 다룹니다. 이를 분석한 이유는 [의사결정/개선 목표]를 더 명확히 하기 위해서입니다.</p>
<p><span style="color: rgb(138, 152, 173);">예시: 이 프로젝트는 청년 구직자가 교육 수료 후 취업까지 이어지는 과정에서 발생하는 이탈 문제를 다룹니다. 이를 분석한 이유는 어떤 요인이 취업 성과에 영향을 주는지 확인하기 위해서입니다.</span></p>
<h2>사용 데이터</h2>
<p>사용한 데이터는 [출처]의 [기간/범위] 데이터입니다. 주요 변수는 [변수1], [변수2], [변수3]이며, 핵심 지표는 [지표]입니다.</p>
<p><span style="color: rgb(138, 152, 173);">예시: 사용한 데이터는 교육 운영 시스템의 2025년 수강생 데이터입니다. 주요 변수는 수강 과정, 출석률, 과제 제출 여부이며, 핵심 지표는 수료율과 취업 연계율입니다.</span></p>
<h2>분석 과정</h2>
<p>먼저 [기준]으로 데이터를 나누어 비교했습니다. 이후 [분석 방법]을 통해 [패턴/차이]를 확인하고, [판단 기준]을 중심으로 결과를 해석했습니다.</p>
<p><span style="color: rgb(138, 152, 173);">예시: 먼저 과정별로 수료율과 취업 연계율을 비교했습니다. 이후 출석률 구간에 따라 성과 차이를 확인하고, 수료 여부와 취업 여부의 관계를 중심으로 결과를 해석했습니다.</span></p>
<h2>핵심 인사이트</h2>
<p>분석 결과 [핵심 발견]을 확인했습니다. 따라서 [대상/조직]은 [추천 행동]을 우선 검토할 필요가 있습니다.</p>
<p><span style="color: rgb(138, 152, 173);">예시: 분석 결과 출석률이 높은 수강생일수록 수료와 취업 연계 가능성이 함께 높아지는 경향을 확인했습니다. 따라서 교육 운영팀은 중도 이탈 위험이 높은 수강생을 조기에 발견하고 개입하는 방안을 우선 검토할 필요가 있습니다.</span></p>`;

const SECTION_TITLES: Array<[keyof ProjectBodySections, string]> = [
	['problem', '문제 정의'],
	['dataset', '사용 데이터'],
	['process', '분석 과정'],
	['insights', '핵심 인사이트']
];

export function projectBodyFromSections(sections: ProjectBodySections) {
	const hasContent = SECTION_TITLES.some(([key]) => plainTextFromHtml(sections[key]).trim());
	if (!hasContent) {
		return PROJECT_BODY_TEMPLATE;
	}
	return SECTION_TITLES.map(([key, title]) => `<h2>${title}</h2>${formatBodyValue(sections[key])}`).join('');
}

export function parseProjectBody(body: string): ProjectBodySections {
	const html = body.trim();
	const sections: ProjectBodySections = {
		problem: '',
		dataset: '',
		process: '',
		insights: ''
	};
	if (!html) {
		return sections;
	}

	const parser = new DOMParser();
	const doc = parser.parseFromString(`<div>${html}</div>`, 'text/html');
	const root = doc.body.firstElementChild;
	if (!root) {
		sections.problem = html;
		return sections;
	}

	let currentKey: keyof ProjectBodySections | null = null;
	let foundHeading = false;
	for (const node of Array.from(root.childNodes)) {
		if (node.nodeType === Node.ELEMENT_NODE) {
			const element = node as HTMLElement;
			const headingKey = headingSectionKey(element);
			if (headingKey) {
				currentKey = headingKey;
				foundHeading = true;
				continue;
			}
		}
		if (currentKey) {
			sections[currentKey] += nodeToHtml(node);
		}
	}

	if (!foundHeading && plainTextFromHtml(html)) {
		sections.problem = html;
	}
	return sections;
}

export function projectBodyHasContent(body: string) {
	const sections = parseProjectBody(body);
	return SECTION_TITLES.some(([key]) => plainTextFromHtml(sections[key]).trim()) || plainTextFromHtml(body).trim().length > 0;
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

function headingSectionKey(element: HTMLElement): keyof ProjectBodySections | null {
	if (element.tagName.toLowerCase() !== 'h2') {
		return null;
	}
	const heading = element.textContent?.trim() ?? '';
	if (heading === '문제 정의') return 'problem';
	if (heading === '사용 데이터') return 'dataset';
	if (heading === '분석 과정' || heading === '분석 및 시각화') return 'process';
	if (heading === '핵심 인사이트' || heading === '주요 관찰 포인트') return 'insights';
	return null;
}

function nodeToHtml(node: ChildNode) {
	if (node.nodeType === Node.TEXT_NODE) {
		return node.textContent?.trim() ? `<p>${escapeHtml(node.textContent)}</p>` : '';
	}
	if (node.nodeType === Node.ELEMENT_NODE) {
		return (node as HTMLElement).outerHTML;
	}
	return '';
}

function formatBodyValue(value: string | null | undefined) {
	const text = value?.trim() ?? '';
	if (!text) {
		return '<p></p>';
	}
	if (text.includes('<') && text.includes('>')) {
		return text;
	}
	return text
		.split(/\r?\n/)
		.map((line) => line.trim())
		.filter(Boolean)
		.map((line) => `<p>${escapeHtml(line)}</p>`)
		.join('');
}

function escapeHtml(value: string | null | undefined) {
	return String(value ?? '')
		.replace(/&/g, '&amp;')
		.replace(/</g, '&lt;')
		.replace(/>/g, '&gt;')
		.replace(/"/g, '&quot;')
		.replace(/'/g, '&#39;');
}