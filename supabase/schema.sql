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
    ai_summary text,
    tags text[] not null default '{}',
    view_count integer not null default 0,
    is_public boolean not null default true,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists public.likes (
    project_id uuid not null references public.projects(id) on delete cascade,
    user_id uuid not null references public.profiles(id) on delete cascade,
    created_at timestamptz not null default now(),
    primary key (project_id, user_id)
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
create index if not exists likes_user_id_idx on public.likes(user_id);
create index if not exists project_views_project_date_idx on public.project_views(project_id, viewed_on);
create index if not exists policy_versions_type_active_idx on public.policy_versions(policy_type, is_active, effective_at desc);
create index if not exists user_policy_consents_user_id_idx on public.user_policy_consents(user_id);
create index if not exists user_policy_consents_policy_version_id_idx on public.user_policy_consents(policy_version_id);

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

alter table public.profiles enable row level security;
alter table public.projects enable row level security;
alter table public.likes enable row level security;
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
using (is_public = true);

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

insert into public.policy_versions (policy_type, version, title, content, summary, effective_at, is_active)
values
    (
        'terms',
        '2026-06-23',
        'FOLIO 서비스 이용약관',
        'FOLIO는 데이터 분석 프로젝트를 포트폴리오 자산으로 등록, 탐색, 공유하는 서비스입니다.

1. 사용자는 본인이 등록하는 프로젝트 정보와 첨부 링크에 대해 필요한 권리를 보유해야 합니다.
2. 타인의 개인정보, 저작권, 영업비밀 또는 법령을 침해하는 콘텐츠를 등록할 수 없습니다.
3. 서비스 운영자는 안정적인 서비스 운영과 정책 위반 대응을 위해 게시물을 제한하거나 삭제할 수 있습니다.
4. 서비스는 MVP 단계로 제공되며, 기능과 정책은 사전 고지 후 변경될 수 있습니다.
5. 사용자는 본 약관에 동의한 뒤 FOLIO 서비스를 이용할 수 있습니다.',
        'FOLIO 서비스 이용 조건에 동의합니다.',
        now(),
        true
    ),
    (
        'privacy',
        '2026-06-23',
        'FOLIO 개인정보 처리방침',
        'FOLIO는 회원가입, 로그인, 프로젝트 등록 및 서비스 운영을 위해 필요한 최소한의 개인정보를 처리합니다.

1. 수집 항목: 이메일, 이름, 소속, 서비스 이용 기록, 프로젝트 등록 정보
2. 이용 목적: 회원 식별, 로그인, 프로젝트 관리, 서비스 제공 및 운영 개선
3. 보관 기간: 회원 탈퇴 또는 처리 목적 달성 시까지 보관하며, 법령상 보관 의무가 있는 경우 해당 기간 동안 보관합니다.
4. 제3자 제공: 법령에 따른 경우를 제외하고 사용자의 동의 없이 개인정보를 제3자에게 제공하지 않습니다.
5. 사용자는 개인정보 열람, 정정, 삭제, 처리정지를 요청할 수 있습니다.',
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
