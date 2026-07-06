-- Apply this migration before deploying the matching application code.
-- This script preserves every existing projects.view_count value.

begin;

create extension if not exists pgcrypto with schema extensions;

create table if not exists public.project_views (
    project_id uuid not null references public.projects(id) on delete cascade,
    viewer_hash text not null,
    viewed_on date not null,
    created_at timestamptz not null default now(),
    primary key (project_id, viewer_hash, viewed_on)
);

create index if not exists project_views_project_date_idx
on public.project_views(project_id, viewed_on);

alter table public.project_views enable row level security;
revoke all on table public.project_views from anon, authenticated;

drop function if exists public.increment_project_view_count(uuid);

create or replace function public.increment_project_view_count(
    project_id_input uuid,
    anonymous_viewer_id_input uuid
)
returns boolean
language plpgsql
security definer
set search_path = public
as $$
declare
    project_author_id uuid;
    project_is_public boolean;
    viewer_source text;
    hashed_viewer text;
    current_view_date date;
    inserted_rows integer;
begin
    select author_id, is_public
    into project_author_id, project_is_public
    from public.projects
    where id = project_id_input
    for update;

    if not found or not project_is_public then
        return false;
    end if;

    if auth.uid() is not null and auth.uid() = project_author_id then
        return false;
    end if;

    if auth.uid() is not null then
        viewer_source := 'user:' || auth.uid()::text;
    elsif anonymous_viewer_id_input is not null then
        viewer_source := 'anonymous:' || anonymous_viewer_id_input::text;
    else
        return false;
    end if;

    hashed_viewer := encode(
        extensions.digest(convert_to(viewer_source, 'UTF8'), 'sha256'),
        'hex'
    );
    current_view_date := (timezone('Asia/Seoul', now()))::date;

    insert into public.project_views (project_id, viewer_hash, viewed_on)
    values (project_id_input, hashed_viewer, current_view_date)
    on conflict do nothing;

    get diagnostics inserted_rows = row_count;
    if inserted_rows = 0 then
        return false;
    end if;

    update public.projects
    set
        view_count = view_count + 1,
        updated_at = now()
    where id = project_id_input;

    return true;
end;
$$;

revoke all on function public.increment_project_view_count(uuid, uuid) from public;
grant execute on function public.increment_project_view_count(uuid, uuid) to anon, authenticated;

commit;

-- Expected result: table exists and no view count has been reset.
select
    to_regclass('public.project_views') as project_views_table,
    count(*) as project_count,
    coalesce(sum(view_count), 0) as preserved_total_view_count
from public.projects;

