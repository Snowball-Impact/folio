-- Apply this once in Supabase SQL Editor when an authenticated author can
-- edit a public project but receives 42501 while making it private.

begin;

grant select on public.projects to anon;
grant select, insert, update, delete on public.projects to authenticated;

drop policy if exists "Public projects are readable by everyone" on public.projects;
create policy "Public projects are readable by everyone"
on public.projects for select
using (is_public = true);

drop policy if exists "Users can read own projects" on public.projects;
create policy "Users can read own projects"
on public.projects for select
to authenticated
using ((select auth.uid()) = author_id);

drop policy if exists "Users can update own projects" on public.projects;
create policy "Users can update own projects"
on public.projects for update
to authenticated
using ((select auth.uid()) = author_id)
with check ((select auth.uid()) = author_id);

commit;
