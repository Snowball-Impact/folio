-- Security hardening: client roles and Power BI report identifiers are server-managed.
-- Apply this migration to every Supabase environment after deploying the matching app code.

-- A profile owner may edit only presentation fields. In particular, role is never client-writable.
-- New profile rows are created exclusively by public.handle_new_user(), a server-owned trigger.
revoke insert, update, delete on table public.profiles from anon, authenticated;
grant update (name, organization, bio, avatar_url) on table public.profiles to authenticated;

drop policy if exists "Users can create own profile" on public.profiles;

-- Embed report and dataset IDs are privileged server-side Power BI metadata. Client writes could
-- otherwise cause the token endpoint to mint an embed token for a report chosen by the attacker.
revoke insert, update, delete on table public.powerbi_reports from authenticated;

drop policy if exists "Project authors can create own Power BI reports" on public.powerbi_reports;
drop policy if exists "Project authors can update own Power BI reports" on public.powerbi_reports;
drop policy if exists "Project authors can delete own Power BI reports" on public.powerbi_reports;
