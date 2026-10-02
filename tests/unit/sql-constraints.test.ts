import assert from 'node:assert/strict';
import fs from 'node:fs';
import test from 'node:test';

const expectedTrustedEmbedExpression =
	"^https://(app[.]powerbi[.]com|app[.]fabric[.]microsoft[.]com|public[.]tableau[.]com|lookerstudio[.]google[.]com|datastudio[.]google[.]com|share[.]streamlit[.]io|[a-z0-9-]+[.]streamlit[.]app|[a-z0-9-]+[.]github[.]io)(:[0-9]+)?([/?#]|$)";

const trustedEmbedPattern = new RegExp(expectedTrustedEmbedExpression, 'i');

test('trusted embed host expression accepts the documented URL forms', () => {
	for (const url of [
		'https://app.powerbi.com/view?r=example',
		'https://app.fabric.microsoft.com/reportEmbed?reportId=example',
		'https://public.tableau.com/views/example',
		'https://lookerstudio.google.com/embed/reporting/example',
		'https://datastudio.google.com/embed/reporting/example',
		'https://share.streamlit.io/example',
		'https://demo.streamlit.app?embed=true',
		'https://example.github.io#dashboard',
		'https://app.powerbi.com:443/view?r=example'
	]) {
		assert.match(url, trustedEmbedPattern, url);
	}
});

test('trusted embed host expression rejects scheme, host, userinfo, and port bypasses', () => {
	for (const url of [
		'http://app.powerbi.com/view?r=example',
		'https://app.powerbi.com.evil.example/view',
		'https://evil-app.powerbi.com/view',
		'https://app.powerbi.com@evil.example/view',
		'https://app.powerbi.com:443@evil.example/view',
		'https://app.powerbi.com:abc/view'
	]) {
		assert.doesNotMatch(url, trustedEmbedPattern, url);
	}
});

for (const path of [
	'supabase/schema.sql',
	'supabase/harden_public_security_boundaries.sql',
	'supabase/fix_trusted_embed_url_constraint.sql'
]) {
	test(`${path} uses the PostgreSQL-safe trusted embed host expression`, () => {
		const sql = fs.readFileSync(path, 'utf8');
		assert.ok(sql.includes(expectedTrustedEmbedExpression));
		assert.ok(!sql.includes('app\\\\.powerbi\\\\.com'));
	});
}

test('GA4 backfill hashes use a DateStyle-independent ISO date', () => {
	const sql = fs.readFileSync(
		'supabase/backfill_project_views_from_ga4_20260922_20260927.sql',
		'utf8'
	);
	const fixedDateExpression = "to_char(source.viewed_on, 'YYYY-MM-DD')";

	assert.equal(sql.match(new RegExp(fixedDateExpression.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g'))?.length, 3);
	assert.ok(!sql.includes("'ga4-backfill-20260928:' || source.viewed_on"));
});

test('trusted embed constraint repair is atomic', () => {
	const sql = fs.readFileSync('supabase/fix_trusted_embed_url_constraint.sql', 'utf8').trim();
	const beginIndex = sql.toLowerCase().indexOf('begin;');
	const dropIndex = sql.toLowerCase().indexOf('drop constraint');
	const commitIndex = sql.toLowerCase().lastIndexOf('commit;');

	assert.ok(beginIndex >= 0 && beginIndex < dropIndex);
	assert.ok(dropIndex < commitIndex);
	assert.match(sql, /commit;$/i);
});
