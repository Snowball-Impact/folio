import { existsSync, readFileSync } from 'node:fs';
import { resolve } from 'node:path';

function readEnvFile(path: string) {
	if (!existsSync(path)) {
		return new Map<string, string>();
	}

	const values = new Map<string, string>();
	for (const line of readFileSync(path, 'utf8').split(/\r?\n/)) {
		const match = line.match(/^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)\s*$/);
		if (!match) {
			continue;
		}
		let value = match[2].trim();
		if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith("'") && value.endsWith("'"))) {
			value = value.slice(1, -1);
		}
		values.set(match[1], value);
	}
	return values;
}
const localValues = new Map([
	...readEnvFile(resolve(process.cwd(), '.env')),
	...readEnvFile(resolve(process.cwd(), '..', '.env'))
]);

export function testEnv(...names: string[]) {
	for (const name of names) {
		const processValue = process.env[name]?.trim();
		if (processValue) {
			return processValue;
		}
		const localValue = localValues.get(name)?.trim();
		if (localValue) {
			return localValue;
		}
	}
	return '';
}
