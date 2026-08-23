create table if not exists public.profiles (
    id uuid primary key references auth.users(id) on delete cascade,
    email text not null,
    name text not null,
    organization text,
    bio text,
    avatar_url text,
    role text not null default 'member',
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists public.policy_versions (
    id uuid primary key default gen_random_uuid(),
    policy_type text not null check (policy_type in ('terms', 'privacy')),
    version text not null,
    title text not null,
    content text,
    content_url text,
    summary text,
    effective_at timestamptz not null default now(),
    is_active boolean not null default true,
    created_at timestamptz not null default now(),
    unique (policy_type, version)
);

-- `content` was added after some projects already created policy_versions
-- without it. `create table if not exists` does not retrofit columns onto an
-- existing table, so add it explicitly for deployments created before this.
alter table public.policy_versions add column if not exists content text;

create table if not exists public.user_policy_consents (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references public.profiles(id) on delete cascade,
    policy_version_id uuid not null references public.policy_versions(id) on delete restrict,
    consented_at timestamptz not null default now(),
    ip_address inet,
    user_agent text,
    created_at timestamptz not null default now(),
    unique (user_id, policy_version_id)
);

create table if not exists public.projects (
    id uuid primary key default gen_random_uuid(),
    author_id uuid not null references public.profiles(id) on delete cascade,
    title text not null,
    one_liner text,
    problem text not null,
    dataset text,
    process text,
    insights text not null,
    power_bi_url text,
    report_url text,
    github_url text,
    thumbnail_url text,
    thumbnail_mode text not null default 'auto_cover' check (thumbnail_mode in ('auto_cover', 'manual_url', 'capture', 'upload')),
    project_type text not null default 'other' check (project_type in ('powerbi', 'tableau', 'looker', 'streamlit', 'notebook', 'html_report', 'markdown_report', 'web', 'other')),
    status text not null default 'published' check (status in ('processing', 'published', 'failed', 'deleted')),
    embed_status text not null default 'external_only' check (embed_status in ('supported', 'external_only', 'failed')),
    ai_summary text,
    tags text[] not null default '{}',
    view_count integer not null default 0,
    is_public boolean not null default true,
    published_at timestamptz,
    deleted_at timestamptz,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists public.powerbi_reports (
    id uuid primary key default gen_random_uuid(),
    project_id uuid not null references public.projects(id) on delete cascade,
    workspace_id text not null,
    report_id text,
    dataset_id text,
    embed_url text,
    web_url text,
    import_id text,
    import_status text,
    error_code text,
    error_message text,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    unique (project_id)
);

create table if not exists public.likes (
    project_id uuid not null references public.projects(id) on delete cascade,
    user_id uuid not null references public.profiles(id) on delete cascade,
    created_at timestamptz not null default now(),
    primary key (project_id, user_id)
);

create table if not exists public.comments (
    id uuid primary key default gen_random_uuid(),
    project_id uuid not null references public.projects(id) on delete cascade,
    author_id uuid not null references public.profiles(id) on delete cascade,
    parent_id uuid references public.comments(id) on delete cascade,
    body text not null,
    depth integer not null default 0 check (depth in (0, 1)),
    is_deleted boolean not null default false,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists public.project_comment_reads (
    project_id uuid not null references public.projects(id) on delete cascade,
    user_id uuid not null references public.profiles(id) on delete cascade,
    last_read_at timestamptz not null default now(),
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    primary key (project_id, user_id)
);

create table if not exists public.notifications (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references public.profiles(id) on delete cascade,
    actor_id uuid references public.profiles(id) on delete set null,
    project_id uuid references public.projects(id) on delete cascade,
    comment_id uuid references public.comments(id) on delete cascade,
    type text not null check (type in ('project_comment')),
    title text not null,
    body text,
    is_read boolean not null default false,
    read_at timestamptz,
    created_at timestamptz not null default now()
);

create extension if not exists pgcrypto with schema extensions;

create table if not exists public.project_views (
    project_id uuid not null references public.projects(id) on delete cascade,
    viewer_hash text not null,
    viewed_on date not null,
    created_at timestamptz not null default now(),
    primary key (project_id, viewer_hash, viewed_on)
);

create index if not exists projects_author_id_idx on public.projects(author_id);
create index if not exists projects_created_at_idx on public.projects(created_at desc);
create index if not exists powerbi_reports_project_id_idx on public.powerbi_reports(project_id);
create index if not exists powerbi_reports_import_id_idx on public.powerbi_reports(import_id);
create index if not exists likes_user_id_idx on public.likes(user_id);
create index if not exists comments_project_id_idx on public.comments(project_id, created_at);
create index if not exists comments_parent_id_idx on public.comments(parent_id);
create index if not exists comments_author_id_idx on public.comments(author_id);
create index if not exists project_comment_reads_user_id_idx on public.project_comment_reads(user_id);
create index if not exists notifications_user_read_created_idx on public.notifications(user_id, is_read, created_at desc);
create index if not exists notifications_project_id_idx on public.notifications(project_id);
create unique index if not exists notifications_project_comment_unique_idx
on public.notifications(comment_id)
where type = 'project_comment' and comment_id is not null;
create index if not exists project_views_project_date_idx on public.project_views(project_id, viewed_on);
create index if not exists policy_versions_type_active_idx on public.policy_versions(policy_type, is_active, effective_at desc);
create index if not exists user_policy_consents_user_id_idx on public.user_policy_consents(user_id);
create index if not exists user_policy_consents_policy_version_id_idx on public.user_policy_consents(policy_version_id);

alter table public.projects
add column if not exists thumbnail_mode text not null default 'auto_cover';

alter table public.projects
add column if not exists project_type text not null default 'other';

alter table public.projects
add column if not exists status text not null default 'published';

alter table public.projects
add column if not exists embed_status text not null default 'external_only';

alter table public.projects
add column if not exists published_at timestamptz;

alter table public.projects
add column if not exists deleted_at timestamptz;

create index if not exists projects_status_created_at_idx on public.projects(status, created_at desc);
create index if not exists projects_project_type_idx on public.projects(project_type);
create index if not exists projects_public_created_at_idx
on public.projects(created_at desc, id desc)
where is_public = true and status = 'published';
create index if not exists projects_public_view_count_idx
on public.projects(view_count desc, created_at desc, id desc)
where is_public = true and status = 'published';

alter table public.projects
drop constraint if exists projects_thumbnail_mode_check;

alter table public.projects
add constraint projects_thumbnail_mode_check
check (thumbnail_mode in ('auto_cover', 'manual_url', 'capture', 'upload'));

do $$
begin
    if not exists (
        select 1 from pg_constraint
        where conname = 'projects_project_type_check'
          and conrelid = 'public.projects'::regclass
    ) then
        alter table public.projects
        add constraint projects_project_type_check
        check (project_type in ('powerbi', 'tableau', 'looker', 'streamlit', 'notebook', 'html_report', 'markdown_report', 'web', 'other'));
    end if;
end $$;

do $$
begin
    if not exists (
        select 1 from pg_constraint
        where conname = 'projects_status_check'
          and conrelid = 'public.projects'::regclass
    ) then
        alter table public.projects
        add constraint projects_status_check
        check (status in ('processing', 'published', 'failed', 'deleted'));
    end if;
end $$;

do $$
begin
    if not exists (
        select 1 from pg_constraint
        where conname = 'projects_embed_status_check'
          and conrelid = 'public.projects'::regclass
    ) then
        alter table public.projects
        add constraint projects_embed_status_check
        check (embed_status in ('supported', 'external_only', 'failed'));
    end if;
end $$;

do $$
begin
    if not exists (
        select 1 from pg_constraint
        where conname = 'comments_body_length_check'
          and conrelid = 'public.comments'::regclass
    ) then
        alter table public.comments
        add constraint comments_body_length_check
        check (char_length(btrim(body)) between 1 and 1000);
    end if;
end $$;

create or replace view public.public_profiles as
select
    id,
    coalesce(nullif(name, ''), split_part(email, '@', 1)) as name,
    organization,
    avatar_url
from public.profiles;

grant select on public.public_profiles to anon, authenticated;
grant select on public.policy_versions to anon, authenticated;
grant select, insert on public.user_policy_consents to authenticated;
grant select on public.projects to anon;
grant select, insert, update, delete on public.projects to authenticated;
grant select on public.powerbi_reports to anon;
grant select, insert, update, delete on public.powerbi_reports to authenticated;
grant select on public.comments to anon;
grant select, insert, delete on public.comments to authenticated;
grant select, insert, update on public.project_comment_reads to authenticated;
grant select, insert, update on public.notifications to authenticated;

drop function if exists public.home_project_snapshot(integer, integer, integer);

create or replace function public.home_project_snapshot(
    p_limit integer default 6,
    p_tag_limit integer default 10,
    p_like_sample_limit integer default 120
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
        greatest(coalesce(p_like_sample_limit, 120), coalesce(p_limit, 6), 0) as like_sample_limit
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
),
popular_tags as (
    select tag
    from tag_counts
    order by tag_count desc, tag asc
    limit (select tag_limit from safe_args)
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

revoke all on function public.home_project_snapshot(integer, integer, integer) from public;
grant execute on function public.home_project_snapshot(integer, integer, integer) to anon, authenticated;

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

create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
    insert into public.profiles (id, email, name, organization)
    values (
        new.id,
        new.email,
        coalesce(new.raw_user_meta_data->>'name', split_part(new.email, '@', 1)),
        new.raw_user_meta_data->>'organization'
    )
    on conflict (id) do update
    set
        email = excluded.email,
        name = excluded.name,
        organization = excluded.organization,
        updated_at = now();

    return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
after insert on auth.users
for each row execute function public.handle_new_user();

create or replace function public.validate_comment_thread()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
declare
    parent_project_id uuid;
    parent_depth integer;
begin
    new.body := btrim(new.body);

    if new.parent_id is null then
        new.depth := 0;
        return new;
    end if;

    select project_id, depth
    into parent_project_id, parent_depth
    from public.comments
    where id = new.parent_id;

    if not found then
        raise exception 'Parent comment does not exist';
    end if;

    if parent_project_id <> new.project_id or parent_depth <> 0 then
        raise exception 'Replies are allowed only one level under a comment in the same project';
    end if;

    new.depth := 1;
    return new;
end;
$$;

drop trigger if exists validate_comment_thread_before_write on public.comments;
create trigger validate_comment_thread_before_write
before insert or update on public.comments
for each row execute function public.validate_comment_thread();

alter table public.profiles enable row level security;
alter table public.projects enable row level security;
alter table public.powerbi_reports enable row level security;
alter table public.likes enable row level security;
alter table public.comments enable row level security;
alter table public.project_comment_reads enable row level security;
alter table public.notifications enable row level security;
alter table public.project_views enable row level security;
alter table public.policy_versions enable row level security;
alter table public.user_policy_consents enable row level security;

revoke all on table public.project_views from anon, authenticated;

drop policy if exists "Profiles are readable by everyone" on public.profiles;
drop policy if exists "Users can read own profile" on public.profiles;
create policy "Users can read own profile"
on public.profiles for select
using (auth.uid() = id);

drop policy if exists "Users can create own profile" on public.profiles;
create policy "Users can create own profile"
on public.profiles for insert
with check (auth.uid() = id);

drop policy if exists "Users can update own profile" on public.profiles;
create policy "Users can update own profile"
on public.profiles for update
using (auth.uid() = id)
with check (auth.uid() = id);

drop policy if exists "Public projects are readable by everyone" on public.projects;
create policy "Public projects are readable by everyone"
on public.projects for select
using (is_public = true and status = 'published');

drop policy if exists "Users can read own projects" on public.projects;
create policy "Users can read own projects"
on public.projects for select
using (auth.uid() = author_id);

drop policy if exists "Users can create own projects" on public.projects;
create policy "Users can create own projects"
on public.projects for insert
with check (auth.uid() = author_id);

drop policy if exists "Users can update own projects" on public.projects;
create policy "Users can update own projects"
on public.projects for update
using (auth.uid() = author_id)
with check (auth.uid() = author_id);

drop policy if exists "Users can delete own projects" on public.projects;
create policy "Users can delete own projects"
on public.projects for delete
using (auth.uid() = author_id);

drop policy if exists "Visible Power BI reports are readable" on public.powerbi_reports;
create policy "Visible Power BI reports are readable"
on public.powerbi_reports for select
using (
    exists (
        select 1
        from public.projects
        where projects.id = powerbi_reports.project_id
          and (
              (projects.is_public = true and projects.status = 'published')
              or auth.uid() = projects.author_id
          )
    )
);

drop policy if exists "Project authors can create own Power BI reports" on public.powerbi_reports;
create policy "Project authors can create own Power BI reports"
on public.powerbi_reports for insert
with check (
    exists (
        select 1
        from public.projects
        where projects.id = powerbi_reports.project_id
          and projects.author_id = auth.uid()
    )
);

drop policy if exists "Project authors can update own Power BI reports" on public.powerbi_reports;
create policy "Project authors can update own Power BI reports"
on public.powerbi_reports for update
using (
    exists (
        select 1
        from public.projects
        where projects.id = powerbi_reports.project_id
          and projects.author_id = auth.uid()
    )
)
with check (
    exists (
        select 1
        from public.projects
        where projects.id = powerbi_reports.project_id
          and projects.author_id = auth.uid()
    )
);

drop policy if exists "Project authors can delete own Power BI reports" on public.powerbi_reports;
create policy "Project authors can delete own Power BI reports"
on public.powerbi_reports for delete
using (
    exists (
        select 1
        from public.projects
        where projects.id = powerbi_reports.project_id
          and projects.author_id = auth.uid()
    )
);

drop policy if exists "Likes are readable by everyone" on public.likes;
create policy "Likes are readable by everyone"
on public.likes for select
using (true);

drop policy if exists "Users can create own likes" on public.likes;
create policy "Users can create own likes"
on public.likes for insert
with check (auth.uid() = user_id);

drop policy if exists "Users can delete own likes" on public.likes;
create policy "Users can delete own likes"
on public.likes for delete
using (auth.uid() = user_id);

drop policy if exists "Comments are readable by everyone" on public.comments;
drop policy if exists "Visible project comments are readable" on public.comments;
create policy "Visible project comments are readable"
on public.comments for select
using (
    exists (
        select 1
        from public.projects
        where projects.id = comments.project_id
          and (
              (projects.is_public = true and projects.status = 'published')
              or auth.uid() = projects.author_id
          )
    )
);

drop policy if exists "Users can create own comments" on public.comments;
create policy "Users can create own comments"
on public.comments for insert
with check (
    auth.uid() = author_id
    and exists (
        select 1
        from public.projects
        where projects.id = comments.project_id
          and (
              (projects.is_public = true and projects.status = 'published')
              or auth.uid() = projects.author_id
          )
          and projects.status <> 'deleted'
    )
);

drop policy if exists "Users can delete own comments" on public.comments;
create policy "Users can delete own comments"
on public.comments for delete
using (auth.uid() = author_id);

drop policy if exists "Project authors can read own comment read state" on public.project_comment_reads;
create policy "Project authors can read own comment read state"
on public.project_comment_reads for select
using (
    auth.uid() = user_id
    and exists (
        select 1
        from public.projects
        where projects.id = project_comment_reads.project_id
          and projects.author_id = auth.uid()
    )
);

drop policy if exists "Project authors can create own comment read state" on public.project_comment_reads;
create policy "Project authors can create own comment read state"
on public.project_comment_reads for insert
with check (
    auth.uid() = user_id
    and exists (
        select 1
        from public.projects
        where projects.id = project_comment_reads.project_id
          and projects.author_id = auth.uid()
    )
);

drop policy if exists "Project authors can update own comment read state" on public.project_comment_reads;
create policy "Project authors can update own comment read state"
on public.project_comment_reads for update
using (
    auth.uid() = user_id
    and exists (
        select 1
        from public.projects
        where projects.id = project_comment_reads.project_id
          and projects.author_id = auth.uid()
    )
)
with check (
    auth.uid() = user_id
    and exists (
        select 1
        from public.projects
        where projects.id = project_comment_reads.project_id
          and projects.author_id = auth.uid()
    )
);

drop policy if exists "Users can read own notifications" on public.notifications;
create policy "Users can read own notifications"
on public.notifications for select
using (auth.uid() = user_id);

drop policy if exists "Users can update own notifications" on public.notifications;
create policy "Users can update own notifications"
on public.notifications for update
using (auth.uid() = user_id)
with check (auth.uid() = user_id);

drop policy if exists "Comment authors can create project comment notifications" on public.notifications;
create policy "Comment authors can create project comment notifications"
on public.notifications for insert
with check (
    type = 'project_comment'
    and actor_id = auth.uid()
    and user_id <> auth.uid()
    and project_id is not null
    and comment_id is not null
    and exists (
        select 1
        from public.projects
        where projects.id = notifications.project_id
          and projects.author_id = notifications.user_id
    )
    and exists (
        select 1
        from public.comments
        where comments.id = notifications.comment_id
          and comments.project_id = notifications.project_id
          and comments.author_id = auth.uid()
    )
);

drop policy if exists "Active policy versions are readable by everyone" on public.policy_versions;
create policy "Active policy versions are readable by everyone"
on public.policy_versions for select
using (is_active = true);

drop policy if exists "Users can read own policy consents" on public.user_policy_consents;
create policy "Users can read own policy consents"
on public.user_policy_consents for select
using (auth.uid() = user_id);

drop policy if exists "Users can create own policy consents" on public.user_policy_consents;
create policy "Users can create own policy consents"
on public.user_policy_consents for insert
with check (auth.uid() = user_id);

-- 새 버전을 활성화하기 전에 기존 활성 버전을 비활성화한다. 이미 동의한 사용자는
-- user_policy_consents가 이전 policy_version_id를 참조하므로 새 버전 재동의가 필요해진다.
update public.policy_versions
set is_active = false
where policy_type in ('terms', 'privacy')
  and version <> '2026-07-07';

insert into public.policy_versions (policy_type, version, title, content, summary, effective_at, is_active)
values
    (
        'terms',
        '2026-07-07',
        'FOLIO 서비스 이용약관',
        'FOLIO는 데이터 분석 프로젝트를 포트폴리오 자산으로 등록, 탐색, 공유하는 서비스입니다.

1. 사용자는 본인이 등록하는 프로젝트 정보와 첨부 링크에 대해 필요한 권리를 보유해야 합니다.
2. 타인의 개인정보, 저작권, 영업비밀 또는 법령을 침해하는 콘텐츠를 등록할 수 없습니다.
3. 서비스 운영자는 안정적인 서비스 운영과 정책 위반 대응을 위해 게시물을 제한하거나 삭제할 수 있습니다.
4. 서비스는 MVP 단계로 제공되며, 기능과 정책은 사전 고지 후 변경될 수 있습니다.
5. 서비스 운영자는 시스템 점검, 장애, 서비스 종료 등 불가피한 사정으로 서비스 제공을 일시적으로 중단하거나 종료할 수 있으며, 이 경우 사전에 공지합니다.
6. 서비스 운영자는 법령상 허용되는 범위에서 서비스 이용과 관련하여 발생한 손해에 대한 책임을 제한할 수 있습니다.
7. 본 약관과 관련한 분쟁은 대한민국 법령을 준거법으로 합니다.
8. 약관 문의: ggmaeng@gmail.com
9. 사용자는 본 약관에 동의한 뒤 FOLIO 서비스를 이용할 수 있습니다.

공고일자: 2026-07-07
시행일자: 2026-07-07',
        'FOLIO 서비스 이용 조건에 동의합니다.',
        now(),
        true
    ),
    (
        'privacy',
        '2026-07-07',
        'FOLIO 개인정보 처리방침',
        'FOLIO는 회원가입, 로그인, 프로젝트 등록 및 서비스 운영을 위해 필요한 최소한의 개인정보를 처리합니다.

1. 수집 항목: 이메일, 이름, 소속, 서비스 이용 기록, 프로젝트 등록 정보, 조회수 중복 집계 방지를 위한 익명 방문자 식별자
2. 이용 목적: 회원 식별, 로그인, 프로젝트 관리, 서비스 제공 및 운영 개선
3. 보유 및 이용 기간: 회원 탈퇴 또는 처리 목적 달성 시까지 보관하며, 법령상 보관 의무가 있는 경우 해당 기간 동안 보관합니다.
4. 제3자 제공: 법령에 따른 경우를 제외하고 사용자의 동의 없이 개인정보를 제3자에게 제공하지 않습니다.
5. 처리위탁: 데이터베이스 운영과 로그인 인증 기능을 위해 Supabase Inc.에 개인정보 처리를 위탁하고 있으며, 실제 데이터는 Northeast Asia(Seoul) 리전 서버에 저장됩니다.
6. 쿠키 등 자동 수집 장치: 로그인 상태 유지를 위한 암호화된 쿠키와, 프로젝트 조회수 중복 집계를 막기 위한 익명 방문자 식별 쿠키를 사용합니다. 사용자는 브라우저 설정에서 쿠키 저장을 거부할 수 있으나, 이 경우 로그인 유지와 조회수 집계 등 일부 기능이 제한될 수 있습니다.
7. 파기절차 및 방법: 개인정보는 보유 기간이 지나거나 처리 목적을 달성하면 지체 없이 파기합니다. 전자적 파일 형태로 저장된 개인정보는 복구할 수 없는 방법으로 삭제합니다.
8. 안전성 확보조치: 전송 구간 암호화(HTTPS), 비밀번호 암호화 저장, 데이터베이스 행 수준 보안(RLS)을 통한 접근 통제, 최소 권한 원칙에 따른 접근 권한 관리를 시행합니다.
9. 정보주체의 권리와 행사방법: 사용자는 언제든지 자신의 개인정보에 대한 열람, 정정, 삭제, 처리정지를 아래 연락처로 요청할 수 있습니다.
10. 개인정보 보호책임자(문의): 이메일 ggmaeng@gmail.com
11. 권익침해 구제방법: 개인정보 관련 분쟁이나 상담이 필요하면 개인정보분쟁조정위원회(국번없이 1833-6972), 개인정보침해신고센터(국번없이 118, privacy.kisa.or.kr), 대검찰청(국번없이 1301), 경찰청 사이버수사국(국번없이 182)에 문의할 수 있습니다.

공고일자: 2026-07-07
시행일자: 2026-07-07',
        '개인정보 수집 및 이용에 동의합니다.',
        now(),
        true
    )
on conflict (policy_type, version) do update
set
    title = excluded.title,
    content = excluded.content,
    summary = excluded.summary,
    is_active = excluded.is_active;
