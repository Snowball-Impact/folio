revoke insert, update, delete on public.user_policy_consents from anon, authenticated;
grant select on public.user_policy_consents to authenticated;

drop policy if exists "Users can create own policy consents" on public.user_policy_consents;
