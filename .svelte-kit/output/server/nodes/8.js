import * as server from '../entries/pages/policy/_page.server.ts.js';

export const index = 8;
let component_cache;
export const component = async () => component_cache ??= (await import('../entries/pages/policy/_page.svelte.js')).default;
export { server };
export const server_id = "routes/policy/+page.server.ts";
export const imports = ["_app/immutable/nodes/8.DLL37hnJ.js","_app/immutable/chunks/CIfncF2G.js","_app/immutable/chunks/xihTtKlq.js"];
export const stylesheets = [];
export const fonts = [];
