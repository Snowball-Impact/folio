// See https://svelte.dev/docs/kit/types#app.d.ts
// for information about these interfaces
declare module '*?raw' {
	const content: string;
	export default content;
}

declare module 'cloudflare:sockets' {
	export type SocketAddress = {
		hostname: string;
		port: number;
	};

	export type SocketOptions = {
		secureTransport?: 'off' | 'on' | 'starttls';
		allowHalfOpen?: boolean;
	};

	export type Socket = {
		readable: ReadableStream<Uint8Array>;
		writable: WritableStream<Uint8Array>;
		opened: Promise<unknown>;
		closed: Promise<void>;
		close(): Promise<void>;
		startTls(): Socket;
	};

	export function connect(address: SocketAddress | string, options?: SocketOptions): Socket;
}

declare global {
	namespace App {
		// interface Error {}
		// interface Locals {}
		// interface PageData {}
		// interface PageState {}
		// interface Platform {}
	}
}

export {};
