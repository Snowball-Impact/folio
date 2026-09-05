import * as server from '../entries/pages/references/_platform_/_page.server.ts.js';

export const index = 14;
let component_cache;
export const component = async () => component_cache ??= (await import('../entries/pages/references/_platform_/_page.svelte.js')).default;
export { server };
export const server_id = "routes/references/[platform]/+page.server.ts";
export const imports = ["_app/immutable/nodes/14.DxNkvg5U.js","_app/immutable/chunks/CIfncF2G.js","_app/immutable/chunks/xihTtKlq.js","_app/immutable/chunks/Cf8PjfuQ.js","_app/immutable/chunks/oE2QjaDQ.js"];
export const stylesheets = [];
export const fonts = [];
