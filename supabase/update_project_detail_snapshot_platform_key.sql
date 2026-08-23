-- Apply this once in Supabase SQL Editor before the Svelte public-detail
-- migration. Some remote databases have an older project_detail_snapshot()
-- response that omits platform_key even though the canonical schema includes it.

drop function if exists public.project_detail_snapshot(uuid);

create or replace function public.project_detail_snapshot(
    p_project_id uuid
)
returns jsonb
language sql
stable
security definer
set search_path = public
as $$
with
selected_project as (
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
        p.platform_key,
        p.project_type,
        p.status,
        p.embed_status,
        p.is_public,
        p.view_count,
        p.created_at,
        p.updated_at
    from public.projects p
    where p.id = p_project_id
      and p.is_public = true
      and coalesce(p.status, 'published') <> 'deleted'
    limit 1
),
like_counts as (
    select l.project_id, count(*)::integer as like_count
    from public.likes l
    join selected_project sp on sp.id = l.project_id
    group by l.project_id
),
comment_counts as (
    select c.project_id, count(*)::integer as comment_count
    from public.comments c
    join selected_project sp on sp.id = c.project_id
    group by c.project_id
)
select
    case
        when sp.id is null then null
        else jsonb_build_object(
            'id', sp.id,
            'author_id', sp.author_id,
            'title', sp.title,
            'one_liner', sp.one_liner,
            'problem', sp.problem,
            'dataset', sp.dataset,
            'process', sp.process,
            'insights', sp.insights,
            'tags', coalesce(to_jsonb(sp.tags), '[]'::jsonb),
            'thumbnail_url', sp.thumbnail_url,
            'power_bi_url', sp.power_bi_url,
            'report_url', sp.report_url,
            'github_url', sp.github_url,
            'platform_key', sp.platform_key,
            'project_type', sp.project_type,
            'status', sp.status,
            'embed_status', sp.embed_status,
            'is_public', sp.is_public,
            'view_count', sp.view_count,
            'created_at', sp.created_at,
            'updated_at', sp.updated_at,
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
            'comment_count', coalesce(cc.comment_count, 0)
        )
    end
from selected_project sp
left join public.public_profiles pp on pp.id = sp.author_id
left join like_counts lc on lc.project_id = sp.id
left join comment_counts cc on cc.project_id = sp.id;
$$;

revoke all on function public.project_detail_snapshot(uuid) from public;
grant execute on function public.project_detail_snapshot(uuid) to anon, authenticated;
