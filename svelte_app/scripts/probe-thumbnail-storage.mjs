import { createClient } from '@supabase/supabase-js';
import { readFileSync } from 'node:fs';

const env = readEnv('../.env');
const supabaseUrl = env.PUBLIC_SUPABASE_URL || env.SUPABASE_URL;
const serviceRoleKey = env.SUPABASE_SERVICE_ROLE_KEY;
const bucketName = env.THUMBNAIL_STORAGE_BUCKET || 'project-thumbnails';

if (!supabaseUrl || !serviceRoleKey) {
	throw new Error('PUBLIC_SUPABASE_URL/SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY is missing.');
}

const client = createClient(supabaseUrl, serviceRoleKey, {
	auth: {
		autoRefreshToken: false,
		persistSession: false
	}
});
const bucket = client.storage.from(bucketName);
const bucketResult = await client.storage.getBucket(bucketName);
console.log('bucket', bucketResult.error ? bucketResult.error.message : 'ok', bucketResult.data ? { name: bucketResult.data.name, public: bucketResult.data.public } : null);

if (process.argv.includes('--fix')) {
	const update = await client.storage.updateBucket(bucketName, {
		public: true,
		fileSizeLimit: 5 * 1024 * 1024,
		allowedMimeTypes: ['image/jpeg', 'image/png', 'image/webp']
	});
	console.log('updateBucket', update.error ? update.error.message : 'ok');
}

const probes = [
	{
		extension: 'png',
		type: 'image/png',
		base64: 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/p9sAAAAASUVORK5CYII='
	},
	{
		extension: 'jpg',
		type: 'image/jpeg',
		base64: '/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAP//////////////////////////////////////////////////////////////////////////////////////2wBDAf//////////////////////////////////////////////////////////////////////////////////////wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAX/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIQAxAAAAH/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/9oACAEBAAEFAqf/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oACAEDAQE/ASP/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oACAECAQE/ASP/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/9oACAEBAAY/Aqf/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/9oACAEBAAE/IX//2gAMAwEAAgADAAAAEP/EFBQRAQAAAAAAAAAAAAAAAAAAARD/2gAIAQMBAT8QH//EFBQRAQAAAAAAAAAAAAAAAAAAARD/2gAIAQIBAT8QH//EFBABAQAAAAAAAAAAAAAAAAAAARD/2gAIAQEAAT8QH//Z'
	},
	{
		extension: 'webp',
		type: 'image/webp',
		base64: 'UklGRiIAAABXRUJQVlA4IBYAAAAwAQCdASoBAAEADsD+JaQAA3AA/vuUAAA='
	}
];

for (const probe of probes) {
	const bytes = Uint8Array.from(Buffer.from(probe.base64, 'base64'));
	const path = `diagnostics/codex-thumbnail-probe-${Date.now()}.${probe.extension}`;
	const upload = await bucket.upload(path, bytes, {
		contentType: probe.type,
		cacheControl: '60',
		upsert: true
	});
	console.log('upload', probe.type, upload.error ? upload.error.message : 'ok');

	if (!upload.error) {
		const publicUrl = bucket.getPublicUrl(path).data.publicUrl;
		console.log('publicUrl', probe.type, publicUrl ? 'ok' : 'missing');
		const remove = await bucket.remove([path]);
		console.log('remove', probe.type, remove.error ? remove.error.message : 'ok');
	}
}

function readEnv(path) {
	const values = {};
	for (const line of readFileSync(path, 'utf8').split(/\r?\n/)) {
		const trimmed = line.trim();
		if (!trimmed || trimmed.startsWith('#')) {
			continue;
		}
		const match = trimmed.match(/^([A-Za-z_][A-Za-z0-9_]*)=(.*)$/);
		if (!match) {
			continue;
		}
		values[match[1]] = unquote(match[2].trim());
	}
	return values;
}

function unquote(value) {
	if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith("'") && value.endsWith("'"))) {
		return value.slice(1, -1);
	}
	return value;
}
