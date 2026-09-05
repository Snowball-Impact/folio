import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig, loadEnv } from 'vite';

export default defineConfig(({ mode }) => {
	const rootEnv = loadEnv(mode, '..', '');
	for (const [key, value] of Object.entries(rootEnv)) {
		process.env[key] ??= value;
	}

	return {
		envDir: '..',
		envPrefix: ['VITE_', 'PUBLIC_'],
		plugins: [sveltekit()]
	};
});
