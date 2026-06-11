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

create table if not exists public.projects (
    id uuid primary key default gen_random_uuid(),
    author_id uuid not null references public.profiles(id) on delete cascade,
    title text not null,
    category text not null,
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

create index if not exists projects_author_id_idx on public.projects(author_id);
create index if not exists projects_category_idx on public.projects(category);
create index if not exists projects_created_at_idx on public.projects(created_at desc);
create index if not exists likes_user_id_idx on public.likes(user_id);

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

drop policy if exists "Profiles are readable by everyone" on public.profiles;
create policy "Profiles are readable by everyone"
on public.profiles for select
using (true);

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
