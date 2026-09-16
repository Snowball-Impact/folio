-- Hotfix for databases where add_server_rate_limits_and_secure_views.sql
-- was applied before the request_time variable rename.
-- Safe to run more than once; it only replaces the RPC implementation.

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
