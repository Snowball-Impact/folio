import fs from 'node:fs';
import path from 'node:path';
import { chromium, expect } from '@playwright/test';
import { createClient } from '@supabase/supabase-js';

const projectId = process.env.PLAYWRIGHT_RICH_BODY_PROJECT_ID?.trim();
const baseUrl = process.env.PLAYWRIGHT_BASE_URL?.trim() || 'http://127.0.0.1:5174';
const evidenceDir = path.resolve(process.cwd(), '..', 'artifacts', 'uiux-rich-body-persistence-20260829');

if (!projectId) {
	throw new Error('PLAYWRIGHT_RICH_BODY_PROJECT_ID가 필요합니다.');
}

function readEnvFile(path) {
	if (!fs.existsSync(path)) {
		return {};
	}
	return Object.fromEntries(
		fs
			.readFileSync(path, 'utf8')
			.split(/\r?\n/)
			.map((line) => line.match(/^\s*([^#=\s]+)\s*=\s*(.*)\s*$/))
			.filter(Boolean)
			.map(([, key, value]) => [key, value.trim().replace(/^['"]|['"]$/g, '')])
	);
}

const env = {
	...readEnvFile('../.env'),
	...readEnvFile('.env')
};
const email = process.env.FOLIO_TEST_ID?.trim() || env.FOLIO_TEST_ID || env.test_id;
const password = process.env.FOLIO_TEST_PW?.trim() || env.FOLIO_TEST_PW || env.test_pw;
const admin = createClient(env.SUPABASE_URL, env.SUPABASE_SERVICE_ROLE_KEY);
const contentColumns = 'problem,dataset,process,insights';
const snapshotResult = await admin.from('projects').select(contentColumns).eq('id', projectId).single();

if (snapshotResult.error || !snapshotResult.data) {
	throw new Error(`본문 snapshot 실패: ${snapshotResult.error?.message || '프로젝트 없음'}`);
}
if (!email || !password) {
	throw new Error('테스트 계정 설정이 필요합니다.');
}

const original = snapshotResult.data;
const editPath = `/projects/${projectId}/edit`;
const detailPath = `/projects/${projectId}`;
const structurePattern = /<h2[ >][\s\S]*<\/h2>[\s\S]*<ul[ >][\s\S]*<li[ >][\s\S]*<\/ul>[\s\S]*<blockquote[ >]/;
const linkHref = 'https://example.com/reference';
const linkText = '참고 링크';
const imageSrc = new URL('/snowball-impact.webp', baseUrl).toString();
const imageAlt = '분석 결과 차트';
const uploadedImageAlt = 'test1_thumbnail.jpg';
const mathLatex = 'x^2 + y^2 = z^2';
const advancedHeadingText = '서식 persistence 본문 검증';
const advancedFontSize = '1.5em';

function sameImageSet(actual, expected) {
	const key = (image) => `${image.src ?? ''}\u0000${image.alt ?? ''}`;
	return JSON.stringify(actual.map(key).sort()) === JSON.stringify(expected.map(key).sort());
}

function withoutImages(shape) {
	const { images: _images, ...rest } = shape;
	return rest;
}

async function verifyViewport(name, width, height) {
	const browser = await chromium.launch({ headless: true });
	const page = await browser.newPage({
		viewport: { width, height },
		isMobile: name === 'mobile',
		locale: 'ko-KR'
	});

	try {
		await page.goto(`${baseUrl}/login?next=${encodeURIComponent(editPath)}`, { waitUntil: 'networkidle' });
		await page.locator('input[type="email"]').fill(email);
		await page.locator('input[type="password"]').fill(password);
		await page.getByRole('button', { name: '로그인' }).click();
		await page.waitForURL((url) => url.pathname === editPath, { timeout: 20_000 });
		await page.locator('form.project-form').waitFor({ state: 'visible', timeout: 15_000 });

		const editor = page.locator('.rich-editor .tiptap');
		await expect(editor).toHaveAttribute('contenteditable', 'true', { timeout: 8_000 });
		await editor.click();
		await page.keyboard.press('Control+A');
		await page.keyboard.press('Backspace');
		await page.locator('.rich-editor-format-select').selectOption('heading2');
		const headingBox = await editor.locator('h2').boundingBox();
		if (!headingBox) {
			throw new Error('빈 제목 노드의 위치를 확인할 수 없습니다.');
		}
		await page.mouse.click(headingBox.x + 4, headingBox.y + headingBox.height / 2);
		await page.keyboard.insertText('문제 정의');
		await expect(editor.locator('h2')).toHaveText('문제 정의');
		await page.keyboard.press('Enter');
		await page.keyboard.insertText('서식 persistence 본문 검증');
		await page.keyboard.press('Enter');
		await page.getByTitle('글머리 목록').click();
		const listItemBox = await editor.locator('ul > li').first().boundingBox();
		if (!listItemBox) {
			throw new Error('빈 목록 항목의 위치를 확인할 수 없습니다.');
		}
		await page.mouse.click(listItemBox.x + 4, listItemBox.y + listItemBox.height / 2);
		await page.keyboard.insertText('목록 항목 하나');
		await page.keyboard.press('Enter');
		await page.keyboard.insertText('목록 항목 둘');
		await page.keyboard.press('Enter');
		await page.keyboard.press('Enter');
		await page.getByTitle('인용').click();
		const quoteBox = await editor.locator('blockquote').first().boundingBox();
		if (!quoteBox) {
			throw new Error('빈 인용 블록의 위치를 확인할 수 없습니다.');
		}
		await page.mouse.click(quoteBox.x + 4, quoteBox.y + quoteBox.height / 2);
		await page.keyboard.insertText('인용 서식 확인');
		await page.keyboard.press('Enter');
		await page.keyboard.press('Enter');
		await page.keyboard.insertText(linkText);
		await page.keyboard.press('Shift+Home');
		page.once('dialog', (dialog) => dialog.accept(linkHref));
		await page.getByRole('button', { name: 'Link', exact: true }).click();
		await expect(editor.locator(`a[href="${linkHref}"]`)).toHaveText(linkText);
		await page.locator('.rich-editor-color-select').selectOption('#1459c8');
		await page.locator('.rich-editor-highlight-select').selectOption('#fff2a8');
		await page.locator('.rich-editor-font-select').selectOption('serif');
		await page.getByTitle('위첨자').click();
		await page.getByTitle('아래첨자').click();
		await editor.click();
		await page.keyboard.press('Control+End');
		let imagePrompt = 0;
		const handleImageDialog = async (dialog) => {
			if (imagePrompt++ === 0) {
				await dialog.accept(imageSrc);
				return;
			}
			await dialog.accept(imageAlt);
		};
		page.on('dialog', handleImageDialog);
		await page.getByTitle('이미지 삽입').click();
		await expect(editor.locator(`img[src="${imageSrc}"]`)).toHaveAttribute('alt', imageAlt);
		page.off('dialog', handleImageDialog);
		page.once('dialog', (dialog) => dialog.accept(mathLatex));
		await page.getByTitle('수식 삽입').click();
		await expect(editor.locator(`[data-type="inline-math"][data-latex="${mathLatex}"]`)).toHaveCount(1);
		await editor.click();
		await page.keyboard.press('Control+End');
		await page.keyboard.press('Enter');
		await page.keyboard.insertText(advancedHeadingText);
		const advancedParagraph = editor.locator('p').filter({ hasText: advancedHeadingText }).last();
		await advancedParagraph.click();
		await page.locator('.rich-editor-format-select').selectOption('heading6');
		await expect(editor.locator('h6')).toHaveText(advancedHeadingText);
		await editor.locator('h6').selectText();
		await page.locator('.rich-editor-size-select').selectOption(advancedFontSize);
		await editor.locator('h6').click();
		await page.keyboard.press('End');
		await page.getByTitle('들여쓰기').click();
		await expect(editor.locator(`h6[data-indent="1"]`)).toHaveText(advancedHeadingText);

		const editorShape = await editor.evaluate((element) => ({
			headings: [...element.querySelectorAll('h2')].map((node) => node.textContent?.trim()),
			subHeadings: [...element.querySelectorAll('h6')].map((node) => node.textContent?.trim()),
			fontSizes: [...element.querySelectorAll('[style*="font-size"]')].map((node) => node.getAttribute('style')?.match(/font-size:\s*([^;]+)/)?.[1]?.trim() ?? ''),
			indents: [...element.querySelectorAll('[data-indent]')].map((node) => node.getAttribute('data-indent')),
			listItems: [...element.querySelectorAll('ul > li')].map((node) => node.textContent?.trim()),
			quotes: [...element.querySelectorAll('blockquote')].map((node) => node.textContent?.trim()),
			links: [...element.querySelectorAll('a')].map((node) => ({ text: node.textContent?.trim(), href: node.getAttribute('href') })),
			superscripts: [...element.querySelectorAll('sup')].map((node) => node.textContent?.trim()),
			subscripts: [...element.querySelectorAll('sub')].map((node) => node.textContent?.trim()),
			colors: [...element.querySelectorAll('span[style*="color"]')].map((node) => getComputedStyle(node).color),
			fontFamilies: [...element.querySelectorAll('span[style*="font-family"]')].map((node) => getComputedStyle(node).fontFamily),
			backgroundColors: [...element.querySelectorAll('mark')].map((node) => getComputedStyle(node).backgroundColor),
			images: [...element.querySelectorAll('img')].filter((node) => node.getAttribute('src')).map((node) => ({ src: node.getAttribute('src'), alt: node.getAttribute('alt') })),
			math: [...element.querySelectorAll('[data-type="inline-math"], [data-type="block-math"]')].map((node) => ({ type: node.getAttribute('data-type'), latex: node.getAttribute('data-latex') }))
		}));
		const editorHtml = await editor.innerHTML();
		const marksPersisted = (shape) =>
			JSON.stringify({
				superscripts: shape.superscripts,
				subscripts: shape.subscripts,
				colors: shape.colors,
				fontFamilies: shape.fontFamilies,
				backgroundColors: shape.backgroundColors
			}) ===
			JSON.stringify({
				superscripts: [linkText],
				subscripts: [linkText],
				colors: ['rgb(20, 89, 200)'],
				fontFamilies: ['serif'],
				backgroundColors: ['rgb(255, 242, 168)']
			});
		const editorHasStructure =
			structurePattern.test(editorHtml) &&
			editorShape.links.some((link) => link.text === linkText && link.href === linkHref) &&
			marksPersisted(editorShape) &&
			JSON.stringify(editorShape.subHeadings) === JSON.stringify([advancedHeadingText]) &&
			JSON.stringify(editorShape.fontSizes) === JSON.stringify([advancedFontSize]) &&
			JSON.stringify(editorShape.indents) === JSON.stringify(['1']) &&
			JSON.stringify(editorShape) ===
			JSON.stringify({
				headings: ['문제 정의'],
				subHeadings: [advancedHeadingText],
				fontSizes: [advancedFontSize],
				indents: ['1'],
				listItems: ['목록 항목 하나', '목록 항목 둘'],
				quotes: ['인용 서식 확인'],
				links: [{ text: linkText, href: linkHref }],
				superscripts: [linkText],
				subscripts: [linkText],
				colors: ['rgb(20, 89, 200)'],
				fontFamilies: ['serif'],
				backgroundColors: ['rgb(255, 242, 168)'],
				images: [{ src: imageSrc, alt: imageAlt }],
				math: [{ type: 'inline-math', latex: mathLatex }]
			});
		const bodyImageInput = page.locator('[data-body-image-input]');
		await bodyImageInput.setInputFiles(path.resolve(process.cwd(), '..', 'artifacts', 'test1_thumbnail.jpg'));
		await expect(editor.locator(`img[alt="${uploadedImageAlt}"]`)).toHaveCount(1);
		await expect(editor.locator(`img[src="${imageSrc}"]`)).toHaveCount(1);
		await page.waitForTimeout(150);
		await expect(editor.locator(`img[src="${imageSrc}"]`)).toHaveCount(1);
		const bodyImageResponsePromise = page.waitForResponse((response) =>
			response.url().includes(`/api/projects/${projectId}/body-image`) && response.request().method() === 'POST'
		);
		await page.getByRole('button', { name: '수정 완료', exact: true }).click();
		const bodyImageResponse = await bodyImageResponsePromise;
		const bodyImagePayload = await bodyImageResponse.json();
		if (!bodyImageResponse.ok() || !bodyImagePayload.image_url) {
			throw new Error(`본문 이미지 업로드 응답 실패: ${JSON.stringify(bodyImagePayload)}`);
		}
		const uploadedImageUrl = bodyImagePayload.image_url;
		await page.waitForURL((url) => url.pathname === detailPath, { timeout: 20_000 });
		await page.locator('#project-report').waitFor({ state: 'visible', timeout: 15_000 });
		const detailHtml = await page.locator('#project-report').innerHTML();
		const detailShape = await page.locator('#project-report').evaluate((element) => ({
			subHeadings: [...element.querySelectorAll('h6')].map((node) => node.textContent?.trim()),
			fontSizes: [...element.querySelectorAll('[style*="font-size"]')].map((node) => node.getAttribute('style')?.match(/font-size:\s*([^;]+)/)?.[1]?.trim() ?? ''),
			indents: [...element.querySelectorAll('[data-indent]')].map((node) => node.getAttribute('data-indent')),
			listItems: [...element.querySelectorAll('ul > li')].map((node) => node.textContent?.trim()),
			quotes: [...element.querySelectorAll('blockquote')].map((node) => node.textContent?.trim()),
			links: [...element.querySelectorAll('a')].map((node) => ({ text: node.textContent?.trim(), href: node.getAttribute('href') })),
			superscripts: [...element.querySelectorAll('sup')].map((node) => node.textContent?.trim()),
			subscripts: [...element.querySelectorAll('sub')].map((node) => node.textContent?.trim()),
			colors: [...element.querySelectorAll('span[style*="color"]')].map((node) => getComputedStyle(node).color),
			fontFamilies: [...element.querySelectorAll('span[style*="font-family"]')].map((node) => getComputedStyle(node).fontFamily),
			backgroundColors: [...element.querySelectorAll('mark')].map((node) => getComputedStyle(node).backgroundColor),
			images: [...element.querySelectorAll('img')].filter((node) => node.getAttribute('src')).map((node) => ({ src: node.getAttribute('src'), alt: node.getAttribute('alt') })),
			math: [...element.querySelectorAll('[data-type="inline-math"], [data-type="block-math"]')].map((node) => ({ type: node.getAttribute('data-type'), latex: node.getAttribute('data-latex') }))
		}));
		const detailHasStructure =
			/<ul[ >][\s\S]*<li[ >][\s\S]*<\/ul>[\s\S]*<blockquote[ >]/.test(detailHtml) &&
			detailShape.links.some((link) => link.text === linkText && link.href === linkHref) &&
			marksPersisted(detailShape) &&
			JSON.stringify(detailShape.subHeadings) === JSON.stringify([advancedHeadingText]) &&
			JSON.stringify(detailShape.fontSizes) === JSON.stringify([advancedFontSize]) &&
			JSON.stringify(detailShape.indents) === JSON.stringify(['1']) &&
			sameImageSet(detailShape.images, [
				{ src: imageSrc, alt: imageAlt },
				{ src: uploadedImageUrl, alt: uploadedImageAlt }
			]) &&
			JSON.stringify(withoutImages(detailShape)) ===
			JSON.stringify({
				subHeadings: [advancedHeadingText],
				fontSizes: [advancedFontSize],
				indents: ['1'],
				listItems: ['목록 항목 하나', '목록 항목 둘'],
				quotes: ['인용 서식 확인'],
				links: [{ text: linkText, href: linkHref }],
				superscripts: [linkText],
				subscripts: [linkText],
				colors: ['rgb(20, 89, 200)'],
				fontFamilies: ['serif'],
				backgroundColors: ['rgb(255, 242, 168)'],
				math: [{ type: 'inline-math', latex: mathLatex }]
			});

		await page.goto(`${baseUrl}${editPath}`, { waitUntil: 'networkidle' });
		await page.locator('form.project-form').waitFor({ state: 'visible', timeout: 15_000 });
		const editHtml = await page.locator('.rich-editor .tiptap').innerHTML();
		const editShape = await page.locator('.rich-editor .tiptap').evaluate((element) => ({
			headings: [...element.querySelectorAll('h2')].map((node) => node.textContent?.trim()),
			subHeadings: [...element.querySelectorAll('h6')].map((node) => node.textContent?.trim()),
			fontSizes: [...element.querySelectorAll('[style*="font-size"]')].map((node) => node.getAttribute('style')?.match(/font-size:\s*([^;]+)/)?.[1]?.trim() ?? ''),
			indents: [...element.querySelectorAll('[data-indent]')].map((node) => node.getAttribute('data-indent')),
			listItems: [...element.querySelectorAll('ul > li')].map((node) => node.textContent?.trim()),
			quotes: [...element.querySelectorAll('blockquote')].map((node) => node.textContent?.trim()),
			links: [...element.querySelectorAll('a')].map((node) => ({ text: node.textContent?.trim(), href: node.getAttribute('href') })),
			superscripts: [...element.querySelectorAll('sup')].map((node) => node.textContent?.trim()),
			subscripts: [...element.querySelectorAll('sub')].map((node) => node.textContent?.trim()),
			colors: [...element.querySelectorAll('span[style*="color"]')].map((node) => getComputedStyle(node).color),
			fontFamilies: [...element.querySelectorAll('span[style*="font-family"]')].map((node) => getComputedStyle(node).fontFamily),
			backgroundColors: [...element.querySelectorAll('mark')].map((node) => getComputedStyle(node).backgroundColor),
			images: [...element.querySelectorAll('img')].filter((node) => node.getAttribute('src')).map((node) => ({ src: node.getAttribute('src'), alt: node.getAttribute('alt') })),
			math: [...element.querySelectorAll('[data-type="inline-math"], [data-type="block-math"]')].map((node) => ({ type: node.getAttribute('data-type'), latex: node.getAttribute('data-latex') }))
		}));
		const editHasStructure =
			structurePattern.test(editHtml) &&
			editShape.headings.includes('문제 정의') &&
			marksPersisted(editShape) &&
			JSON.stringify(editShape.subHeadings) === JSON.stringify(editorShape.subHeadings) &&
			JSON.stringify(editShape.fontSizes) === JSON.stringify(editorShape.fontSizes) &&
			JSON.stringify(editShape.indents) === JSON.stringify(editorShape.indents) &&
			sameImageSet(editShape.images, detailShape.images) &&
			JSON.stringify(editShape.listItems) === JSON.stringify(editorShape.listItems) &&
			JSON.stringify(editShape.quotes) === JSON.stringify(editorShape.quotes) &&
			JSON.stringify(editShape.links) === JSON.stringify(editorShape.links) &&
			JSON.stringify(editShape.math) === JSON.stringify(editorShape.math);
		const evidence = { viewport: name, editorHasStructure, detailHasStructure, editHasStructure, editorShape, detailShape, editShape };
		if (!editorHasStructure || !detailHasStructure || !editHasStructure) {
			throw new Error(`서식 구조 persistence 실패: ${JSON.stringify(evidence)}`);
		}
		fs.mkdirSync(evidenceDir, { recursive: true });
		await page.screenshot({
			path: path.join(evidenceDir, `${name}-edit-rich-body.png`),
			fullPage: true
		});
		fs.writeFileSync(
			path.join(evidenceDir, `${name}-metrics.json`),
			JSON.stringify(evidence, null, 2),
			'utf8'
		);

		return evidence;
	} finally {
		await browser.close();
	}
}

try {
	const results = [];
	for (const [name, width, height] of [
		['desktop', 1440, 1000],
		['mobile', 390, 844]
	]) {
		results.push(await verifyViewport(name, width, height));
		const restoreResult = await admin.from('projects').update(original).eq('id', projectId);
		if (restoreResult.error) {
			throw new Error(`본문 원복 실패: ${restoreResult.error.message}`);
		}
	}
	console.log(JSON.stringify(results));
} finally {
	const restoreResult = await admin.from('projects').update(original).eq('id', projectId);
	if (restoreResult.error) {
		throw new Error(`본문 최종 원복 실패: ${restoreResult.error.message}`);
	}
}
