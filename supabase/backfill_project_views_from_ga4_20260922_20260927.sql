-- Aggregate reconstruction from GA4 Date x project path x Active users.
-- Window: 2026-09-22..27 KST. Sep 21 is excluded to avoid partial-day duplicates.
-- Synthetic hashes are deterministic, so this script is safe to rerun.

begin;

create temporary table ga4_project_view_backfill (
    viewed_on date not null,
    project_id uuid not null,
    active_users integer not null check (active_users > 0)
) on commit drop;

insert into ga4_project_view_backfill values
    ('2026-09-22', '4f013e01-2de4-46d5-a7db-073058a314e8', 38),
    ('2026-09-22', '5cb9d672-b4e7-4eb6-9009-1aae676e9570', 29),
    ('2026-09-22', '69a8c0c3-4221-467d-9096-0fe68d292311', 3),
    ('2026-09-22', '1b1d56ff-1937-4a59-a74f-909aef09f251', 18),
    ('2026-09-23', '4f013e01-2de4-46d5-a7db-073058a314e8', 2),
    ('2026-09-23', '5cb9d672-b4e7-4eb6-9009-1aae676e9570', 286),
    ('2026-09-23', '1b1d56ff-1937-4a59-a74f-909aef09f251', 14),
    ('2026-09-24', '5cb9d672-b4e7-4eb6-9009-1aae676e9570', 442),
    ('2026-09-25', '5cb9d672-b4e7-4eb6-9009-1aae676e9570', 299),
    ('2026-09-26', '5cb9d672-b4e7-4eb6-9009-1aae676e9570', 384),
    ('2026-09-26', 'b20f3c1d-cbb8-4be6-93bd-6a4768ab4486', 1),
    ('2026-09-26', 'a06219fe-9c5e-48f2-bd36-c289c4d158e5', 3),
    ('2026-09-26', 'e758068e-fb8d-4faa-8258-2b191b189ca5', 1),
    ('2026-09-26', '74bcaa21-64fd-4313-83ce-6a65eff1431a', 1),
    ('2026-09-26', '682d5011-7d76-4490-b883-0c481dfb0277', 1),
    ('2026-09-26', '718ee7fd-bb1c-4789-b4dc-8a8a70731528', 1),
    ('2026-09-26', '247dba95-5582-44be-8afe-e6bf42925d3a', 1),
    ('2026-09-27', '5cb9d672-b4e7-4eb6-9009-1aae676e9570', 316),
    ('2026-09-27', 'e758068e-fb8d-4faa-8258-2b191b189ca5', 1);

with synthetic_views as (
    select
        source.project_id,
        encode(extensions.digest(pg_catalog.convert_to(
            'ga4-backfill-20260928:' || to_char(source.viewed_on, 'YYYY-MM-DD') || ':' ||
            source.project_id || ':' || series.viewer_number, 'UTF8'
        ), 'sha256'), 'hex') as viewer_hash,
        source.viewed_on,
        (source.viewed_on::timestamp + time '12:00') at time zone 'Asia/Seoul' as created_at
    from ga4_project_view_backfill source
    cross join lateral generate_series(1, source.active_users) series(viewer_number)
)
insert into public.project_views (project_id, viewer_hash, viewed_on, created_at)
select project_id, viewer_hash, viewed_on, created_at from synthetic_views
on conflict (project_id, viewer_hash, viewed_on) do nothing;

update public.projects project
set view_count = ledger.total_views
from (
    select project_id, count(*)::integer as total_views
    from public.project_views
    where project_id in (select distinct project_id from ga4_project_view_backfill)
    group by project_id
) ledger
where project.id = ledger.project_id;

do $$
declare
    expected integer;
    restored integer;
    mismatched_projects integer;
