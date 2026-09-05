import assert from 'node:assert/strict';
import test from 'node:test';
import {
	comparableProjectTag,
	isExcludedHomeTag,
	normalizeHomeTag,
	normalizePopularHomeTags,
	popularTagStatsFromTagLists,
	popularTagsFromTagLists,
	projectTagsInclude
} from '../../src/lib/projectTags.ts';

test('normalizes home tag query values for links and manual input', () => {
	assert.equal(normalizeHomeTag('  #Data Science  '), 'Data Science');
	assert.equal(normalizeHomeTag('전체'), '');
	assert.equal(normalizeHomeTag(null), '');
});

test('matches project tags by normalized spelling', () => {
	assert.equal(projectTagsInclude(['Data Science', '시각화'], 'data science'), true);
	assert.equal(projectTagsInclude(['데이터 분석', '시각화'], '#데이터분석'), true);
	assert.equal(projectTagsInclude(['공공데이터'], '민간데이터'), false);
	assert.equal(projectTagsInclude(['공공데이터'], ''), true);
});

test('builds popular tags with platform exclusions and normalized counts', () => {
	assert.deepEqual(
		popularTagsFromTagLists(
			[
				['Power BI', 'Data Science', '시각화'],
				['powerbi', '#data science'],
				['데이터 분석', '데이터분석']
			],
			3
		),
		['데이터 분석', 'Data Science', '시각화']
	);
	assert.equal(comparableProjectTag('#Power BI'), 'powerbi');
	assert.equal(isExcludedHomeTag('Power BI'), true);
});

test('builds popular tag counts for home chips', () => {
	assert.deepEqual(
		popularTagStatsFromTagLists(
			[
				['시각화', '데이터 분석'],
				['시각화', '데이터분석'],
				['Power BI', '시각화']
			],
			3
		),
		[
			{ label: '시각화', count: 3 },
			{ label: '데이터 분석', count: 2 }
		]
	);
});

test('normalizes database popular tags without changing ranked order', () => {
	assert.deepEqual(
		normalizePopularHomeTags(['시각화', 'Power BI', 'Data Science', '#data science', '공공데이터'], 3),
		['시각화', 'Data Science', '공공데이터']
	);
});
