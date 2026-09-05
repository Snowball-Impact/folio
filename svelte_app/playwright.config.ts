import { defineConfig, devices } from '@playwright/test';

const baseURL = process.env.PLAYWRIGHT_BASE_URL || 'http://127.0.0.1:5174';

export default defineConfig({
	testDir: './tests/uiux',
	testMatch: '**/*.spec.ts',
	testIgnore: '**/*.setup.ts',
	fullyParallel: false,
	workers: 1,
	timeout: 30_000,
	expect: {
		timeout: 5_000
	},
	outputDir: '../artifacts/playwright/test-results',
	reporter: [
		['list'],
		['html', { outputFolder: '../artifacts/playwright/report', open: 'never' }]
	],
	use: {
		baseURL,
		locale: 'ko-KR',
		colorScheme: 'light',
		navigationTimeout: 20_000,
		actionTimeout: 8_000,
		screenshot: 'only-on-failure',
		trace: 'retain-on-failure',
		video: 'off'
	},
	projects: [
		{
			name: 'desktop',
			use: {
				...devices['Desktop Chrome'],
				viewport: { width: 1440, height: 1000 },
				deviceScaleFactor: 1,
				isMobile: false
			}
		},
		{
			name: 'mobile',
			use: {
				...devices['Pixel 5'],
				viewport: { width: 390, height: 844 },
				deviceScaleFactor: 1,
				isMobile: true
			}
		}
	]
});
