import assert from 'node:assert/strict';
import test from 'node:test';
import {
	buildProjectPayload,
	normalizeOptionalUrl,
	normalizePowerBIEmbedUrl,
	projectInputForPbixReplacement,
	validateProjectInput
} from '../../src/lib/projectInput.ts';
import type { ProjectSubmitInput } from '../../src/lib/types.ts';

function baseInput(): ProjectSubmitInput {
	return {
		title: '프로젝트 제목',
		one_liner: '한 줄 소개',
		tags: '분석, 시각화',
		platform: 'other',
		problem: '문제 정의',
		dataset: '',
		process: '',
		insights: '인사이트',
		power_bi_url: '',
		report_url: '',
		github_url: '',
		thumbnail_url: '',
		thumbnail_mode: 'auto_cover',
		delete_thumbnail: false,
		delete_pbix: false,
		is_public: true
	};
}

test('validates required project fields and length limits', () => {
	const input = baseInput();
	assert.equal(validateProjectInput(input), '');

	assert.equal(validateProjectInput({ ...input, title: ' '.repeat(48) }), '프로젝트명을 입력하세요.');
	assert.equal(validateProjectInput({ ...input, title: 'a'.repeat(49) }), '프로젝트명은 최대 48자까지 입력할 수 있습니다.');
	assert.equal(
		validateProjectInput({ ...input, problem: '', insights: '', dataset: '', process: '' }),
		'프로젝트 본문을 한 섹션 이상 입력하세요.'
	);
});

test('normalizes optional URLs and iframe embed URLs', () => {
	assert.equal(normalizeOptionalUrl(' https://example.com/report '), 'https://example.com/report');
	assert.equal(normalizeOptionalUrl('ftp://example.com/report'), null);
	assert.equal(normalizeOptionalUrl('not a url'), null);
	assert.equal(normalizePowerBIEmbedUrl(''), null);
	assert.equal(
		normalizePowerBIEmbedUrl('<iframe src="https://app.powerbi.com/view?r=abc"></iframe>'),
		'https://app.powerbi.com/view?r=abc'
	);
});

test('builds a normalized platform payload', () => {
	const payload = buildProjectPayload({
		...baseInput(),
		title: '  프로젝트 제목  ',
		one_liner: '  한 줄 소개  ',
		tags: '#Power BI, 분석, 분석, Tableau, 추가 태그',
		platform: 'powerbi',
		power_bi_url: '<iframe src="https://app.powerbi.com/view?r=abc"></iframe>',
		report_url: 'https://example.com/report',
		github_url: 'javascript:alert(1)',
		thumbnail_mode: 'manual_url',
		thumbnail_url: 'https://cdn.example.com/thumbnail.webp',
		is_public: false
	});

	assert.deepEqual(payload, {
		title: '프로젝트 제목',
		one_liner: '한 줄 소개',
		problem: '문제 정의',
		dataset: null,
		process: null,
		insights: '인사이트',
		power_bi_url: 'https://app.powerbi.com/view?r=abc',
		report_url: 'https://example.com/report',
		github_url: null,
		thumbnail_url: 'https://cdn.example.com/thumbnail.webp',
		thumbnail_mode: 'manual_url',
		project_type: 'powerbi',
		platform_key: 'powerbi',
		status: 'published',
		embed_status: 'supported',
		tags: ['Power BI', '분석', '추가 태그'],
		is_public: false
	});
});

test('clears deleted PBIX and non-manual thumbnail values in the payload', () => {
	const payload = buildProjectPayload({
		...baseInput(),
		power_bi_url: 'https://app.powerbi.com/view?r=abc',
		thumbnail_mode: 'upload',
		thumbnail_url: 'https://cdn.example.com/old.webp',
		delete_thumbnail: true,
		delete_pbix: true
	});

	assert.equal(payload.power_bi_url, null);
	assert.equal(payload.thumbnail_url, null);
	assert.equal(payload.thumbnail_mode, 'auto_cover');
	assert.equal(payload.embed_status, 'external_only');
});

test('preserves the existing PBIX during intermediate saves for replacement uploads', () => {
	const input = { ...baseInput(), delete_pbix: true };
	const replacementInput = projectInputForPbixReplacement(input, 'edit', true);

	assert.equal(replacementInput.delete_pbix, false);
	assert.equal(input.delete_pbix, true);
	assert.equal(projectInputForPbixReplacement(input, 'edit', false), input);
	assert.equal(projectInputForPbixReplacement(input, 'create', true), input);
});
