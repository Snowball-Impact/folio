alter table public.projects
drop constraint if exists projects_thumbnail_mode_check;

alter table public.projects
add constraint projects_thumbnail_mode_check
check (thumbnail_mode in ('auto_cover', 'manual_url', 'capture', 'upload'));
