create table if not exists public.account_deletion_requests (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references public.profiles(id) on delete cascade,
    email text,
    request_note text check (request_note is null or char_length(request_note) <= 500),
    status text not null default 'open' check (status in ('open', 'reviewing', 'resolved', 'cancelled')),
    requested_at timestamptz not null default now(),
    reviewed_at timestamptz,
    resolved_at timestamptz,
    operator_note text,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create index if not exists account_deletion_requests_user_status_idx
on public.account_deletion_requests(user_id, status, requested_at desc);

create unique index if not exists account_deletion_requests_active_user_idx
on public.account_deletion_requests(user_id)
where status in ('open', 'reviewing');

grant select, update on public.account_deletion_requests to authenticated;
revoke insert, delete on public.account_deletion_requests from anon, authenticated;

alter table public.account_deletion_requests enable row level security;

drop policy if exists "Users can read own account deletion requests" on public.account_deletion_requests;
create policy "Users can read own account deletion requests"
on public.account_deletion_requests for select
using (auth.uid() = user_id);

drop policy if exists "Admins can read account deletion requests" on public.account_deletion_requests;
create policy "Admins can read account deletion requests"
on public.account_deletion_requests for select
using (
    exists (
        select 1
        from public.profiles
        where profiles.id = auth.uid()
          and profiles.role = 'admin'
    )
);

drop policy if exists "Admins can update account deletion requests" on public.account_deletion_requests;
create policy "Admins can update account deletion requests"
on public.account_deletion_requests for update
using (
    exists (
        select 1
        from public.profiles
        where profiles.id = auth.uid()
          and profiles.role = 'admin'
    )
)
with check (
    exists (
        select 1
        from public.profiles
        where profiles.id = auth.uid()
          and profiles.role = 'admin'
    )
);
