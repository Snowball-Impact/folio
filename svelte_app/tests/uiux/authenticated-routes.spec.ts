import { expect, test, type Dialog, type Page } from '@playwright/test';
import { writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { testEnv } from './test-env';

const email = testEnv('test_id', 'FOLIO_TEST_ID');
const password = testEnv('test_pw', 'FOLIO_TEST_PW');
const detailProjectId = testEnv('PLAYWRIGHT_PROJECT_ID');
const mutationProjectId = testEnv('PLAYWRIGHT_MUTATION_PROJECT_ID');
const pbixSafeProjectId = testEnv('PLAYWRIGHT_PBIX_SAFE_PROJECT_ID');
const pbixLiveProjectId = testEnv('PLAYWRIGHT_PBIX_LIVE_PROJECT_ID');
const imageSrc = new URL('/snowball-impact.webp', process.env.PLAYWRIGHT_BASE_URL || 'http://127.0.0.1:5174').toString();

const authenticatedRoutes = [
	{ name: 'my', route: '/my', readySelector: '.profile-overview, .profile-edit-card, .portfolio-section' },
	{ name: 'notifications', route: '/notifications', readySelector: '.notifications-panel' },
	{ name: 'submit', route: '/submit', readySelector: '.project-form' }
];

test.describe('authenticated FOLIO UIUX routes @auth', () => {
	test.skip(!email || !password, 'FOLIO_TEST_ID/FOLIO_TEST_PW 또는 test_id/test_pw가 필요합니다.');

	for (const item of authenticatedRoutes) {
			test(`${item.name} renders authenticated state @auth`, async ({ page }, testInfo) => {
			await signIn(page, item.route);
			await expect(page).toHaveURL(new RegExp(`${escapeRegExp(item.route)}$`));
			await expect(page.locator(item.readySelector).first()).toBeVisible({ timeout: 15_000 });
			await waitForAuthenticatedContent(page, item.name);
			if (testInfo.project.name === 'mobile' && item.name === 'submit') {
				await expect(page.locator('.submit-preview-hero .hero-thumbnail-preview')).toHaveCSS('display', 'none');
			}
			if (item.name === 'notifications') {
				const firstTimestamp = page.locator('.notification-item time').first();
				if (await firstTimestamp.count()) {
					await expect(firstTimestamp).toHaveText(/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$/);
					const firstNotification = page.locator('.notification-item').first();
					const notificationBody = firstNotification.locator(':scope > div');
					const projectButton = firstNotification.getByRole('button', { name: '프로젝트 보기' });
					const bodyBox = await notificationBody.boundingBox();
					const buttonBox = await projectButton.boundingBox();
					const panelBox = await page.locator('.notifications-panel').boundingBox();
					if (bodyBox && buttonBox && panelBox) {
						await expect(buttonBox.y).toBeGreaterThanOrEqual(bodyBox.y + bodyBox.height - 1);
						await expect(buttonBox.x + buttonBox.width).toBeGreaterThanOrEqual(panelBox.x + panelBox.width - 34);
						await expect(buttonBox.width).toBeLessThan(page.viewportSize()?.width ?? 0);
					}
				}
			}
			if (item.name === 'my' && (await page.locator('.portfolio-card-footer .tag').count())) {
				await expect(page.locator('.portfolio-card-footer .tag').first()).toBeVisible();
				await expect(page.locator('.portfolio-card-meta').first()).toBeVisible();
			}
			if (item.name === 'my') {
				const profileBox = await page.locator('.profile-overview').boundingBox();
				const editBox = await page.getByRole('button', { name: '프로필 편집' }).boundingBox();
				if (profileBox && editBox) {
					await expect(editBox.x + editBox.width).toBeGreaterThan(profileBox.x + profileBox.width * 0.65);
				}
			}

			const metrics = await page.evaluate(() => ({
				title: document.title,
				url: window.location.pathname,
				h1: [...document.querySelectorAll('h1')].map((node) => node.textContent?.trim()).filter(Boolean),
				scroll: {
					width: document.documentElement.scrollWidth,
					clientWidth: document.documentElement.clientWidth,
					height: document.documentElement.scrollHeight,
					viewportWidth: window.innerWidth,
					viewportHeight: window.innerHeight
				},
				counts: {
					forms: document.querySelectorAll('form').length,
					buttons: document.querySelectorAll('button').length,
					links: document.querySelectorAll('a').length,
					inputs: document.querySelectorAll('input, textarea, select').length,
					projectCards: document.querySelectorAll('.project-card, .portfolio-card').length,
					notifications: document.querySelectorAll('.notification-item').length,
					iframes: document.querySelectorAll('iframe').length
				}
			}));

			const overflow = metrics.scroll.width - metrics.scroll.clientWidth;
			if (Math.abs(overflow) > 3) {
				throw new Error(`Horizontal overflow detected: ${overflow}px`);
			}

			const metricsPath = testInfo.outputPath('authenticated-metrics.json');
			await writeFile(metricsPath, JSON.stringify(metrics, null, 2), 'utf8');
			await testInfo.attach('authenticated-metrics.json', { path: metricsPath, contentType: 'application/json' });
			await page.screenshot({ path: testInfo.outputPath(`${item.name}-authenticated.png`), fullPage: true });
		});
	}

	test(`my-page profile and delete dialogs cancel safely @auth`, async ({ page }, testInfo) => {
		await signIn(page, '/my');
		await expect(page.locator('.profile-overview')).toBeVisible({ timeout: 15_000 });
		await waitForAuthenticatedContent(page, 'my');

		await page.getByRole('button', { name: '프로필 편집', exact: true }).click();
		await expect(page.locator('.profile-edit-card')).toBeVisible();
		await page.locator('.profile-edit-card').getByRole('button', { name: '취소', exact: true }).click();
		await expect(page.locator('.profile-overview')).toBeVisible();

		const projectCard = page.locator('.portfolio-card').first();
		if (await projectCard.count() === 0) {
			test.skip(true, '삭제 모달을 검증할 인증 프로젝트가 없습니다.');
			return;
		}
		await projectCard.getByRole('button', { name: '삭제', exact: true }).click();
		const deleteDialog = page.getByRole('dialog', { name: '프로젝트 삭제' });
		await expect(deleteDialog).toBeVisible();
		await deleteDialog.getByRole('button', { name: '취소', exact: true }).click();
		await expect(deleteDialog).toHaveCount(0);
		await page.screenshot({ path: testInfo.outputPath('my-interactions.png'), fullPage: true });
	});

	test(`header notification popover opens and closes @auth`, async ({ page }, testInfo) => {
		await signIn(page, '/notifications');
		await expect(page.locator('.notifications-panel')).toBeVisible({ timeout: 15_000 });
		await waitForAuthenticatedContent(page, 'notifications');

		const trigger = page.locator('button.notification-link');
		const popover = page.locator('.notification-submenu');
		await expect(trigger).toHaveAttribute('aria-expanded', 'false');
		await trigger.click();
		await expect(trigger).toHaveAttribute('aria-expanded', 'true');
		await expect(popover).toBeVisible();
		await expect(popover).toContainText('알림');
		await page.screenshot({ path: testInfo.outputPath('notification-popover.png'), fullPage: true });

		await page.keyboard.press('Escape');
		await expect(trigger).toHaveAttribute('aria-expanded', 'false');
		await expect(popover).toBeHidden();
	});

	test(`Power BI menu opens and closes with the trigger @auth`, async ({ page }) => {
		await signIn(page, '/');
		await expect(page.locator('nav.nav')).toBeVisible({ timeout: 15_000 });

		const trigger = page.locator('button.nav-menu-trigger');
		const popover = page.locator('.powerbi-menu .nav-submenu');
		await expect(trigger).toHaveAttribute('aria-expanded', 'false');
		await trigger.click();
		await expect(trigger).toHaveAttribute('aria-expanded', 'true');
		await expect(popover).toBeVisible();
		await expect(popover).toContainText('업데이트 소식');

		await page.keyboard.press('Escape');
		await expect(trigger).toHaveAttribute('aria-expanded', 'false');
		await expect(popover).toBeHidden();
	});

	test(`header notification mark-all-read updates local state without mutation @auth`, async ({ page }) => {
		await signIn(page, '/my');
		await expect(page.locator('.profile-overview')).toBeVisible({ timeout: 15_000 });
		await waitForAuthenticatedContent(page, 'my');

		let markAllPayload: Record<string, unknown> | null = null;
		await page.route('**/rest/v1/notifications**', async (route) => {
			if (route.request().method() === 'GET') {
				await route.fulfill({
					status: 200,
					contentType: 'application/json',
					body: JSON.stringify([
						{
							id: 'uiux-unread-notification',
							user_id: 'uiux-user',
							actor_id: null,
							project_id: null,
							comment_id: null,
							type: 'project_comment',
							title: 'UIUX 읽음 처리 검증',
							body: null,
							is_read: false,
							read_at: null,
							created_at: '2026-08-28T00:00:00.000Z'
						}
					])
				});
				return;
			}
			if (route.request().method() === 'PATCH') {
				markAllPayload = route.request().postDataJSON() as Record<string, unknown>;
				await route.fulfill({ status: 204, body: '' });
				return;
			}
			await route.continue();
		});

		const trigger = page.locator('button.notification-link');
		await trigger.click();
		const popover = page.locator('.notification-submenu');
		await expect(popover).toContainText('UIUX 읽음 처리 검증');
		await expect(popover.getByRole('button', { name: '모두 읽음', exact: true })).toBeVisible();
		await popover.getByRole('button', { name: '모두 읽음', exact: true }).click();
		await expect(popover).toContainText('0개 새 알림');
		await expect(popover.getByRole('button', { name: '모두 읽음', exact: true })).toHaveCount(0);
		expect(markAllPayload).toEqual({ is_read: true, read_at: expect.any(String) });
	});

	test(`notifications matches original read state and header sync @auth`, async ({ page }, testInfo) => {
		const projectId = 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa';
		const title = '국비 직업훈련 시장분석 대시보드 smartHRD에 새 댓글이 남겨졌습니다.';
		let markedAll = false;
		let markAllPayload: Record<string, unknown> | null = null;
		const items = [
			{ id: 'notification-1613', created_at: '2026-08-02T16:13:00+09:00' },
			{ id: 'notification-1555', created_at: '2026-08-02T15:55:00+09:00' },
			{ id: 'notification-1553', created_at: '2026-08-02T15:53:00+09:00' }
		];
		await page.route('**/rest/v1/notifications*', async (route) => {
			const request = route.request();
			if (request.method() === 'GET') {
				await route.fulfill({
					status: 200,
					headers: { 'content-type': 'application/json' },
					body: JSON.stringify(items.map((item, index) => ({
						id: item.id, user_id: 'mock-user', actor_id: null, project_id: projectId, comment_id: null,
						type: 'project_comment', title, body: null,
						is_read: markedAll || index > 0, read_at: markedAll || index > 0 ? '2026-08-02T17:00:00+09:00' : null,
						created_at: item.created_at
					})))
				});
				return;
			}
			if (request.method() === 'PATCH') {
				markedAll = true;
				markAllPayload = request.postDataJSON() as Record<string, unknown>;
				await route.fulfill({ status: 204, body: '' });
				return;
			}
			await route.continue();
		});

		await signIn(page, '/notifications');
		await expect(page.locator('.notifications-panel')).toBeVisible({ timeout: 15_000 });
		await waitForAuthenticatedContent(page, 'notifications');
		await expect(page.locator('.notification-item')).toHaveCount(3);
		await expect(page.locator('.notifications-panel .section-header p')).toHaveText('알림 페이지를 열면 새 알림은 읽음 처리됩니다.');
		await expect(page.locator('.notification-item.read')).toHaveCount(3);
		await expect(page.locator('.notification-item time').nth(0)).toHaveText('2026-08-02 16:13');
		await expect(page.locator('.notification-item time').nth(1)).toHaveText('2026-08-02 15:55');
		await expect(page.locator('.notification-item time').nth(2)).toHaveText('2026-08-02 15:53');
		await expect(page.locator('.notification-item strong')).toHaveCount(3);
		await expect(page.locator('.notification-item strong').first()).toHaveText(title);
		await expect(page.locator('.notification-item').getByRole('button', { name: '프로젝트 보기', exact: true })).toHaveCount(3);
		await expect(page.getByRole('button', { name: '모두 읽음', exact: true })).toHaveCount(0);
		await expect(page.locator('button.notification-link [aria-label$="개 새 알림"]')).toHaveCount(0);
		expect(markAllPayload).toEqual({ is_read: true, read_at: expect.any(String) });

		const metrics = await page.evaluate(() => ({
			itemCount: document.querySelectorAll('.notification-item').length,
			readCount: document.querySelectorAll('.notification-item.read').length,
			projectActionCount: document.querySelectorAll('.notification-item button').length,
			headerUnreadBadge: Boolean(document.querySelector('button.notification-link [aria-label$="개 새 알림"]')),
			scrollWidth: document.documentElement.scrollWidth,
			clientWidth: document.documentElement.clientWidth
		}));
		expect(metrics.itemCount).toBe(3);
		expect(metrics.readCount).toBe(3);
		expect(metrics.projectActionCount).toBe(3);
		expect(metrics.headerUnreadBadge).toBe(false);
		expect(metrics.scrollWidth - metrics.clientWidth).toBeLessThanOrEqual(3);
		const metricsPath = testInfo.outputPath('notifications-same-state-metrics.json');
		await writeFile(metricsPath, JSON.stringify(metrics, null, 2), 'utf8');
		await testInfo.attach('notifications-same-state-metrics.json', { path: metricsPath, contentType: 'application/json' });
		await page.screenshot({ path: testInfo.outputPath('notifications-same-state.png'), fullPage: true });
	});

	test(`header notification project link marks read and navigates @auth`, async ({ page }) => {
		await signIn(page, '/my');
		await expect(page.locator('.portfolio-section')).toBeVisible({ timeout: 15_000 });
		await waitForAuthenticatedContent(page, 'my');
		const projectHref = await page.locator('.portfolio-card').first().getByRole('link', { name: '보기', exact: true }).getAttribute('href');
		if (!projectHref) {
			test.skip(true, '알림 프로젝트 이동에 사용할 인증 프로젝트가 없습니다.');
			return;
		}
		const projectId = projectHref.split('/').at(-1) ?? '';
		let readNotificationId = '';
		await page.route('**/rest/v1/notifications**', async (route) => {
			if (route.request().method() === 'GET') {
				await route.fulfill({
					status: 200,
					contentType: 'application/json',
					body: JSON.stringify([
						{
							id: 'uiux-project-notification',
							user_id: 'uiux-user',
							actor_id: null,
							project_id: projectId,
							comment_id: null,
							type: 'project_comment',
							title: 'UIUX 프로젝트 이동 검증',
							body: null,
							is_read: false,
							read_at: null,
							created_at: '2026-08-28T00:00:00.000Z'
						}
					])
				});
				return;
			}
			if (route.request().method() === 'PATCH') {
				readNotificationId = route.request().url().match(/id=eq\.([^&]+)/)?.[1] ?? '';
				await route.fulfill({ status: 204, body: '' });
				return;
			}
			await route.continue();
		});

		// AuthNav can finish its initial real notification request after sign-in.
		// Reload after installing the mock so the clicked item and PATCH id are deterministic.
		await page.reload();
		await expect(page.locator('.portfolio-section')).toBeVisible({ timeout: 15_000 });
		await waitForAuthenticatedContent(page, 'my');
		await page.locator('button.notification-link').click();
		await page
			.locator('.notification-submenu .notification-preview')
			.filter({ hasText: 'UIUX 프로젝트 이동 검증' })
			.click();
		await expect(page).toHaveURL(new RegExp(`/projects/${escapeRegExp(projectId)}$`), { timeout: 15_000 });
		expect(readNotificationId).toBe('uiux-project-notification');
	});

	test(`my-page profile save sends normalized values without mutation @auth`, async ({ page }) => {
		await signIn(page, '/my');
		await expect(page.locator('.profile-overview')).toBeVisible({ timeout: 15_000 });
		await waitForAuthenticatedContent(page, 'my');

		let profilePayload: Record<string, unknown> | null = null;
		await page.route('**/rest/v1/profiles**', async (route) => {
			if (route.request().method() !== 'PATCH') {
				await route.continue();
				return;
			}
			profilePayload = route.request().postDataJSON() as Record<string, unknown>;
			await route.fulfill({ status: 204, body: '' });
		});

		await page.getByRole('button', { name: '프로필 편집', exact: true }).click();
		await expect(page.locator('.profile-edit-card')).toBeVisible();
		const nameInput = page.locator('.profile-edit-card input').first();
		const originalName = await nameInput.inputValue();
		await nameInput.fill(` ${originalName} `);
		await page.getByRole('button', { name: '변경사항 저장', exact: true }).click();
		await expect(page.locator('.profile-edit-card')).toHaveCount(0);
		await expect(page.locator('.auth-message.success')).toContainText('프로필이 업데이트됐습니다.');
		expect(profilePayload).toEqual({ name: originalName, organization: expect.any(String), bio: expect.any(String) });
	});

	test(`my-page matches original populated profile and portfolio state @auth`, async ({ page }, testInfo) => {
		const projectId = 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa';
		const authorId = 'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb';
		const project = {
			id: projectId,
			author_id: authorId,
			title: '국비 직업훈련 시장분석 대시보드 smartHRD',
			one_liner: '직업훈련기관의 데이터 기반 의사결정을 지원하는 AI 운영지원 플랫폼',
			problem: 'mock problem', dataset: 'mock dataset', process: 'mock process', insights: 'mock insights',
			tags: ['powerbi', '내일배움카드', '직업훈련', '시장분석', '상권분석', '국비'],
			thumbnail_url: null, thumbnail_mode: 'auto_cover', power_bi_url: null, report_url: null, github_url: null,
			platform_key: 'powerbi', project_type: 'powerbi', status: 'published', embed_status: 'external_only',
			is_public: true, view_count: 23,
			created_at: '2026-08-20T09:00:00.000Z', updated_at: '2026-08-20T09:00:00.000Z'
		};

		await page.route('**/rest/v1/profiles*', async (route) => {
			if (route.request().method() !== 'GET') return route.continue();
			await route.fulfill({ status: 200, headers: { 'content-type': 'application/json' }, body: JSON.stringify({
				id: authorId, email: 'ggmaeng@gmail.com', name: '맹광국', organization: '스노우볼 임팩트', bio: null
			}) });
		});
		await page.route('**/rest/v1/projects*', async (route) => {
			if (route.request().method() !== 'GET') return route.continue();
			await route.fulfill({ status: 200, headers: { 'content-type': 'application/json' }, body: JSON.stringify([project]) });
		});
		await page.route('**/rest/v1/public_profiles*', (route) => route.fulfill({
			status: 200, headers: { 'content-type': 'application/json' },
			body: JSON.stringify([{ id: authorId, name: '맹광국', organization: '스노우볼 임팩트' }])
		}));
		await page.route('**/rest/v1/likes*', (route) => route.fulfill({
			status: 200, headers: { 'content-type': 'application/json' },
			body: JSON.stringify([{ project_id: projectId }, { project_id: projectId }])
		}));
		await page.route('**/rest/v1/comments*', (route) => route.fulfill({
			status: 200, headers: { 'content-type': 'application/json' },
			body: JSON.stringify(Array.from({ length: 9 }, (_, index) => ({
				project_id: projectId, author_id: `comment-author-${index}`,
				created_at: `2026-08-${String(20 - (index % 9)).padStart(2, '0')}T09:00:00.000Z`
			})))
		}));
		await page.route('**/rest/v1/project_comment_reads*', (route) => route.fulfill({
			status: 200, headers: { 'content-type': 'application/json' },
			body: JSON.stringify([{ project_id: projectId, last_read_at: '2026-08-30T00:00:00.000Z' }])
		}));

		await signIn(page, '/my');
		await expect(page.locator('.profile-overview')).toBeVisible({ timeout: 15_000 });
		await waitForAuthenticatedContent(page, 'my');
		const profile = page.locator('.profile-overview');
		await expect(profile).toContainText('맹광국');
		await expect(profile).toContainText('스노우볼 임팩트');
		await expect(profile).toContainText('ggmaeng@gmail.com');
		await expect(profile.locator('.profile-stats')).toContainText('전체 프로젝트1');
		await expect(profile.locator('.profile-stats')).toContainText('공개 프로젝트1');
		await expect(profile.locator('.profile-stats')).toContainText('누적 조회23');
		await expect(profile.locator('.profile-stats')).toContainText('총 좋아요2');

		const card = page.locator('.portfolio-card');
		await expect(card).toHaveCount(1);
		await expect(card).toContainText(project.title);
		await expect(card).toContainText(project.one_liner);
		await expect(card.locator('.portfolio-card-footer .tag')).toHaveCount(6);
		await expect(card.locator('.portfolio-card-meta [aria-label="조회수 23"]')).toBeVisible();
		await expect(card.locator('.portfolio-card-meta [aria-label="좋아요 2"]')).toBeVisible();
		await expect(card.locator('.portfolio-card-meta [aria-label="댓글 9"]')).toBeVisible();
		await expect(card.locator('[aria-label="공개 상태 공개"]')).toBeVisible();
		await expect(card.locator('.portfolio-unread-badge')).toHaveCount(0);
		await expect(card.getByRole('link', { name: '보기', exact: true })).toBeVisible();
		await expect(card.getByRole('link', { name: '수정', exact: true })).toBeVisible();
		await expect(card.getByRole('button', { name: '삭제', exact: true })).toBeVisible();

		await card.getByRole('button', { name: '삭제', exact: true }).click();
		const dialog = page.getByRole('dialog', { name: '프로젝트 삭제' });
		await expect(dialog).toContainText(project.title);
		await page.screenshot({ path: testInfo.outputPath('my-same-fixture-delete-confirm.png'), fullPage: true });
		await dialog.getByRole('button', { name: '취소', exact: true }).click();
		await expect(dialog).toHaveCount(0);

		const metrics = await page.evaluate(() => ({
			profileStats: document.querySelector('.profile-stats')?.textContent?.replace(/\s+/g, ' ').trim() ?? '',
			cardCount: document.querySelectorAll('.portfolio-card').length,
			cardFooter: document.querySelector('.portfolio-card-footer')?.textContent?.replace(/\s+/g, ' ').trim() ?? '',
			actionCount: document.querySelectorAll('.portfolio-actions a, .portfolio-actions button').length,
			scrollWidth: document.documentElement.scrollWidth, clientWidth: document.documentElement.clientWidth
		}));
		expect(metrics.cardCount).toBe(1);
		expect(metrics.actionCount).toBe(3);
		expect(metrics.scrollWidth - metrics.clientWidth).toBeLessThanOrEqual(3);
		const metricsPath = testInfo.outputPath('my-same-fixture-metrics.json');
		await writeFile(metricsPath, JSON.stringify(metrics, null, 2), 'utf8');
		await testInfo.attach('my-same-fixture-metrics.json', { path: metricsPath, contentType: 'application/json' });
		await page.screenshot({ path: testInfo.outputPath('my-same-fixture.png'), fullPage: true });
	});

	test(`submit controls preserve preview and draft states @auth`, async ({ page }, testInfo) => {
		await signIn(page, '/submit');
		await expect(page.locator('form.project-form')).toBeVisible({ timeout: 15_000 });
		await clearSubmitDrafts(page);
		await page.reload({ waitUntil: 'networkidle' });
		await expect(page.locator('form.project-form')).toBeVisible({ timeout: 15_000 });
		const autoCover = page.locator('.hero-thumbnail-preview .folio-auto-cover');
		await expect(autoCover).toHaveClass(/folio-auto-cover-18/);
		await expect.poll(() => autoCover.evaluate((node) => getComputedStyle(node).backgroundImage)).toContain('rgb(163, 95, 183)');
		if (testInfo.project.name === 'desktop') {
			await expect(page.locator('.hero-thumbnail-preview .card-preview-author')).toHaveText('작성자');
			await expect(page.locator('.hero-thumbnail-preview .card-meta-bottom [aria-label="조회수 0"]')).toBeVisible();
			await expect(page.locator('.hero-thumbnail-preview .card-meta-bottom [aria-label="좋아요 0"]')).toBeVisible();
			await expect(page.locator('.hero-thumbnail-preview .card-meta-bottom [aria-label="댓글 0"]')).toBeVisible();
		}
		await expect(page.locator('.project-form-overview-column').first().getByRole('button', { name: '프로젝트명 도움말' })).toHaveAttribute('title', /최대 48자/);
		await expect(page.locator('.project-form-overview-column').first().locator('.field-label-row').nth(2)).toContainText('태그');
		await page.locator('.platform-panel input[type="radio"][value="powerbi"]').check();
		await expect(page.locator('.project-form-overview-column').first().locator('.field-label-row').nth(2)).toContainText('#Power BI');
		await page.getByPlaceholder('공공데이터, 시각화, 취업').fill('PowerBI, 분석');
		const tagLabelText = await page.locator('.project-form-overview-column').first().locator('.field-label-row').nth(2).innerText();
		expect(tagLabelText).toContain('#Power BI');
		expect(tagLabelText).toContain('#분석');
		expect(tagLabelText).not.toContain('#PowerBI');
		await page.getByPlaceholder('공공데이터, 시각화, 취업').fill('');
		await page.locator('.platform-panel input[type="radio"][value="other"]').check();
		await page.screenshot({ path: testInfo.outputPath('submit-empty-baseline.png'), fullPage: true });
		const formatSelect = page.locator('.rich-editor-format-select');
		await expect(page.locator('.rich-editor-toolbar-group')).toHaveCount(7);
		expect(
			await page.locator('.rich-editor-toolbar-group').evaluateAll((groups) =>
				groups.map((group) => group.getAttribute('aria-label'))
			)
		).toEqual(['글자 서식', '색상', '목록과 정렬', '문단 형식과 크기', '고급 블록 서식', '링크와 이미지', '글꼴']);
		const toolbarButton = page.locator('.rich-editor-toolbar button').first();
		const toolbarButtonStyle = await toolbarButton.evaluate((button) => ({
			borderStyle: getComputedStyle(button).borderStyle,
			height: getComputedStyle(button).height
		}));
		expect(toolbarButtonStyle.borderStyle).toBe('none');
		expect(toolbarButtonStyle.height).toBe('24px');
		await toolbarButton.hover();
		await expect.poll(() => toolbarButton.evaluate((button) => getComputedStyle(button).color)).toBe('rgb(20, 89, 200)');
		await expect(formatSelect).toHaveValue('paragraph');
		await expect(formatSelect.locator('option')).toHaveText(['Normal', 'H1', 'H2', 'H3', 'H4', 'H5', 'H6']);
		await page.locator('.rich-editor .tiptap h2').first().click();
		await expect(formatSelect).toHaveValue('heading2');
		await formatSelect.selectOption('heading3');
		await expect(page.locator('.rich-editor .tiptap h3').first()).toBeVisible();
		await formatSelect.selectOption('heading1');
		await expect(page.locator('.rich-editor .tiptap h1').first()).toBeVisible();
		await formatSelect.selectOption('heading6');
		await expect(page.locator('.rich-editor .tiptap h6').first()).toBeVisible();
		await formatSelect.selectOption('heading2');
		await expect(page.locator('.rich-editor .tiptap h2').first()).toBeVisible();
		const editorContent = page.locator('.rich-editor .tiptap');
		await editorContent.click();
		await page.keyboard.press('Control+a');
		const colorSelect = page.locator('.rich-editor-color-select');
		await expect(colorSelect).toHaveValue('#8a98ad');
		await colorSelect.selectOption('#1459c8');
		await expect(editorContent.locator('span[style*="color"]').first()).toBeVisible();
		const highlightSelect = page.locator('.rich-editor-highlight-select');
		await expect(highlightSelect).toHaveValue('default');
		await highlightSelect.selectOption('#fff2a8');
		await expect(editorContent.locator('mark').first()).toBeVisible();
		const fontSelect = page.locator('.rich-editor-font-select');
		await expect(fontSelect).toHaveValue('default');
		await fontSelect.selectOption('serif');
		await expect(editorContent.locator('span[style*="font-family"]').first()).toBeVisible();
		const sizeSelect = page.locator('.rich-editor-size-select');
		await expect(sizeSelect).toHaveValue('default');
		await sizeSelect.selectOption('1.5em');
		await expect(editorContent.locator('span[style*="font-size: 1.5em"]').first()).toBeVisible();
		await editorContent.locator('h2').first().selectText();
		await page.getByTitle('들여쓰기').click();
		await expect(editorContent.locator('[data-indent="1"]')).toHaveCount(1);
		await page.getByTitle('내어쓰기').click();
		await expect(editorContent.locator('[data-indent]')).toHaveCount(0);
		await editorContent.click();
		await page.keyboard.press('Control+a');
		await page.getByTitle('위첨자').click();
		await expect(editorContent.locator('sup').first()).toBeVisible();
		await page.getByTitle('아래첨자').click();
		await expect(editorContent.locator('sub').first()).toBeVisible();
		await editorContent.click();
		await page.keyboard.press('Control+End');
		let imagePrompt = 0;
		const handleImageDialog = async (dialog: Dialog) => {
			expect(dialog.type()).toBe('prompt');
			if (imagePrompt++ === 0) {
				expect(dialog.message()).toContain('이미지 URL');
				await dialog.accept(imageSrc);
				return;
			}
			expect(dialog.message()).toContain('이미지 설명');
			await dialog.accept('분석 결과 차트');
		};
		page.on('dialog', handleImageDialog);
		await page.getByTitle('이미지 삽입').click();
		await expect(editorContent.locator(`img[src="${imageSrc}"]`)).toHaveAttribute('alt', '분석 결과 차트');
		page.off('dialog', handleImageDialog);
		page.once('dialog', async (dialog) => {
			expect(dialog.type()).toBe('prompt');
			expect(dialog.message()).toContain('수식 입력');
			await dialog.accept('x^2 + y^2 = z^2');
		});
		await page.getByTitle('수식 삽입').click();
		await expect(editorContent.locator('[data-type="inline-math"][data-latex="x^2 + y^2 = z^2"]')).toBeVisible();
		const bodyImageInput = page.locator('[data-body-image-input]');
		await bodyImageInput.setInputFiles(resolve(process.cwd(), '..', 'artifacts', 'test1_thumbnail.jpg'));
		await expect(editorContent.locator('img[alt="test1_thumbnail.jpg"]')).toHaveCount(1);

		await page.getByPlaceholder('예: 서울시 청년 취업 데이터 분석').fill('상태 검증 프로젝트');
		await page.getByPlaceholder('핵심 메시지를 한 문장으로 적어주세요.').fill('입력 상태를 검증합니다.');

		const thumbnailPanel = page.locator('.thumbnail-panel');
		await page.locator('input[type="radio"][value="upload"]').check();
		const thumbnailInput = thumbnailPanel.locator('input[type="file"]');
		await expect(thumbnailInput).toBeVisible();
		await thumbnailInput.setInputFiles(resolve(process.cwd(), '..', 'artifacts', 'test1_thumbnail.jpg'));
		expect(await thumbnailInput.evaluate((input: HTMLInputElement) => input.files?.length ?? 0)).toBe(1);

		await page.locator('input[type="radio"][value="manual_url"]').check();
		await thumbnailPanel.getByPlaceholder('https://...').fill('https://example.com/thumbnail.png');
		await expect(page.locator('.hero-thumbnail-preview img')).toHaveAttribute('src', 'https://example.com/thumbnail.png');

		await page.locator('input[type="radio"][value="capture"]').check();
		await expect(page.getByText('Embed Code 또는 Web App URL 기준으로 대표 이미지를 생성합니다.')).toBeVisible();

		await page.locator('input[type="radio"][value="powerbi"]').check();
		const pbixInput = page.locator('input[type="file"][accept=".pbix"]');
		await expect(pbixInput).toBeVisible();
		await pbixInput.setInputFiles(resolve(process.cwd(), '..', 'artifacts', 'test.pbix'));
		expect(await pbixInput.evaluate((input: HTMLInputElement) => input.files?.length ?? 0)).toBe(1);

		await page.locator('summary', { hasText: '본문 미리보기' }).click();
		const bodyPreview = page.locator('.rich-editor-preview-content');
		await expect(bodyPreview).toBeVisible();
		await expect(bodyPreview.locator('h2')).toHaveCount(4);
		await expect(bodyPreview.locator('span[style*="color"]').first()).toBeVisible();
		await expect(bodyPreview.locator(`img[src="${imageSrc}"]`)).toHaveAttribute('alt', '분석 결과 차트');
		await expect(bodyPreview.locator('img[alt="test1_thumbnail.jpg"]')).toHaveCount(1);
		await expect(bodyPreview.locator('[data-type="inline-math"]')).toBeVisible();
		await expect(bodyPreview.locator('.katex')).toBeVisible();
		await page.evaluate(() => window.scrollTo({ top: 0, behavior: 'instant' }));
		await expect.poll(() => page.evaluate(() => window.scrollY)).toBe(0);
		await page.screenshot({ path: testInfo.outputPath('submit-controls.png'), fullPage: true });

		await page.getByRole('button', { name: '초안 지우기', exact: true }).click();
		await expect(page.getByPlaceholder('예: 서울시 청년 취업 데이터 분석')).toHaveValue('');
		await clearSubmitDrafts(page);
	});

	test(`submit validation blocks incomplete states with an alert @auth`, async ({ page }) => {
		await signIn(page, '/submit');
		await expect(page.locator('form.project-form')).toBeVisible({ timeout: 15_000 });
		await clearSubmitDrafts(page);
		await page.reload({ waitUntil: 'networkidle' });
		await expect(page.locator('form.project-form')).toBeVisible({ timeout: 15_000 });

		let projectPostCount = 0;
		page.on('request', (request) => {
			if (request.method() === 'POST' && new URL(request.url()).pathname.endsWith('/rest/v1/projects')) {
				projectPostCount += 1;
			}
		});

		const submitButton = page.getByRole('button', { name: '프로젝트 등록하기', exact: true });
		await submitButton.click();
		await expect(page.locator('#project-form-error')).toHaveAttribute('role', 'alert');
		await expect(page.locator('#project-form-error')).toContainText('프로젝트명을 입력하세요.');

		await page.getByPlaceholder('예: 서울시 청년 취업 데이터 분석').fill('검증 프로젝트');
		await page.getByPlaceholder('https://github.com/...').fill('invalid-url');
		await submitButton.click();
		await expect(page.locator('#project-form-error')).toContainText('GitHub URL은 http:// 또는 https://로 시작해야 합니다.');
		await page.getByPlaceholder('https://github.com/...').fill('');

		await page.locator('.thumbnail-choice-panel input[type="radio"][value="manual_url"]').check();
		await page.locator('.thumbnail-panel input[placeholder="https://..."]').fill('javascript:bad');
		await submitButton.click();
		await expect(page.locator('#project-form-error')).toContainText('썸네일 URL은 http:// 또는 https://로 시작해야 합니다.');

		await page.locator('.thumbnail-choice-panel input[type="radio"][value="capture"]').check();
		await page.locator('input[placeholder="https://... 또는 iframe 코드"]').fill('');
		await page.getByPlaceholder('https://...').last().fill('');
		await submitButton.click();
		await expect(page.locator('#project-form-error')).toContainText('자동 캡처를 사용하려면 Embed Code, Web App URL, 또는 PBIX 파일이 필요합니다.');

		await page.locator('.thumbnail-choice-panel input[type="radio"][value="upload"]').check();
		await submitButton.click();
		await expect(page.locator('#project-form-error')).toContainText('업로드할 썸네일 이미지를 선택하세요.');
		await expect(page.getByPlaceholder('예: 서울시 청년 취업 데이터 분석')).toHaveValue('검증 프로젝트');
		expect(projectPostCount).toBe(0);
	});

	test(`edit page loads existing project state without mutation @auth`, async ({ page }, testInfo) => {
		await signIn(page, '/my');
		await expect(page.locator('.portfolio-section')).toBeVisible({ timeout: 15_000 });
		await waitForAuthenticatedContent(page, 'my');

		const projectCard = page.locator('.portfolio-card').first();
		if (await projectCard.count() === 0) {
			test.skip(true, '수정 페이지 검증에 사용할 인증 프로젝트가 없습니다.');
			return;
		}
		const editHref = await projectCard.getByRole('link', { name: '수정', exact: true }).getAttribute('href');
		const projectTitle = await projectCard.locator('.portfolio-title-line strong').innerText();
		if (!editHref) {
			test.skip(true, '프로젝트 카드에 수정 링크가 없습니다.');
			return;
		}

		await page.goto(editHref, { waitUntil: 'networkidle' });
		await expect(page.locator('form.project-form')).toBeVisible({ timeout: 15_000 });
		await expect(page.locator('.edit-hero')).toBeVisible();
		await expect(page.locator('.edit-hero')).toContainText('프로젝트 정보와 대표 썸네일을 업데이트하세요.');
		await expect(page.getByPlaceholder('예: 서울시 청년 취업 데이터 분석')).toHaveValue(projectTitle);
		await expect(
			page.locator(
				'input[type="radio"][value="auto_cover"], input[type="radio"][value="upload"], input[type="radio"][value="manual_url"], input[type="radio"][value="capture"]'
			).first()
		).toBeAttached();

		const editState = await page.evaluate(() => ({
			title: (document.querySelector('input[placeholder^="예: 서울시"]') as HTMLInputElement | null)?.value ?? '',
			platform: (document.querySelector('.platform-panel input[type="radio"]:checked') as HTMLInputElement | null)?.value ?? null,
			thumbnailMode: (document.querySelector('input[type="radio"][value="auto_cover"]:checked, input[type="radio"][value="upload"]:checked, input[type="radio"][value="manual_url"]:checked, input[type="radio"][value="capture"]:checked') as HTMLInputElement | null)?.value ?? null,
			hasExistingThumbnailDelete: Boolean(document.querySelector('.thumbnail-panel .delete-option-row input[type="checkbox"]')),
			hasExistingPbixDelete: Boolean(document.querySelector('.platform-panel .delete-option-row input[type="checkbox"]')),
			bodyHeadings: [...document.querySelectorAll('.rich-editor-content h2')].map((node) => node.textContent?.trim()).filter(Boolean),
			preview: Boolean(document.querySelector('.hero-thumbnail-preview .project-card')),
			scrollWidth: document.documentElement.scrollWidth,
			clientWidth: document.documentElement.clientWidth
		}));
		expect(editState.title).toBe(projectTitle);
		expect(editState.thumbnailMode).not.toBeNull();
		expect(editState.preview).toBe(true);
		expect(editState.scrollWidth - editState.clientWidth).toBeLessThanOrEqual(3);
		const editFormatSelect = page.locator('.rich-editor-format-select');
		await expect(editFormatSelect).toBeVisible();
		await expect(editFormatSelect.locator('option')).toHaveText(['Normal', 'H1', 'H2', 'H3', 'H4', 'H5', 'H6']);
		await page.locator('.rich-editor .tiptap h2').first().click();
		await expect(editFormatSelect).toHaveValue('heading2');
		await expect(page.locator('.rich-editor-size-select')).toBeVisible();
		await expect(page.locator('.rich-editor-size-select option')).toHaveText(['Normal', 'Small', 'Large', 'Huge']);
		await page.locator('.rich-editor-format-select').selectOption('heading6');
		await expect(page.locator('.rich-editor .tiptap h6').first()).toBeVisible();
		await page.locator('.rich-editor-format-select').selectOption('heading2');
		if (editState.hasExistingPbixDelete) {
			const deletePbix = page.locator('.platform-panel .delete-option-row input[type="checkbox"]');
			await expect(deletePbix).toBeVisible();
			await deletePbix.check();
			await expect(page.locator('.pbix-upload-field input[type="file"][accept=".pbix"]')).toBeVisible();
			await deletePbix.uncheck();
			await expect(page.locator('.pbix-upload-field input[type="file"][accept=".pbix"]')).toHaveCount(0);
		}
		if (editState.hasExistingThumbnailDelete) {
			const deleteThumbnail = page.locator('.thumbnail-panel .delete-option-row input[type="checkbox"]');
			await page.locator('.thumbnail-choice-panel input[type="radio"][value="upload"]').check();
			await deleteThumbnail.check();
			await expect(page.locator('.thumbnail-panel input[type="file"][accept="image/jpeg,image/png,image/webp"]')).toBeVisible();
			await deleteThumbnail.uncheck();
			await expect(page.locator('.thumbnail-panel input[type="file"][accept="image/jpeg,image/png,image/webp"]')).toHaveCount(0);
			await page.locator('.thumbnail-choice-panel input[type="radio"][value="auto_cover"]').check();
		}
		await page.locator('summary', { hasText: '본문 미리보기' }).click();
		await expect(page.locator('.rich-editor-preview-content')).toBeVisible();
		await expect(page.locator('.rich-editor-preview-content h2')).toHaveCount(4);
		await page.evaluate(() => window.scrollTo({ top: 0, behavior: 'instant' }));
		await expect.poll(() => page.evaluate(() => window.scrollY)).toBe(0);
		await page.screenshot({ path: testInfo.outputPath('edit-existing-state.png'), fullPage: true });

		await page.getByRole('link', { name: '목록으로 돌아가기', exact: true }).click();
		await expect(page).toHaveURL(/\/my$/);
	});

	test(`edit save request and detail navigation stay non-mutating @auth`, async ({ page }, testInfo) => {
		await signIn(page, '/my');
		await expect(page.locator('.portfolio-section')).toBeVisible({ timeout: 15_000 });
		await waitForAuthenticatedContent(page, 'my');

		const projectCard = page
			.locator('.portfolio-card')
			.filter({ has: page.locator('[aria-label="공개 상태 공개"]') })
			.filter({ hasNotText: /처리 중|게시 실패/ })
			.first();
		if (await projectCard.count() === 0) {
			test.skip(true, '공개 상세 저장 흐름 검증에 사용할 인증 프로젝트가 없습니다.');
			return;
		}
		const editHref = await projectCard.getByRole('link', { name: '수정', exact: true }).getAttribute('href');
		if (!editHref) {
			test.skip(true, '프로젝트 카드에 수정 링크가 없습니다.');
			return;
		}

		await page.goto(editHref, { waitUntil: 'networkidle' });
		await expect(page.locator('form.project-form')).toBeVisible({ timeout: 15_000 });
		const projectId = editHref.split('/').at(-2);
		const originalTitle = await page.getByPlaceholder('예: 서울시 청년 취업 데이터 분석').inputValue();
		let updatePayload: Record<string, unknown> | null = null;
		await page.route('**/rest/v1/projects**', async (route) => {
			if (route.request().method() !== 'PATCH') {
				await route.continue();
				return;
			}
			updatePayload = route.request().postDataJSON() as Record<string, unknown>;
			await route.fulfill({ status: 204, body: '' });
		});

		await page.locator('input[type="radio"][value="auto_cover"]').check();
		await page.getByRole('button', { name: '수정 완료', exact: true }).click();
		await expect(page).toHaveURL(new RegExp(`/projects/${escapeRegExp(projectId ?? '')}$`), { timeout: 15_000 });
		const capturedPayload = updatePayload;
		expect(capturedPayload).not.toBeNull();
		expect((capturedPayload as Record<string, unknown> | null)?.title).toBe(originalTitle);
		// The original stores the editor body in the four project content columns,
		// so the save payload must retain the structured HTML section content.
		for (const key of ['problem', 'dataset', 'process', 'insights']) {
			const sectionHtml = (capturedPayload as Record<string, unknown> | null)?.[key];
			expect(typeof sectionHtml).toBe('string');
			expect(String(sectionHtml)).toMatch(/<p[ >]/);
		}
		expect(String((capturedPayload as Record<string, unknown> | null)?.problem)).not.toContain('<h2>');
		if (await page.getByRole('heading', { name: '404', exact: true }).count()) {
			test.skip(true, '저장 payload는 검증했지만 인증 계정에 공개 상세 fixture가 없어 상세 렌더링은 확인하지 못했습니다.');
			return;
		}
		await expect(page.locator('.detail-hero')).toBeVisible({ timeout: 15_000 });
		await expect(page.locator('.detail-hero h1')).toHaveText(originalTitle);
		await page.screenshot({ path: testInfo.outputPath('edit-save-detail-navigation.png'), fullPage: true });
	});

	test(`real edit persistence fixture restores its original value @mutation`, async ({ page }, testInfo) => {
		test.skip(!mutationProjectId, 'PLAYWRIGHT_MUTATION_PROJECT_ID가 지정된 경우에만 실제 저장 fixture를 실행합니다.');
		const editHref = `/projects/${mutationProjectId}/edit`;
		await signIn(page, editHref);
		await expect(page.locator('form.project-form')).toBeVisible({ timeout: 15_000 });
		const oneLinerInput = page.getByPlaceholder('핵심 메시지를 한 문장으로 적어주세요.');
		const originalOneLiner = await oneLinerInput.inputValue();
		const thumbnailMode = await page.locator('.thumbnail-choice-panel input[type="radio"]:checked').inputValue();
		if (!['auto_cover', 'manual_url'].includes(thumbnailMode)) {
			test.skip(true, `실제 저장 fixture의 썸네일 모드(${thumbnailMode})는 side effect 격리 조건에 맞지 않습니다.`);
			return;
		}

		const marker = `UIUX 저장 반영 검증 ${Date.now()}`;
		try {
			await oneLinerInput.fill(marker);
			await page.getByRole('button', { name: '수정 완료', exact: true }).click();
			await expect(page).toHaveURL(new RegExp(`/projects/${escapeRegExp(mutationProjectId!)}$`), { timeout: 20_000 });
			await expect(page.locator('.detail-hero-copy > p')).toHaveText(marker);

			await page.goto(editHref, { waitUntil: 'networkidle' });
			await expect(page.locator('form.project-form')).toBeVisible({ timeout: 15_000 });
			await expect(page.getByPlaceholder('핵심 메시지를 한 문장으로 적어주세요.')).toHaveValue(marker);

			await page.goto('/my', { waitUntil: 'networkidle' });
			await expect(page.locator('.portfolio-section')).toBeVisible({ timeout: 15_000 });
			await waitForAuthenticatedContent(page, 'my');
			await expect(page.locator('.portfolio-card').filter({ hasText: marker })).toBeVisible();
			await page.screenshot({ path: testInfo.outputPath('real-edit-persistence.png'), fullPage: true });
		} finally {
			await page.goto(editHref, { waitUntil: 'networkidle' });
			await expect(page.locator('form.project-form')).toBeVisible({ timeout: 15_000 });
			await page.getByPlaceholder('핵심 메시지를 한 문장으로 적어주세요.').fill(originalOneLiner);
			await page.getByRole('button', { name: '수정 완료', exact: true }).click();
			await expect(page).toHaveURL(new RegExp(`/projects/${escapeRegExp(mutationProjectId!)}$`), { timeout: 20_000 });
			await page.goto(editHref, { waitUntil: 'networkidle' });
			await expect(page.locator('form.project-form')).toBeVisible({ timeout: 15_000 });
			await expect(page.getByPlaceholder('핵심 메시지를 한 문장으로 적어주세요.')).toHaveValue(originalOneLiner);
		}
	});

	test(`real thumbnail upload fixture restores auto cover @mutation-thumbnail`, async ({ page }, testInfo) => {
		test.skip(!mutationProjectId, 'PLAYWRIGHT_MUTATION_PROJECT_ID가 지정된 경우에만 실제 썸네일 fixture를 실행합니다.');
		const editHref = `/projects/${mutationProjectId}/edit`;
		await signIn(page, editHref);
		await expect(page.locator('form.project-form')).toBeVisible({ timeout: 15_000 });
		const initialThumbnailMode = await page.locator('.thumbnail-choice-panel input[type="radio"]:checked').inputValue();
		const hasExistingThumbnail = (await page.locator('.thumbnail-panel .delete-option-row').count()) > 0;
		if (initialThumbnailMode !== 'auto_cover' || hasExistingThumbnail) {
			test.skip(true, '기존 썸네일이 없는 auto_cover fixture에서만 업로드/복구 테스트를 실행합니다.');
			return;
		}

		const thumbnailPath = resolve(process.cwd(), '..', 'artifacts', 'test1_thumbnail.jpg');
		try {
			await page.locator('.thumbnail-choice-panel input[type="radio"][value="upload"]').check();
			const thumbnailInput = page.locator('.thumbnail-panel input[type="file"][accept="image/jpeg,image/png,image/webp"]');
			await expect(thumbnailInput).toBeVisible();
			await thumbnailInput.setInputFiles(thumbnailPath);
			await expect(page.locator('.hero-thumbnail-preview img')).toHaveCount(1);
			await page.getByRole('button', { name: '수정 완료', exact: true }).click();
			await expect(page).toHaveURL(new RegExp(`/projects/${escapeRegExp(mutationProjectId!)}$`), { timeout: 30_000 });
			await expect(page.locator('.detail-hero .project-card img')).toHaveCount(1, { timeout: 15_000 });

			await page.goto(editHref, { waitUntil: 'networkidle' });
			await expect(page.locator('form.project-form')).toBeVisible({ timeout: 15_000 });
			await expect(page.locator('.thumbnail-choice-panel input[type="radio"][value="upload"]')).toBeChecked();
			await expect(page.locator('.thumbnail-panel .delete-option-row input[type="checkbox"]')).toBeVisible();
			await page.screenshot({ path: testInfo.outputPath('real-thumbnail-upload.png'), fullPage: true });
		} finally {
			await page.goto(editHref, { waitUntil: 'networkidle' });
			await expect(page.locator('form.project-form')).toBeVisible({ timeout: 15_000 });
			await page.locator('.thumbnail-choice-panel input[type="radio"][value="auto_cover"]').check();
			const deleteThumbnail = page.locator('.thumbnail-panel .delete-option-row input[type="checkbox"]');
			if (await deleteThumbnail.count()) {
				await deleteThumbnail.check();
			}
			await page.getByRole('button', { name: '수정 완료', exact: true }).click();
			await expect(page).toHaveURL(new RegExp(`/projects/${escapeRegExp(mutationProjectId!)}$`), { timeout: 30_000 });
			await expect(page.locator('.detail-hero .project-card img')).toHaveCount(0, { timeout: 15_000 });
		}
	});

	test(`PBIX publish failure preserves the existing embed connection @mutation-pbix-safe`, async ({ page }, testInfo) => {
		test.skip(!pbixSafeProjectId, 'PLAYWRIGHT_PBIX_SAFE_PROJECT_ID가 지정된 경우에만 PBIX 실패 안전 테스트를 실행합니다.');
		const editHref = `/projects/${pbixSafeProjectId}/edit`;
		await signIn(page, editHref);
		await expect(page.locator('form.project-form')).toBeVisible({ timeout: 15_000 });
		const powerBiRadio = page.locator('.platform-panel input[type="radio"][value="powerbi"]');
		if (!(await powerBiRadio.isChecked())) {
			test.skip(true, 'PBIX 실패 안전 테스트에는 Power BI fixture가 필요합니다.');
			return;
		}
		const existingEmbedUrl = await page.locator('input[placeholder="https://... 또는 iframe 코드"]').inputValue();
		if (!existingEmbedUrl) {
			test.skip(true, '기존 Power BI Embed URL이 있는 fixture가 필요합니다.');
			return;
		}
		const deletePbix = page.locator('.platform-panel .delete-option-row input[type="checkbox"]');
		if (!(await deletePbix.count())) {
			test.skip(true, '기존 Power BI 게시본 연결이 있는 fixture가 필요합니다.');
			return;
		}
		await deletePbix.check();
		const pbixInput = page.locator('input[type="file"][accept=".pbix"]');
		await expect(pbixInput).toBeVisible();
		await pbixInput.setInputFiles(resolve(process.cwd(), '..', 'artifacts', 'test.pbix'));

		let updatePayload: Record<string, unknown> | null = null;
		await page.route('**/rest/v1/projects**', async (route) => {
			if (route.request().method() !== 'PATCH') {
				await route.continue();
				return;
			}
			updatePayload = route.request().postDataJSON() as Record<string, unknown>;
			await route.fulfill({ status: 204, body: '' });
		});
		await page.route(`**/api/projects/${pbixSafeProjectId}/powerbi-publish`, async (route) => {
			if (route.request().method() !== 'POST') {
				await route.continue();
				return;
			}
			await route.fulfill({
				status: 502,
				contentType: 'application/json',
				body: JSON.stringify({ error: 'PBIX 게시 실패 mock' })
			});
		});

		await page.getByRole('button', { name: '수정 완료', exact: true }).click();
		await expect(page.locator('.auth-message.error')).toContainText('PBIX 게시 실패 mock');
		await expect(page.locator('form.project-form')).toBeVisible();
		const capturedPayload = updatePayload;
		expect(capturedPayload).not.toBeNull();
		expect((capturedPayload as Record<string, unknown> | null)?.power_bi_url).toBe(existingEmbedUrl);
		expect((capturedPayload as Record<string, unknown> | null)?.embed_status).toBe('supported');
		await page.screenshot({ path: testInfo.outputPath('pbix-failure-preserves-embed.png'), fullPage: true });
	});

	test(`PBIX replacement success keeps the edit flow atomic without mutation @auth`, async ({ page }, testInfo) => {
		await signIn(page, '/my');
		await expect(page.locator('.portfolio-section')).toBeVisible({ timeout: 15_000 });
		await waitForAuthenticatedContent(page, 'my');

		const editHrefs = await page
			.locator('.portfolio-card')
			.filter({ has: page.locator('[aria-label="공개 상태 공개"]') })
			.filter({ hasNotText: /처리 중|게시 실패/ })
			.locator('a[href*="/edit"]')
			.evaluateAll((links) =>
			links.map((link) => link.getAttribute('href')).filter((href): href is string => Boolean(href))
			);
		let editHref = '';
		let existingEmbedUrl = '';
		for (const href of editHrefs) {
			await page.goto(href, { waitUntil: 'networkidle' });
			await expect(page.locator('form.project-form')).toBeVisible({ timeout: 15_000 });
			const powerBiRadio = page.locator('.platform-panel input[type="radio"][value="powerbi"]');
			const embedInput = page.locator('input[placeholder="https://... 또는 iframe 코드"]');
			const hasExistingPbix = (await page.locator('.platform-panel .delete-option-row input[type="checkbox"]').count()) > 0;
			if (await powerBiRadio.isChecked() && hasExistingPbix && (await embedInput.inputValue()).trim()) {
				editHref = href;
				existingEmbedUrl = await embedInput.inputValue();
				break;
			}
		}
		if (!editHref) {
			test.skip(true, '공개 상태이면서 기존 Power BI 게시본이 연결된 수정 fixture가 없습니다.');
			return;
		}

		const projectId = editHref.split('/').at(-2) ?? '';
		const pbixPath = resolve(process.cwd(), '..', 'artifacts', 'test.pbix');
		await page.locator('.platform-panel .delete-option-row input[type="checkbox"]').check();
		const pbixInput = page.locator('input[type="file"][accept=".pbix"]');
		await expect(pbixInput).toBeVisible();
		await pbixInput.setInputFiles(pbixPath);

		let updatePayload: Record<string, unknown> | null = null;
		let publishRequestBytes = 0;
		let publishRequestHasFilename = false;
		await page.route('**/rest/v1/projects**', async (route) => {
			if (route.request().method() !== 'PATCH') {
				await route.continue();
				return;
			}
			updatePayload = route.request().postDataJSON() as Record<string, unknown>;
			await route.fulfill({ status: 204, body: '' });
		});
		await page.route(`**/api/projects/${projectId}/powerbi-publish`, async (route) => {
			if (route.request().method() !== 'POST') {
				await route.continue();
				return;
			}
			const body = route.request().postDataBuffer();
			publishRequestBytes = body?.byteLength ?? 0;
			publishRequestHasFilename = route.request().postData()?.includes('filename="test.pbix"') ?? false;
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify({ ok: true, message: 'PBIX 교체 게시 완료 mock' })
			});
		});

		await page.getByRole('button', { name: '수정 완료', exact: true }).click();
		await expect(page).toHaveURL(new RegExp(`/projects/${escapeRegExp(projectId)}$`), { timeout: 15_000 });
		expect(updatePayload).not.toBeNull();
		expect((updatePayload as Record<string, unknown> | null)?.power_bi_url).toBe(existingEmbedUrl);
		expect((updatePayload as Record<string, unknown> | null)?.embed_status).toBe('supported');
		expect(publishRequestBytes).toBeGreaterThan(0);
		expect(publishRequestHasFilename).toBe(true);
		if (await page.getByRole('heading', { name: '404', exact: true }).count()) {
			test.skip(true, 'PBIX 교체 요청 계약은 검증했지만 인증 계정에 공개 상세 fixture가 없어 상세 렌더링은 확인하지 못했습니다.');
			return;
		}
		await expect(page.locator('.detail-hero')).toBeVisible({ timeout: 15_000 });
		await page.screenshot({ path: testInfo.outputPath('pbix-replacement-success-contract.png'), fullPage: true });
	});

	test(`live PBIX replacement completes Import and updates the report fixture @mutation-pbix-live`, async ({ page }, testInfo) => {
		test.skip(!pbixLiveProjectId, 'PLAYWRIGHT_PBIX_LIVE_PROJECT_ID가 지정된 경우에만 실제 PBIX 교체를 실행합니다.');
		const editHref = `/projects/${pbixLiveProjectId}/edit`;
		await signIn(page, editHref);
		await expect(page.locator('form.project-form')).toBeVisible({ timeout: 15_000 });

		const powerBiRadio = page.locator('.platform-panel input[type="radio"][value="powerbi"]');
		await expect(powerBiRadio).toBeChecked();
		const existingEmbedUrl = await page.locator('input[placeholder="https://... 또는 iframe 코드"]').inputValue();
		const deletePbix = page.locator('.platform-panel .delete-option-row input[type="checkbox"]');
		await expect(deletePbix).toBeVisible();
		await deletePbix.check();

		const pbixInput = page.locator('input[type="file"][accept=".pbix"]');
		await expect(pbixInput).toBeVisible();
		await pbixInput.setInputFiles(resolve(process.cwd(), '..', 'artifacts', 'test.pbix'));

		await page.getByRole('button', { name: '수정 완료', exact: true }).click();
		await expect(page).toHaveURL(new RegExp(`/projects/${escapeRegExp(pbixLiveProjectId!)}$`), { timeout: 120_000 });
		await expect(page.locator('.detail-hero')).toBeVisible({ timeout: 20_000 });
		await expect(page.locator('.powerbi-shell')).toHaveAttribute('data-powerbi-status', 'ready', { timeout: 30_000 });

		const detailMetrics = await page.evaluate(() => {
			const report = document.querySelector<HTMLElement>('.powerbi-report');
			const frame = document.querySelector<HTMLIFrameElement>('.powerbi-report iframe');
			return {
				powerBIStatus: document.querySelector<HTMLElement>('.powerbi-shell')?.dataset.powerbiStatus ?? null,
				reportHeight: report?.getBoundingClientRect().height ?? 0,
				iframeHeight: frame?.getBoundingClientRect().height ?? 0,
				scrollWidth: document.documentElement.scrollWidth,
				clientWidth: document.documentElement.clientWidth
			};
		});
		expect(detailMetrics.powerBIStatus).toBe('ready');
		expect(detailMetrics.iframeHeight).toBeGreaterThan(0);
		expect(detailMetrics.scrollWidth - detailMetrics.clientWidth).toBeLessThanOrEqual(3);

		await page.screenshot({ path: testInfo.outputPath('pbix-replacement-live-success.png'), fullPage: true });
	});

	test(`detail renders a valid project fixture @auth`, async ({ page }, testInfo) => {
		let targetProjectId = detailProjectId;
		if (targetProjectId) {
			await signIn(page, `/projects/${targetProjectId}`);
		} else {
			await signIn(page, '/my');
			await waitForAuthenticatedContent(page, 'my');
			const projectCandidates = await page.locator('.portfolio-card').evaluateAll((cards) => {
				return cards
					.map((card) => {
						const href = card.querySelector('a[href^="/projects/"]')?.getAttribute('href') ?? '';
						const commentLabel = card.querySelector<HTMLElement>('.portfolio-card-meta [aria-label^="댓글 "]')?.getAttribute('aria-label');
						const commentMatch = commentLabel?.match(/댓글\s*(\d+)/);
						return { href, commentCount: Number(commentMatch?.[1] ?? 0) };
					})
					.filter((candidate) => candidate.href)
					.sort((left, right) => right.commentCount - left.commentCount);
			});
			if (projectCandidates.length === 0) {
				test.skip(true, '인증 계정에 상세 검증에 사용할 프로젝트가 없습니다.');
				return;
			}
			const selectionResults: Array<{ commentCount: number; commentCards: number }> = [];
			let fallbackProjectId = '';
			for (const candidate of projectCandidates) {
				const match = candidate.href.match(/^\/projects\/([^/?#]+)/);
				if (!match) {
					continue;
				}
				await page.goto(`/projects/${match[1]}`, { waitUntil: 'networkidle' });
				if (await page.getByRole('heading', { name: '404', exact: true }).count()) {
					selectionResults.push({ commentCount: candidate.commentCount, commentCards: 0 });
					continue;
				}
				await expect(page.locator('#project-comments')).toBeVisible({ timeout: 15_000 });
				await expect(page.locator('#project-comments')).not.toContainText('댓글을 불러오는 중입니다.', {
					timeout: 15_000
				});
				const commentCards = await page.locator('.comment-card').count();
				selectionResults.push({ commentCount: candidate.commentCount, commentCards });
				fallbackProjectId ||= match[1];
				if (commentCards) {
					targetProjectId = match[1];
					break;
				}
			}
			const selectionPath = testInfo.outputPath('detail-fixture-selection.json');
			await writeFile(selectionPath, JSON.stringify(selectionResults, null, 2), 'utf8');
			await testInfo.attach('detail-fixture-selection.json', {
				path: selectionPath,
				contentType: 'application/json'
			});
			if (!targetProjectId) {
				targetProjectId = fallbackProjectId;
			}
			if (!targetProjectId) {
				test.skip(true, '인증 계정에 접근 가능한 상세 프로젝트가 없습니다.');
				return;
			}
		}
		await page.waitForTimeout(750);
		await expect(page).toHaveURL(new RegExp(`/projects/${escapeRegExp(targetProjectId)}$`));
		await expect(page.locator('.detail-hero')).toBeVisible({ timeout: 15_000 });
		await expect(page.locator('#project-comments')).toBeVisible({ timeout: 15_000 });
		const powerBIShell = page.locator('.powerbi-shell').first();
		if (await powerBIShell.count()) {
			await expect(powerBIShell).toHaveAttribute('data-powerbi-status', 'ready', { timeout: 20_000 });
		}
		const embeddedDashboardFrame = page.frames().find((frame) => frame.url().startsWith('https://snowball-impact.github.io/smartHRD/'));
		const dashboardBodyText = embeddedDashboardFrame
			? await embeddedDashboardFrame.locator('body').innerText({ timeout: 8_000 }).catch(() => '')
			: '';
		const detailMetrics = {
			...(await page.evaluate(() => {
			const firstComment = document.querySelector('.comment-card');
			const siteHeader = document.querySelector<HTMLElement>('.site-header');
			const detailHero = document.querySelector<HTMLElement>('.detail-hero');
			const date = firstComment?.querySelector('.comment-date')?.getBoundingClientRect();
			const actions = firstComment?.querySelector('.comment-actions')?.getBoundingClientRect();
			const powerBIShell = document.querySelector<HTMLElement>('.powerbi-shell');
			const powerBIReport = document.querySelector<HTMLElement>('.powerbi-report');
			const powerBIFrame = document.querySelector<HTMLIFrameElement>('.powerbi-report iframe');
			const dashboardFrame = document.querySelector<HTMLIFrameElement>('.dashboard-frame');
			const describeFrame = (frame: HTMLIFrameElement | null) =>
				frame
					? (() => {
						const rect = frame.getBoundingClientRect();
						const style = getComputedStyle(frame);
					return {
						src: frame.getAttribute('src') || '',
						width: rect.width,
						height: rect.height,
						display: style.display,
						visibility: style.visibility,
						opacity: style.opacity
					};
					})()
					: null;
			const dateCenter = date ? date.y + date.height / 2 : null;
			const actionsCenter = actions ? actions.y + actions.height / 2 : null;
			return {
			title: document.title,
			viewportScrollY: window.scrollY,
			siteHeader: siteHeader ? (() => {
				const rect = siteHeader.getBoundingClientRect();
				return { top: rect.top, bottom: rect.bottom, position: getComputedStyle(siteHeader).position };
			})() : null,
			detailHero: detailHero ? (() => {
				const rect = detailHero.getBoundingClientRect();
				return { top: rect.top, bottom: rect.bottom };
			})() : null,
				h1: [...document.querySelectorAll('h1')].map((node) => node.textContent?.trim()).filter(Boolean),
				detailCard: Boolean(document.querySelector('.detail-card-preview .project-card')),
				detailCardIconMetrics: document.querySelectorAll('.detail-card-preview .card-meta-bottom [aria-label]').length,
				detailCardActivityBadge: document.querySelector('.detail-card-preview .card-activity-badge')?.textContent?.trim() ?? null,
				detailCardFooterMeta: document.querySelector('.detail-card-preview .card-footer-meta')?.textContent?.trim() ?? null,
				detailCardSummaryColor: (() => {
					const summary = document.querySelector<HTMLElement>('.detail-card-preview .card-summary');
					return summary ? getComputedStyle(summary).color : null;
				})(),
				visualPanel: Boolean(document.querySelector('#project-output')),
			iframes: document.querySelectorAll('iframe').length,
			powerBIStatus: powerBIShell?.dataset.powerbiStatus ?? null,
			powerBIShellHeight: powerBIShell?.getBoundingClientRect().height ?? 0,
			powerBIReportHeight: powerBIReport?.getBoundingClientRect().height ?? 0,
			powerBIFrame: describeFrame(powerBIFrame),
			dashboardFrame: describeFrame(dashboardFrame),
			fallback: Boolean(document.querySelector('.embed-empty')),
			report: Boolean(document.querySelector('#project-report')),
			comments: Boolean(document.querySelector('#project-comments')),
			commentCards: document.querySelectorAll('.comment-card').length,
			commentDateVisible: Boolean(date),
			commentActionsVisible: Boolean(actions),
			commentDateActionSameRow: dateCenter !== null && actionsCenter !== null && Math.abs(dateCenter - actionsCenter) <= 8,
			scrollWidth: document.documentElement.scrollWidth,
			clientWidth: document.documentElement.clientWidth
			};
			})),
			dashboardFrameUrl: embeddedDashboardFrame?.url() ?? null,
			dashboardBodyTextLength: dashboardBodyText.length,
			 dashboardBodyTextStart: dashboardBodyText.slice(0, 160)
		};
		if (testInfo.project.name === 'mobile') {
			await expect(page.locator('.detail-hero.project-detail-image-hero .detail-card-preview')).toHaveCSS('display', 'none');
		}
		if (testInfo.project.name === 'desktop') {
			await expect(detailMetrics.detailCardIconMetrics).toBe(3);
			if (detailProjectId) {
				await expect(detailMetrics.detailCardActivityBadge).toBe('NEW');
				await expect(detailMetrics.detailCardFooterMeta).toContain('2026-08-27');
				await expect(detailMetrics.detailCardFooterMeta).toContain('맹광국');
			} else {
				await expect(detailMetrics.detailCardActivityBadge === null || detailMetrics.detailCardActivityBadge === 'NEW' || detailMetrics.detailCardActivityBadge === '댓글 NEW').toBe(true);
				await expect(detailMetrics.detailCardFooterMeta).toMatch(/^\d{4}-\d{2}-\d{2}/);
			}
			await expect(detailMetrics.detailCardSummaryColor).toBe('rgba(255, 255, 255, 0.78)');
		}
		const actionOrder = await page.locator('.detail-action-group > *').evaluateAll((nodes) =>
			nodes.map((node) => node.textContent?.replace(/\s+/g, ' ').trim() ?? '')
		);
		const shareIndex = actionOrder.findIndex((label) => label.includes('링크 복사'));
		const likeIndex = actionOrder.findIndex((label) => label.includes('좋아요'));
		await expect(shareIndex).toBeGreaterThanOrEqual(0);
		await expect(likeIndex).toBeGreaterThan(shareIndex);
		if (actionOrder.some((label) => label === '수정')) {
			await expect(actionOrder.indexOf('수정')).toBeGreaterThan(likeIndex);
			await expect(actionOrder.indexOf('삭제')).toBeGreaterThan(actionOrder.indexOf('수정'));
		}
		await page.evaluate(() => {
			Object.defineProperty(navigator, 'clipboard', { configurable: true, value: undefined });
			Object.defineProperty(document, 'execCommand', {
				configurable: true,
				value: (command: string) => {
					if (command !== 'copy') {
						return false;
					}
					const source = document.querySelector<HTMLTextAreaElement>('textarea[readonly]');
					document.documentElement.dataset.folioCopiedShare = source?.value ?? '';
					return true;
				}
			});
		});
		await page.getByRole('button', { name: '공유 링크 복사' }).click();
		await expect(page.getByRole('button', { name: '공유 링크 복사' })).toContainText('복사 완료');
		const fallbackShareUrl = await page.evaluate(() => document.documentElement.dataset.folioCopiedShare ?? '');
		const fallbackShareParams = new URL(fallbackShareUrl).searchParams;
		await expect(fallbackShareParams.get('page')).toBe('Home');
		await expect(fallbackShareParams.get('project_id')).toBe(targetProjectId);
		await expect(fallbackShareParams.get('utm_campaign')).toBe('project_share');
		await expect(detailMetrics.viewportScrollY).toBe(0);
		// The original Streamlit shell keeps a 16px top inset at scrollY=0
		// on both viewports; sticky positioning only removes it after scrolling.
		const expectedHeaderTop = 16;
		await expect(detailMetrics.siteHeader?.top ?? 999).toBeGreaterThanOrEqual(expectedHeaderTop - 1);
		await expect(detailMetrics.siteHeader?.top ?? 999).toBeLessThanOrEqual(expectedHeaderTop + 1);
		await expect(detailMetrics.detailHero?.top ?? -1).toBeGreaterThan(detailMetrics.siteHeader?.bottom ?? 0);
		if (detailMetrics.commentCards > 0) {
			await expect(detailMetrics.commentDateVisible).toBe(true);
			await expect(detailMetrics.commentActionsVisible).toBe(true);
			await expect(detailMetrics.commentDateActionSameRow).toBe(true);

			const replyComment = page
				.locator('.comment-card:not(.reply)')
				.filter({ has: page.getByRole('button', { name: '답글', exact: true }) })
				.first();
			await expect(replyComment).toBeVisible();
			await replyComment.getByRole('button', { name: '답글', exact: true }).click();
			const replyForm = page.locator('form.reply-form');
			await expect(replyForm).toBeVisible();
			await replyForm.getByRole('button', { name: '취소', exact: true }).click();
			await expect(replyForm).toHaveCount(0);

			const deletableComment = replyComment;
			const deleteButton = deletableComment.locator('.comment-actions button').filter({ hasText: /^삭제$/ });
			await expect(deletableComment).toBeVisible();
			await expect(deleteButton).toBeVisible();
			await deleteButton.click();
			await expect(deletableComment.getByRole('button', { name: '삭제 확인', exact: true })).toBeVisible();
			await deletableComment.getByRole('button', { name: '취소', exact: true }).click();
			await expect(deletableComment.getByRole('button', { name: '삭제', exact: true })).toBeVisible();
		}
		if (detailMetrics.powerBIStatus === 'ready') {
			await expect(detailMetrics.powerBIShellHeight).toBeGreaterThanOrEqual(620);
			await expect(detailMetrics.powerBIReportHeight).toBeGreaterThanOrEqual(620);
		}
		const detailMetricsPath = testInfo.outputPath('detail-authenticated-metrics.json');
		await writeFile(detailMetricsPath, JSON.stringify(detailMetrics, null, 2), 'utf8');
		await testInfo.attach('detail-authenticated-metrics.json', {
			path: detailMetricsPath,
			contentType: 'application/json'
		});
		if (await page.locator('.dashboard-frame').count()) {
			await page.locator('.dashboard-frame').screenshot({ path: testInfo.outputPath('dashboard-frame.png') });
		}
		await page.evaluate(() => window.scrollTo({ top: 0, behavior: 'instant' }));
		await expect.poll(() => page.evaluate(() => window.scrollY)).toBe(0);
		await page.screenshot({ path: testInfo.outputPath('detail-viewport.png') });
		await page.screenshot({ path: testInfo.outputPath('detail-authenticated.png'), fullPage: true });
	});

	test(`detail falls back when the Power BI frame errors @auth`, async ({ page }, testInfo) => {
		if (!detailProjectId) {
			test.skip(true, 'Power BI fallback 검증에 사용할 프로젝트 ID가 없습니다.');
			return;
		}

		await page.route('https://app.powerbi.com/**', (route) => route.abort());
		await signIn(page, `/projects/${detailProjectId}`);
		await expect(page.locator('.detail-hero')).toBeVisible({ timeout: 15_000 });
		await expect(page.locator('.dashboard-frame')).toBeVisible({ timeout: 20_000 });
		await expect(page.locator('.powerbi-shell')).toHaveCount(0);

		const metrics = await page.evaluate(() => ({
			fallbackFrame: Boolean(document.querySelector('.dashboard-frame')),
			powerBIShell: Boolean(document.querySelector('.powerbi-shell')),
			fallbackCaption: document.querySelector('.visual-caption')?.textContent?.trim() ?? '',
			scrollWidth: document.documentElement.scrollWidth,
			clientWidth: document.documentElement.clientWidth
		}));
		await expect(metrics.fallbackFrame).toBe(true);
		await expect(metrics.powerBIShell).toBe(false);
		await expect(Math.abs(metrics.scrollWidth - metrics.clientWidth)).toBeLessThanOrEqual(3);

		const metricsPath = testInfo.outputPath('powerbi-error-fallback-metrics.json');
		await writeFile(metricsPath, JSON.stringify(metrics, null, 2), 'utf8');
		await testInfo.attach('powerbi-error-fallback-metrics.json', {
			path: metricsPath,
			contentType: 'application/json'
		});
		await page.screenshot({ path: testInfo.outputPath('powerbi-error-fallback.png'), fullPage: true });
	});

	test(`detail keeps populated comment metadata and actions compact @auth`, async ({ page }, testInfo) => {
		if (!detailProjectId) {
			test.skip(true, '댓글 밀도 검증에 사용할 프로젝트 ID가 없습니다.');
			return;
		}

		const rootId = '33333333-3333-4333-8333-333333333333';
		const replyId = '44444444-4444-4444-8444-444444444444';
		const rootAuthorId = '55555555-5555-4555-8555-555555555555';
		const replyAuthorId = '66666666-6666-4666-8666-666666666666';
		let currentUserId = '';
		const buildComments = () => [
			{
				id: rootId,
				project_id: detailProjectId,
				author_id: currentUserId || rootAuthorId,
				parent_id: null,
				body: '원본과 같은 한 줄 댓글의 정보 계층을 확인합니다.',
				depth: 0,
				is_deleted: false,
				created_at: '2026-08-28T10:00:00.000Z'
			},
			{
				id: replyId,
				project_id: detailProjectId,
				author_id: replyAuthorId,
				parent_id: rootId,
				body: '답글도 같은 날짜와 액션 밀도를 유지합니다.',
				depth: 1,
				is_deleted: false,
				created_at: '2026-08-28T10:05:00.000Z'
			}
		];

		await page.route('**/auth/v1/token*', async (route) => {
			const response = await route.fetch();
			const payload = (await response.json()) as { user?: { id?: string } };
			currentUserId = payload.user?.id || '';
			await route.fulfill({ response, body: JSON.stringify(payload) });
		});

		await page.route('**/rest/v1/comments*', (route) => {
			if (route.request().method() === 'GET') {
				return route.fulfill({
					status: 200,
					headers: { 'content-type': 'application/json' },
					body: JSON.stringify(buildComments())
				});
			}
			return route.continue();
		});
		await page.route('**/rest/v1/public_profiles*', (route) =>
			route.fulfill({
				status: 200,
				headers: { 'content-type': 'application/json' },
				body: JSON.stringify([
					{ id: currentUserId || rootAuthorId, name: '댓글 작성자' },
					{ id: replyAuthorId, name: '답글 작성자' }
				])
			})
		);

		await signIn(page, `/projects/${detailProjectId}`);
		await expect(page.locator('#project-comments')).not.toContainText('댓글을 불러오는 중입니다.', {
			timeout: 15_000
		});
		await expect(page.locator('.comment-card')).toHaveCount(2);
		const rootComment = page.locator('.comment-card').first();
		await expect(rootComment.getByRole('button', { name: '답글', exact: true })).toBeVisible();

		const metrics = await page.evaluate(() => {
			const cards = [...document.querySelectorAll<HTMLElement>('.comment-card')];
			return cards.map((card) => {
				const date = card.querySelector<HTMLElement>('.comment-date')?.getBoundingClientRect();
				const actions = card.querySelector<HTMLElement>('.comment-actions')?.getBoundingClientRect();
				return {
					text: card.querySelector('p')?.textContent?.trim() ?? '',
					dateVisible: Boolean(date),
					actionsVisible: Boolean(actions),
					sameRow: date && actions ? Math.abs(date.y + date.height / 2 - (actions.y + actions.height / 2)) <= 8 : false
				};
			});
		});
		await expect(metrics[0]?.dateVisible).toBe(true);
		await expect(metrics[0]?.actionsVisible).toBe(true);
		await expect(metrics[0]?.sameRow).toBe(true);
		await expect(metrics[1]?.dateVisible).toBe(true);
		await expect(currentUserId).not.toBe('');
		const deleteButton = rootComment.getByRole('button', { name: '삭제', exact: true });
		await expect(deleteButton).toBeVisible();
		await deleteButton.click();
		await expect(rootComment.getByRole('button', { name: '삭제 확인', exact: true })).toBeVisible();
		await page.screenshot({ path: testInfo.outputPath('detail-comment-delete-confirm.png'), fullPage: true });
		await rootComment.getByRole('button', { name: '취소', exact: true }).click();
		await expect(deleteButton).toBeVisible();
		await page.evaluate(() => window.scrollTo({ top: 0, behavior: 'instant' }));
		await expect.poll(() => page.evaluate(() => window.scrollY)).toBe(0);

		const metricsPath = testInfo.outputPath('detail-comment-density-metrics.json');
		await writeFile(metricsPath, JSON.stringify(metrics, null, 2), 'utf8');
		await testInfo.attach('detail-comment-density-metrics.json', {
			path: metricsPath,
			contentType: 'application/json'
		});
		await page.screenshot({ path: testInfo.outputPath('detail-comment-density.png'), fullPage: true });
	});

	test(`detail creates a comment and refreshes the list without mutation @auth`, async ({ page }) => {
		if (!detailProjectId) {
			test.skip(true, '댓글 등록 검증에 사용할 프로젝트 ID가 없습니다.');
			return;
		}

		const commentId = '11111111-1111-4111-8111-111111111111';
		const authorId = '22222222-2222-4222-8222-222222222222';
		let inserted = false;
		let insertPayload: Record<string, unknown> | null = null;
		const comment = {
			id: commentId,
			project_id: detailProjectId,
			author_id: authorId,
			parent_id: null,
			body: 'mock 댓글 등록 확인',
			depth: 0,
			is_deleted: false,
			created_at: '2026-08-28T10:00:00.000Z'
		};

		await page.route('**/rest/v1/comments*', async (route) => {
			const request = route.request();
			if (request.method() === 'GET') {
				await route.fulfill({
					status: 200,
					headers: { 'content-type': 'application/json' },
					body: JSON.stringify(inserted ? [comment] : [])
				});
				return;
			}
			if (request.method() === 'POST') {
				insertPayload = JSON.parse(request.postData() || '{}') as Record<string, unknown>;
				inserted = true;
				await route.fulfill({
					status: 201,
					headers: { 'content-type': 'application/json' },
					body: JSON.stringify(comment)
				});
				return;
			}
			await route.continue();
		});
		await page.route('**/rest/v1/public_profiles*', (route) =>
			route.fulfill({
				status: 200,
				headers: { 'content-type': 'application/json' },
				body: JSON.stringify([{ id: authorId, name: '테스트 작성자' }])
			})
		);
		await page.route('**/api/comments/*/email-notification', (route) =>
			route.fulfill({ status: 202, headers: { 'content-type': 'application/json' }, body: '{}' })
		);

		await signIn(page, `/projects/${detailProjectId}`);
		await expect(page.locator('#project-comments')).toBeVisible({ timeout: 15_000 });
		await expect(page.locator('#project-comments')).not.toContainText('댓글을 불러오는 중입니다.', {
			timeout: 15_000
		});
		const commentForm = page.locator('form.comment-form').first();
		await commentForm.locator('textarea').fill('  mock 댓글 등록 확인  ');
		await commentForm.getByRole('button', { name: '댓글 남기기', exact: true }).click();
		await expect(page.locator('#project-comments')).toContainText('댓글이 등록되었습니다.', { timeout: 8_000 });
		await expect(page.locator('.comment-card')).toContainText('mock 댓글 등록 확인');
		await expect(page.locator('#project-comments h2')).toHaveText('댓글 1개');
		await expect(insertPayload).toMatchObject({
			project_id: detailProjectId,
			body: 'mock 댓글 등록 확인',
			parent_id: null,
			depth: 0
		});
	});
});

async function waitForAuthenticatedContent(page: Page, routeName: string) {
	if (routeName === 'my') {
		await expect(page.locator('.portfolio-section')).not.toContainText('내 프로젝트를 불러오는 중입니다.', {
			timeout: 15_000
		});
		return;
	}
	if (routeName === 'notifications') {
		await expect(page.locator('.notifications-panel')).not.toContainText('알림을 불러오는 중입니다.', {
			timeout: 15_000
		});
	}
}

async function clearSubmitDrafts(page: Page) {
	await page.evaluate(() => {
		for (const key of Object.keys(localStorage)) {
			if (key.startsWith('folio-submit-draft:')) {
				localStorage.removeItem(key);
			}
		}
	});
}

async function signIn(page: Page, next: string) {
	const authEvents: string[] = [];
	page.on('requestfailed', (request) => {
		if (request.url().includes('/auth/')) {
			authEvents.push(`requestfailed ${new URL(request.url()).pathname} ${request.failure()?.errorText || 'unknown'}`);
		}
	});
	page.on('response', (response) => {
		if (response.url().includes('/auth/')) {
			authEvents.push(`${response.status()} ${new URL(response.url()).pathname}`);
		}
	});
	await page.goto(`/login?next=${encodeURIComponent(next)}`, { waitUntil: 'networkidle' });
	await page.waitForTimeout(250);
	await page.locator('input[type="email"]').fill(email);
	await page.locator('input[type="password"]').fill(password);
	await page.getByRole('button', { name: '로그인' }).click();
	try {
		await page.waitForURL((url) => url.pathname === next, { timeout: 15_000 });
	} catch {
		// Keep the login-page message below as the actionable failure instead of masking it with a timeout.
	}
	if (page.url().includes('/login') && authEvents.some((event) => event.includes(' 200 /auth/v1/token'))) {
		// Supabase may finish persisting the session just after the login action resolves.
		// Re-enter the destination once before treating the remaining login page as a failure.
		await page.goto(next, { waitUntil: 'networkidle' });
		await page.waitForTimeout(250);
	}
	if (page.url().includes('/login')) {
		const message = await page.locator('.auth-message').allTextContents();
		await page.locator('input[type="password"]').fill('');
		throw new Error(
			`Authenticated setup did not complete: ${message.join(' ').trim() || 'login page remained'}; auth=${authEvents.join(', ') || 'no auth request captured'}`
		);
	}
}

function escapeRegExp(value: string) {
	return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}