begin
    select sum(active_users) into expected from ga4_project_view_backfill;
    select count(*) into restored
    from ga4_project_view_backfill source
    cross join lateral generate_series(1, source.active_users) series(viewer_number)
    join public.project_views view_row
      on view_row.project_id = source.project_id
     and view_row.viewed_on = source.viewed_on
     and view_row.viewer_hash = encode(extensions.digest(pg_catalog.convert_to(
        'ga4-backfill-20260928:' || to_char(source.viewed_on, 'YYYY-MM-DD') || ':' ||
        source.project_id || ':' || series.viewer_number, 'UTF8'
     ), 'sha256'), 'hex');

    select count(*) into mismatched_projects
    from public.projects project
    where project.id in (select distinct project_id from ga4_project_view_backfill)
      and project.view_count <> (select count(*) from public.project_views view_row
                                 where view_row.project_id = project.id);

    if restored <> expected or mismatched_projects <> 0 then
        raise exception 'Backfill verification failed: expected %, restored %, mismatches %',
            expected, restored, mismatched_projects;
    end if;
end
$$;

commit;

-- Expected result: restored_ga4_views = 1841 and counter_mismatches = 0.
with source(viewed_on, project_id, active_users) as (
    select * from (values
        ('2026-09-22'::date, '4f013e01-2de4-46d5-a7db-073058a314e8'::uuid, 38),
        ('2026-09-22', '5cb9d672-b4e7-4eb6-9009-1aae676e9570', 29),
        ('2026-09-22', '69a8c0c3-4221-467d-9096-0fe68d292311', 3),
        ('2026-09-22', '1b1d56ff-1937-4a59-a74f-909aef09f251', 18),
        ('2026-09-23', '4f013e01-2de4-46d5-a7db-073058a314e8', 2),
        ('2026-09-23', '5cb9d672-b4e7-4eb6-9009-1aae676e9570', 286),
        ('2026-09-23', '1b1d56ff-1937-4a59-a74f-909aef09f251', 14),
        ('2026-09-24', '5cb9d672-b4e7-4eb6-9009-1aae676e9570', 442),
        ('2026-09-25', '5cb9d672-b4e7-4eb6-9009-1aae676e9570', 299),
        ('2026-09-26', '5cb9d672-b4e7-4eb6-9009-1aae676e9570', 384),
        ('2026-09-26', 'b20f3c1d-cbb8-4be6-93bd-6a4768ab4486', 1),
        ('2026-09-26', 'a06219fe-9c5e-48f2-bd36-c289c4d158e5', 3),
        ('2026-09-26', 'e758068e-fb8d-4faa-8258-2b191b189ca5', 1),
        ('2026-09-26', '74bcaa21-64fd-4313-83ce-6a65eff1431a', 1),
        ('2026-09-26', '682d5011-7d76-4490-b883-0c481dfb0277', 1),
        ('2026-09-26', '718ee7fd-bb1c-4789-b4dc-8a8a70731528', 1),
        ('2026-09-26', '247dba95-5582-44be-8afe-e6bf42925d3a', 1),
        ('2026-09-27', '5cb9d672-b4e7-4eb6-9009-1aae676e9570', 316),
        ('2026-09-27', 'e758068e-fb8d-4faa-8258-2b191b189ca5', 1)
    ) data
), restored as (
    select count(*) as restored_ga4_views
    from source
    cross join lateral generate_series(1, source.active_users) series(n)
    join public.project_views view_row
      on view_row.project_id = source.project_id
     and view_row.viewed_on = source.viewed_on
     and view_row.viewer_hash = encode(extensions.digest(pg_catalog.convert_to(
        'ga4-backfill-20260928:' || to_char(source.viewed_on, 'YYYY-MM-DD') || ':' || source.project_id || ':' || series.n,
        'UTF8'), 'sha256'), 'hex')
), mismatches as (
    select count(*) as counter_mismatches
    from public.projects project
    where project.id in (select distinct project_id from source)
      and project.view_count <> (select count(*) from public.project_views view_row
                                 where view_row.project_id = project.id)
)
select restored_ga4_views, counter_mismatches from restored cross join mismatches;
