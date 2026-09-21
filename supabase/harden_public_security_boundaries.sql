-- Apply once in the Supabase SQL editor before deploying the matching app code.
-- It is forward-compatible with older snapshot-function bodies: the old body is
-- retained as an internal implementation and a bounded public wrapper is added.

begin;

do $$
begin
    if to_regprocedure('public.home_project_snapshot_internal(integer,integer,integer,text)') is null then
        alter function public.home_project_snapshot(integer, integer, integer, text)
            rename to home_project_snapshot_internal;
    end if;
end
$$;

create or replace function public.home_project_snapshot(
    p_limit integer default 6,
    p_tag_limit integer default 10,
    p_like_sample_limit integer default 120,
    p_platform_key text default null
)
returns jsonb
language sql
stable
security definer
set search_path = ''
as $$
    select public.home_project_snapshot_internal(
        least(greatest(coalesce(p_limit, 6), 0), 24),
        least(greatest(coalesce(p_tag_limit, 10), 0), 40),
        least(greatest(coalesce(p_like_sample_limit, 120), coalesce(p_limit, 6), 0), 240),
        p_platform_key
    );
$$;

revoke all on function public.home_project_snapshot_internal(integer, integer, integer, text) from public, anon, authenticated;
revoke all on function public.home_project_snapshot(integer, integer, integer, text) from public;
grant execute on function public.home_project_snapshot(integer, integer, integer, text) to anon, authenticated;

do $$
begin
    if to_regprocedure('public.project_detail_snapshot_internal(uuid)') is null then
        alter function public.project_detail_snapshot(uuid)
            rename to project_detail_snapshot_internal;
    end if;
end
$$;

create or replace function public.project_detail_snapshot(p_project_id uuid)
returns jsonb
language sql
stable
security definer
set search_path = ''
as $$
    select case when exists (
        select 1
        from public.projects p
        where p.id = p_project_id
          and p.is_public = true
          and p.status = 'published'
    ) then public.project_detail_snapshot_internal(p_project_id) else null::jsonb end;
$$;

revoke all on function public.project_detail_snapshot_internal(uuid) from public, anon, authenticated;
revoke all on function public.project_detail_snapshot(uuid) from public;
grant execute on function public.project_detail_snapshot(uuid) to anon, authenticated;

alter table public.projects
drop constraint if exists projects_power_bi_url_allowed_check;

alter table public.projects
add constraint projects_power_bi_url_allowed_check
check (
    power_bi_url is null
    or power_bi_url ~* '^https://(app\\.powerbi\\.com|app\\.fabric\\.microsoft\\.com|public\\.tableau\\.com|lookerstudio\\.google\\.com|datastudio\\.google\\.com|share\\.streamlit\\.io|[a-z0-9-]+\\.streamlit\\.app)(/|:|$)'
) not valid;

revoke delete on public.projects from authenticated;
drop policy if exists "Users can delete own projects" on public.projects;
drop policy if exists "Users can update own projects" on public.projects;
create policy "Users can update own projects"
on public.projects for update
using (auth.uid() = author_id)
with check (auth.uid() = author_id and status is distinct from 'deleted');

commit;
