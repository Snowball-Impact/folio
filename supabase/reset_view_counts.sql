-- DESTRUCTIVE: run only after the daily unique view migration passes integration verification.
-- This establishes a clean measurement baseline and cannot restore previous counters.

begin;

lock table public.projects in share row exclusive mode;
truncate table public.project_views;
update public.projects
set view_count = 0
where view_count <> 0;

commit;

-- Both values must be zero immediately after the reset.
select
    (select count(*) from public.project_views) as stored_view_events,
    (select coalesce(sum(view_count), 0) from public.projects) as total_view_count;

