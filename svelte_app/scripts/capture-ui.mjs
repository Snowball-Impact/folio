import { chromium } from '@playwright/test';
import fs from 'node:fs';
import path from 'node:path';

const DEFAULT_BASE_URL = process.env.PLAYWRIGHT_BASE_URL ?? 'http://127.0.0.1:5174';
const DEFAULT_OUT_DIR = '../artifacts/playwright/manual-captures';
const VIEWPORTS = {
	desktop: { width: 1440, height: 1000, isMobile: false },
	mobile: { width: 390, height: 844, isMobile: true }
};
const ROUTES = [
	['home', '/'],
	['references-powerbi', '/references/powerbi'],
	['powerbi-news', '/powerbi'],
	['powerbi-learning', '/powerbi?topic=learning'],
	['powerbi-community', '/powerbi?topic=community'],
	['powerbi-cert', '/powerbi?topic=cert'],
	['about', '/about'],
	['login', '/login'],
	['signup', '/signup'],
	['submit', '/submit'],
	['my-page', '/my'],
	['notifications', '/notifications']
];

function parseArgs(argv) {
	const options = {
		baseUrl: DEFAULT_BASE_URL,
		outDir: DEFAULT_OUT_DIR,
		viewportNames: Object.keys(VIEWPORTS),
		routes: ROUTES
	};

	for (let index = 0; index < argv.length; index += 1) {
		const arg = argv[index];
		const next = argv[index + 1];
		if (arg === '--base-url' && next) {
			options.baseUrl = next;
			index += 1;
		} else if (arg === '--out-dir' && next) {
			options.outDir = next;
			index += 1;
		} else if (arg === '--viewport' && next) {
			options.viewportNames = next.split(',').map((value) => value.trim()).filter(Boolean);
			index += 1;
		} else if (arg === '--route' && next) {
			const [name, ...pathParts] = next.split('=');
			const routePath = pathParts.join('=');
			if (!name || !routePath) {
				throw new Error('--route must be formatted as name=/path');
			}
			options.routes = [[name, routePath]];
			index += 1;
		}
	}

	for (const viewportName of options.viewportNames) {
		if (!VIEWPORTS[viewportName]) {
			throw new Error(`Unknown viewport: ${viewportName}`);
		}
	}

	return options;
}

function safeName(value) {
	return value.replace(/[^a-zA-Z0-9_.-]+/g, '-').replace(/^-|-$/g, '');
}

function resolveUrl(baseUrl, routePath) {
	return new URL(routePath, baseUrl.endsWith('/') ? baseUrl : `${baseUrl}/`).toString();
}

async function main() {
	const options = parseArgs(process.argv.slice(2));
	const outDir = path.resolve(options.outDir);
	fs.mkdirSync(outDir, { recursive: true });

	const browser = await chromium.launch();
	const manifest = ['# Playwright Manual UI Captures', ''];

	try {
		for (const viewportName of options.viewportNames) {
			const viewport = VIEWPORTS[viewportName];
			const page = await browser.newPage({
				viewport: { width: viewport.width, height: viewport.height },
				deviceScaleFactor: 1,
				isMobile: viewport.isMobile
			});

			for (const [routeName, routePath] of options.routes) {
				const url = resolveUrl(options.baseUrl, routePath);
				await page.goto(url, { waitUntil: 'networkidle' });
				const fileName = `${viewportName}-${safeName(routeName)}.png`;
				const target = path.join(outDir, fileName);
				await page.screenshot({ path: target, fullPage: true });
				manifest.push(`- ${viewportName} / ${routeName} / ${path.relative(process.cwd(), target)} / ${url}`);
			}

			await page.close();
		}
	} finally {
		await browser.close();
	}

	fs.writeFileSync(path.join(outDir, 'manifest.md'), `${manifest.join('\n')}\n`, 'utf8');
	console.log(path.join(outDir, 'manifest.md'));
}

main().catch((error) => {
	console.error(error);
	process.exit(1);
});
