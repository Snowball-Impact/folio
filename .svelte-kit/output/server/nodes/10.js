import * as server from '../entries/pages/powerbi/_page.server.ts.js';

export const index = 10;
let component_cache;
export const component = async () => component_cache ??= (await import('../entries/pages/powerbi/_page.svelte.js')).default;
export { server };
export const server_id = "routes/powerbi/+page.server.ts";
export const imports = ["_app/immutable/nodes/10.BZ3UY_-1.js","_app/immutable/chunks/CIfncF2G.js","_app/immutable/chunks/xihTtKlq.js","_app/immutable/chunks/oE2QjaDQ.js"];
export const stylesheets = [];
export const fonts = [];
