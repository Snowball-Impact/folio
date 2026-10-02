-- Repair the trusted embed URL constraint added by
-- harden_public_security_boundaries.sql. PostgreSQL regular-expression strings
-- do not need the JavaScript-style double escaping that was previously used.
-- Character classes keep the literal-dot intent unambiguous.

begin;

alter table public.projects
drop constraint if exists projects_power_bi_url_allowed_check;

alter table public.projects
add constraint projects_power_bi_url_allowed_check
check (
    power_bi_url is null
    or power_bi_url ~* '^https://(app[.]powerbi[.]com|app[.]fabric[.]microsoft[.]com|public[.]tableau[.]com|lookerstudio[.]google[.]com|datastudio[.]google[.]com|share[.]streamlit[.]io|[a-z0-9-]+[.]streamlit[.]app|[a-z0-9-]+[.]github[.]io)(:[0-9]+)?([/?#]|$)'
) not valid;

-- Existing rows are intentionally validated after installing the corrected
-- expression. If an unexpected legacy host exists, this statement fails
-- without weakening checks for future writes.
alter table public.projects
validate constraint projects_power_bi_url_allowed_check;

commit;
