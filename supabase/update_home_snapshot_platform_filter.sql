-- Apply this once in Supabase SQL Editor to let the Home gallery snapshot
-- filter projects by platform inside PostgreSQL.

create index if not exists likes_created_project_idx on public.likes(created_at desc, project_id);

drop function if exists public.home_project_snapshot(integer, integer, integer);
drop function if exists public.home_project_snapshot(integer, integer, integer, text);

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
set search_path = public
as $$
with
safe_args as (
    select
        greatest(coalesce(p_limit, 6), 0) as rail_limit,
        greatest(coalesce(p_tag_limit, 10), 0) as tag_limit,
        greatest(coalesce(p_like_sample_limit, 120), coalesce(p_limit, 6), 0) as like_sample_limit,
        nullif(lower(trim(coalesce(p_platform_key, ''))), '') as platform_key
),
visible_projects as (
    select
        p.id,
        p.author_id,
        p.title,
        p.one_liner,
        p.problem,
        p.dataset,
        p.process,
        p.insights,
        p.tags,
        p.thumbnail_url,
        p.power_bi_url,
        p.report_url,
        p.github_url,
        p.project_type,
        p.status,
        p.embed_status,
        p.is_public,
        p.view_count,
        p.created_at,
        p.updated_at
    from public.projects p
    where p.is_public = true
      and p.status = 'published'
      and (
          (select platform_key from safe_args) is null
          or (
              (select platform_key from safe_args) = 'powerbi'
              and (
                  exists (
                      select 1
                      from unnest(coalesce(p.tags, array[]::text[])) as tag
                      where lower(trim(tag)) in ('powerbi', 'power bi', 'pbi')
                  )
                  or lower(coalesce(p.power_bi_url, '')) like '%app.powerbi.com%'
                  or lower(coalesce(p.power_bi_url, '')) like '%powerbi.com%'
                  or lower(coalesce(p.report_url, '')) like '%app.powerbi.com%'
                  or lower(coalesce(p.report_url, '')) like '%powerbi.com%'
                  or lower(coalesce(p.github_url, '')) like '%app.powerbi.com%'
                  or lower(coalesce(p.github_url, '')) like '%powerbi.com%'
                  or lower(coalesce(p.thumbnail_url, '')) like '%app.powerbi.com%'
                  or lower(coalesce(p.thumbnail_url, '')) like '%powerbi.com%'
              )
          )
      )
),
recent_projects as (
    select vp.id, row_number() over (order by vp.created_at desc, vp.id desc) as rail_rank
    from visible_projects vp
    order by vp.created_at desc, vp.id desc
    limit (select rail_limit from safe_args)
),
viewed_projects as (
    select vp.id, row_number() over (order by vp.view_count desc, vp.created_at desc, vp.id desc) as rail_rank
    from visible_projects vp
    order by vp.view_count desc, vp.created_at desc, vp.id desc
    limit (select rail_limit from safe_args)
),
recent_likes as (
    select l.project_id, l.created_at
    from public.likes l
    join visible_projects vp on vp.id = l.project_id
    order by l.created_at desc
    limit (select like_sample_limit from safe_args)
),
liked_projects as (
    select
        rl.project_id as id,
        row_number() over (order by count(*) desc, max(rl.created_at) desc, rl.project_id desc) as rail_rank
    from recent_likes rl
    group by rl.project_id
    order by count(*) desc, max(rl.created_at) desc, rl.project_id desc
    limit (select rail_limit from safe_args)
),
project_pool as (
    select id from recent_projects
    union
    select id from viewed_projects
    union
    select id from liked_projects
),
like_counts as (
    select l.project_id, count(*)::integer as like_count
    from public.likes l
    join project_pool pool on pool.id = l.project_id
    group by l.project_id
),
comment_stats as (
    select
        c.project_id,
        count(*)::integer as comment_count,
        max(c.created_at) as latest_comment_at
    from public.comments c
    join project_pool pool on pool.id = c.project_id
    group by c.project_id
),
project_cards as (
    select
        vp.id,
        jsonb_build_object(
            'id', vp.id,
            'author_id', vp.author_id,
            'title', vp.title,
            'one_liner', vp.one_liner,
            'problem', vp.problem,
            'dataset', vp.dataset,
            'process', vp.process,
            'insights', vp.insights,
            'tags', coalesce(to_jsonb(vp.tags), '[]'::jsonb),
            'thumbnail_url', vp.thumbnail_url,
            'power_bi_url', vp.power_bi_url,
            'report_url', vp.report_url,
            'github_url', vp.github_url,
            'project_type', vp.project_type,
            'status', vp.status,
            'embed_status', vp.embed_status,
            'is_public', vp.is_public,
            'view_count', vp.view_count,
            'created_at', vp.created_at,
            'updated_at', vp.updated_at,
            'author',
                case
                    when pp.id is null then '{}'::jsonb
                    else jsonb_build_object(
                        'id', pp.id,
                        'name', pp.name,
                        'organization', pp.organization
                    )
                end,
            'like_count', coalesce(lc.like_count, 0),
            'comment_count', coalesce(cs.comment_count, 0),
            'latest_comment_at', cs.latest_comment_at
        ) as project_json
    from visible_projects vp
    join project_pool pool on pool.id = vp.id
    left join public.public_profiles pp on pp.id = vp.author_id
    left join like_counts lc on lc.project_id = vp.id
    left join comment_stats cs on cs.project_id = vp.id
),
tag_counts as (
    select tag, count(*) as tag_count
    from visible_projects vp
    cross join unnest(vp.tags) as tag
    group by tag
)
select jsonb_build_object(
    'total_project_count', (select count(*) from visible_projects),
    'popular_tags', coalesce((
        select jsonb_agg(tag order by tag_count desc, tag asc)
        from (
            select tag, tag_count
            from tag_counts
            order by tag_count desc, tag asc
            limit (select tag_limit from safe_args)
        ) ranked_tags
    ), '[]'::jsonb),
    'recent_projects', coalesce((
        select jsonb_agg(pc.project_json order by rp.rail_rank)
        from recent_projects rp
        join project_cards pc on pc.id = rp.id
    ), '[]'::jsonb),
    'viewed_projects', coalesce((
        select jsonb_agg(pc.project_json order by vp.rail_rank)
        from viewed_projects vp
        join project_cards pc on pc.id = vp.id
    ), '[]'::jsonb),
    'liked_projects', coalesce((
        select jsonb_agg(pc.project_json order by lp.rail_rank)
        from liked_projects lp
        join project_cards pc on pc.id = lp.id
    ), '[]'::jsonb)
);
$$;

revoke all on function public.home_project_snapshot(integer, integer, integer, text) from public;
grant execute on function public.home_project_snapshot(integer, integer, integer, text) to anon, authenticated;
