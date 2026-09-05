import * as server from '../entries/pages/_page.server.ts.js';

export const index = 2;
let component_cache;
export const component = async () => component_cache ??= (await import('../entries/pages/_page.svelte.js')).default;
export { server };
export const server_id = "routes/+page.server.ts";
export const imports = ["_app/immutable/nodes/2.BcyMV6rc.js","_app/immutable/chunks/CIfncF2G.js","_app/immutable/chunks/xihTtKlq.js","_app/immutable/chunks/Cf8PjfuQ.js","_app/immutable/chunks/oE2QjaDQ.js"];
export const stylesheets = [];
export const fonts = [];
