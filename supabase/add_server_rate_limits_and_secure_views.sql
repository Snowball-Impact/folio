-- Apply this migration before deploying the matching server routes.
-- It keeps existing view counts and moves public view counting behind the app server.

begin;

create table if not exists public.server_rate_limits (
    rate_key text primary key check (rate_key ~ '^[a-f0-9]{64}$'),
    window_started_at timestamptz not null,
    request_count integer not null check (request_count >= 0),
    updated_at timestamptz not null default now()
);

create index if not exists server_rate_limits_window_started_at_idx
on public.server_rate_limits(window_started_at);

alter table public.server_rate_limits enable row level security;
revoke all on table public.server_rate_limits from anon, authenticated;

create or replace function public.consume_server_rate_limit(
    p_rate_key text,
    p_max_requests integer,
    p_window_seconds integer
)
returns boolean
language plpgsql
security definer
set search_path = ''
as $$
declare
    allowed boolean;
    request_time timestamptz := pg_catalog.clock_timestamp();
begin
    if p_rate_key !~ '^[a-f0-9]{64}$'
        or p_max_requests < 1
        or p_max_requests > 10000
        or p_window_seconds < 1
        or p_window_seconds > 86400 then
        raise exception 'Invalid rate limit request';
    end if;

    delete from public.server_rate_limits
    where window_started_at < request_time - interval '2 days';

    insert into public.server_rate_limits (rate_key, window_started_at, request_count, updated_at)
    values (p_rate_key, request_time, 1, request_time)
    on conflict (rate_key) do update
    set
        window_started_at = case
            when public.server_rate_limits.window_started_at <= request_time - pg_catalog.make_interval(secs => p_window_seconds)
                then request_time
            else public.server_rate_limits.window_started_at
        end,
        request_count = case
            when public.server_rate_limits.window_started_at <= request_time - pg_catalog.make_interval(secs => p_window_seconds)
                then 1
            else public.server_rate_limits.request_count + 1
        end,
        updated_at = request_time
    returning request_count <= p_max_requests into allowed;

    return allowed;
end;
$$;

revoke all on function public.consume_server_rate_limit(text, integer, integer) from public;
grant execute on function public.consume_server_rate_limit(text, integer, integer) to service_role;

create or replace function public.increment_project_view_count(
    project_id_input uuid,
    anonymous_viewer_id_input uuid
)
returns boolean
language plpgsql
security definer
set search_path = ''
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
      and status = 'published'
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

    hashed_viewer := pg_catalog.encode(
        extensions.digest(pg_catalog.convert_to(viewer_source, 'UTF8'), 'sha256'),
        'hex'
    );
    current_view_date := (pg_catalog.timezone('Asia/Seoul', pg_catalog.now()))::date;

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
        updated_at = pg_catalog.now()
    where id = project_id_input;

    return true;
end;
$$;

revoke all on function public.increment_project_view_count(uuid, uuid) from public;
grant execute on function public.increment_project_view_count(uuid, uuid) to service_role;

drop function if exists public.record_server_project_view(uuid, uuid, uuid);

create or replace function public.record_server_project_view(
    p_project_id uuid,
    p_viewer_user_id uuid,
    p_anonymous_viewer_key text
)
returns boolean
language plpgsql
security definer
set search_path = ''
as $$
declare
    project_author_id uuid;
    viewer_source text;
    hashed_viewer text;
    current_view_date date;
    inserted_rows integer;
begin
    select author_id
    into project_author_id
    from public.projects
    where id = p_project_id
      and is_public = true
      and status = 'published'
    for update;

    if not found or p_viewer_user_id = project_author_id then
        return false;
    end if;

    if p_viewer_user_id is not null then
        viewer_source := 'user:' || p_viewer_user_id::text;
    elsif p_anonymous_viewer_key ~ '^[a-f0-9]{64}$' then
        viewer_source := 'anonymous:' || p_anonymous_viewer_key;
    else
        return false;
    end if;

    hashed_viewer := pg_catalog.encode(
        extensions.digest(pg_catalog.convert_to(viewer_source, 'UTF8'), 'sha256'),
        'hex'
    );
    current_view_date := (pg_catalog.timezone('Asia/Seoul', pg_catalog.now()))::date;

    insert into public.project_views (project_id, viewer_hash, viewed_on)
    values (p_project_id, hashed_viewer, current_view_date)
    on conflict do nothing;

    get diagnostics inserted_rows = row_count;
    if inserted_rows = 0 then
        return false;
    end if;

    update public.projects
    set view_count = view_count + 1,
        updated_at = pg_catalog.now()
    where id = p_project_id;

    return true;
end;
$$;

revoke all on function public.record_server_project_view(uuid, uuid, text) from public;
grant execute on function public.record_server_project_view(uuid, uuid, text) to service_role;

alter function public.home_project_snapshot(integer, integer, integer, text) set search_path = '';
alter function public.project_detail_snapshot(uuid) set search_path = '';
alter function public.handle_new_user() set search_path = '';
alter function public.validate_comment_thread() set search_path = '';

commit;
