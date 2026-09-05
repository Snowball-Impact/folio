import * as server from '../entries/pages/projects/_id_/_page.server.ts.js';

export const index = 11;
let component_cache;
export const component = async () => component_cache ??= (await import('../entries/pages/projects/_id_/_page.svelte.js')).default;
export { server };
export const server_id = "routes/projects/[id]/+page.server.ts";
export const imports = ["_app/immutable/nodes/11.Jot8C6N0.js","_app/immutable/chunks/CIfncF2G.js","_app/immutable/chunks/teY_FVKk.js","_app/immutable/chunks/HclGiUj8.js","_app/immutable/chunks/xihTtKlq.js","_app/immutable/chunks/B5LhR3dW.js","_app/immutable/chunks/B0qFIe--.js","_app/immutable/chunks/tBNA8RRr.js","_app/immutable/chunks/oE2QjaDQ.js","_app/immutable/chunks/Cf8PjfuQ.js","_app/immutable/chunks/CD19-hRb.js","_app/immutable/chunks/3SprZdwx.js"];
export const stylesheets = [];
export const fonts = [];
