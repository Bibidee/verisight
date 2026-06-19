-- VeriSight initial schema, RLS, and storage bucket.
-- Source of truth for product state; GenLayer remains source of truth for verdicts.

create extension if not exists pgcrypto;

-- ============================================================ profiles
create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  email text not null,
  display_name text,
  role text not null default 'user' check (role in ('user','admin')),
  onboarding_completed boolean not null default false,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- ============================================================ wallets
create table if not exists public.wallets (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null unique references auth.users(id) on delete cascade,
  address text not null unique,
  encrypted_private_key bytea not null,
  encryption_version int not null default 1,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- ============================================================ wallet_key_wraps
create table if not exists public.wallet_key_wraps (
  id uuid primary key default gen_random_uuid(),
  wallet_id uuid not null references public.wallets(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  method text not null check (method in ('password','recovery_key')),
  encrypted_wallet_key bytea not null,
  salt bytea not null,
  kdf_params jsonb not null,
  created_at timestamptz not null default now(),
  unique (wallet_id, method)
);

-- ============================================================ workspaces
create table if not exists public.workspaces (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  name text not null,
  organisation_name text,
  business_function text,
  industry text,
  reporting_cadence text,
  primary_kpi_category text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create index if not exists workspaces_user_idx on public.workspaces(user_id);

-- ============================================================ insight_audit_cases
create table if not exists public.insight_audit_cases (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  workspace_id uuid not null references public.workspaces(id) on delete cascade,
  insight_claim text not null,
  business_question text,
  metric_name text,
  metric_definition text,
  time_period text,
  segment_context text,
  dataset_summary text,
  dashboard_context text,
  report_context text,
  analyst_notes text,
  candidate_interpretation_a text,
  candidate_interpretation_b text,
  candidate_interpretation_c text,
  status text not null default 'draft' check (status in
    ('draft','evidence_added','ready','submitted','consensus_pending','verdict_issued','needs_more_evidence','archived')),
  submitted_to_genlayer_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create index if not exists audit_cases_user_idx on public.insight_audit_cases(user_id);
create index if not exists audit_cases_workspace_idx on public.insight_audit_cases(workspace_id);

-- ============================================================ evidence_files
create table if not exists public.evidence_files (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  audit_case_id uuid not null references public.insight_audit_cases(id) on delete cascade,
  file_url text not null,
  file_path text not null,
  file_bucket text not null default 'evidence',
  file_type text not null,
  file_size int not null,
  evidence_hash text not null,
  uploaded_by uuid references auth.users(id),
  created_at timestamptz not null default now()
);
create index if not exists evidence_case_idx on public.evidence_files(audit_case_id);

-- ============================================================ data_snapshots
create table if not exists public.data_snapshots (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  audit_case_id uuid not null references public.insight_audit_cases(id) on delete cascade,
  source_type text,
  source_url text,
  snapshot_json jsonb not null,
  snapshot_hash text not null,
  created_at timestamptz not null default now()
);

-- ============================================================ genlayer_audit_verdicts
create table if not exists public.genlayer_audit_verdicts (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  audit_case_id uuid not null references public.insight_audit_cases(id) on delete cascade,
  contract_address text not null,
  transaction_hash text not null,
  audit_id_on_chain text,
  verdict text,
  support_level text,
  confidence_label text,
  selected_interpretation text,
  reasoning_summary text,
  evidence_digest text,
  unsupported_assumptions jsonb,
  business_risk text,
  consensus_status text,
  consensus_timestamp timestamptz,
  created_at timestamptz not null default now()
);
create index if not exists verdicts_case_idx on public.genlayer_audit_verdicts(audit_case_id);

-- ============================================================ recovery_audit_logs
create table if not exists public.recovery_audit_logs (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  wallet_id uuid references public.wallets(id) on delete set null,
  action text not null,
  ip_address text,
  user_agent text,
  created_at timestamptz not null default now()
);

-- ============================================================ admin_review_notes
create table if not exists public.admin_review_notes (
  id uuid primary key default gen_random_uuid(),
  audit_case_id uuid not null references public.insight_audit_cases(id) on delete cascade,
  admin_user_id uuid not null references auth.users(id) on delete cascade,
  note text not null,
  created_at timestamptz not null default now()
);

-- ============================================================ contract_activity_logs
create table if not exists public.contract_activity_logs (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) on delete set null,
  audit_case_id uuid references public.insight_audit_cases(id) on delete set null,
  contract_address text not null,
  transaction_hash text,
  action text not null,
  status text not null,
  error_message text,
  created_at timestamptz not null default now()
);

-- ============================================================ RLS
alter table public.profiles                enable row level security;
alter table public.wallets                 enable row level security;
alter table public.wallet_key_wraps        enable row level security;
alter table public.workspaces              enable row level security;
alter table public.insight_audit_cases     enable row level security;
alter table public.evidence_files          enable row level security;
alter table public.data_snapshots          enable row level security;
alter table public.genlayer_audit_verdicts enable row level security;
alter table public.recovery_audit_logs     enable row level security;
alter table public.admin_review_notes      enable row level security;
alter table public.contract_activity_logs  enable row level security;

-- helper: is_admin
create or replace function public.is_admin(uid uuid) returns boolean
  language sql stable as $$
    select coalesce((select role = 'admin' from public.profiles where id = uid), false);
  $$;

-- Generic owner policies
do $$
declare t text;
begin
  foreach t in array array[
    'profiles','wallets','wallet_key_wraps','workspaces','insight_audit_cases',
    'evidence_files','data_snapshots','genlayer_audit_verdicts',
    'recovery_audit_logs'
  ] loop
    execute format('drop policy if exists "%s_owner_select" on public.%I;', t, t);
    execute format('drop policy if exists "%s_owner_insert" on public.%I;', t, t);
    execute format('drop policy if exists "%s_owner_update" on public.%I;', t, t);
    execute format('drop policy if exists "%s_owner_delete" on public.%I;', t, t);
  end loop;
end $$;

-- profiles: id = auth.uid()
create policy "profiles_owner_select" on public.profiles
  for select using (id = auth.uid() or public.is_admin(auth.uid()));
create policy "profiles_owner_insert" on public.profiles
  for insert with check (id = auth.uid());
create policy "profiles_owner_update" on public.profiles
  for update using (id = auth.uid()) with check (id = auth.uid());

-- standard user_id policies
create policy "wallets_owner_select" on public.wallets
  for select using (user_id = auth.uid() or public.is_admin(auth.uid()));
create policy "wallets_owner_insert" on public.wallets
  for insert with check (user_id = auth.uid());
create policy "wallets_owner_update" on public.wallets
  for update using (user_id = auth.uid()) with check (user_id = auth.uid());

create policy "wallet_key_wraps_owner_select" on public.wallet_key_wraps
  for select using (user_id = auth.uid());
create policy "wallet_key_wraps_owner_insert" on public.wallet_key_wraps
  for insert with check (user_id = auth.uid());
create policy "wallet_key_wraps_owner_update" on public.wallet_key_wraps
  for update using (user_id = auth.uid()) with check (user_id = auth.uid());
create policy "wallet_key_wraps_owner_delete" on public.wallet_key_wraps
  for delete using (user_id = auth.uid());

create policy "workspaces_owner_select" on public.workspaces
  for select using (user_id = auth.uid() or public.is_admin(auth.uid()));
create policy "workspaces_owner_insert" on public.workspaces
  for insert with check (user_id = auth.uid());
create policy "workspaces_owner_update" on public.workspaces
  for update using (user_id = auth.uid()) with check (user_id = auth.uid());
create policy "workspaces_owner_delete" on public.workspaces
  for delete using (user_id = auth.uid());

create policy "insight_audit_cases_owner_select" on public.insight_audit_cases
  for select using (user_id = auth.uid() or public.is_admin(auth.uid()));
create policy "insight_audit_cases_owner_insert" on public.insight_audit_cases
  for insert with check (user_id = auth.uid());
create policy "insight_audit_cases_owner_update" on public.insight_audit_cases
  for update using (user_id = auth.uid()) with check (user_id = auth.uid());
create policy "insight_audit_cases_owner_delete" on public.insight_audit_cases
  for delete using (user_id = auth.uid());

create policy "evidence_files_owner_select" on public.evidence_files
  for select using (user_id = auth.uid() or public.is_admin(auth.uid()));
create policy "evidence_files_owner_insert" on public.evidence_files
  for insert with check (user_id = auth.uid());
create policy "evidence_files_owner_delete" on public.evidence_files
  for delete using (user_id = auth.uid());

create policy "data_snapshots_owner_select" on public.data_snapshots
  for select using (user_id = auth.uid() or public.is_admin(auth.uid()));
create policy "data_snapshots_owner_insert" on public.data_snapshots
  for insert with check (user_id = auth.uid());

create policy "genlayer_audit_verdicts_owner_select" on public.genlayer_audit_verdicts
  for select using (user_id = auth.uid() or public.is_admin(auth.uid()));
-- inserts to verdicts come from the server via service role; no user insert policy.

create policy "recovery_audit_logs_owner_select" on public.recovery_audit_logs
  for select using (user_id = auth.uid() or public.is_admin(auth.uid()));
-- inserts via service role from server actions.

-- admin-only tables
drop policy if exists "admin_review_notes_admin_all" on public.admin_review_notes;
create policy "admin_review_notes_admin_all" on public.admin_review_notes
  for all using (public.is_admin(auth.uid())) with check (public.is_admin(auth.uid()));

drop policy if exists "contract_activity_logs_owner_select" on public.contract_activity_logs;
create policy "contract_activity_logs_owner_select" on public.contract_activity_logs
  for select using (user_id = auth.uid() or public.is_admin(auth.uid()));

-- ============================================================ updated_at triggers
create or replace function public.touch_updated_at() returns trigger
  language plpgsql as $$
  begin new.updated_at = now(); return new; end $$;

do $$
declare t text;
begin
  foreach t in array array['profiles','wallets','workspaces','insight_audit_cases'] loop
    execute format('drop trigger if exists trg_%s_touch on public.%I;', t, t);
    execute format('create trigger trg_%s_touch before update on public.%I
                    for each row execute procedure public.touch_updated_at();', t, t);
  end loop;
end $$;

-- ============================================================ Storage bucket
insert into storage.buckets (id, name, public)
  values ('evidence','evidence', false)
  on conflict (id) do nothing;

drop policy if exists "evidence_owner_read"   on storage.objects;
drop policy if exists "evidence_owner_write"  on storage.objects;
drop policy if exists "evidence_owner_delete" on storage.objects;

create policy "evidence_owner_read" on storage.objects
  for select using (
    bucket_id = 'evidence' and (
      auth.uid()::text = (storage.foldername(name))[1] or public.is_admin(auth.uid())
    )
  );
create policy "evidence_owner_write" on storage.objects
  for insert with check (
    bucket_id = 'evidence' and auth.uid()::text = (storage.foldername(name))[1]
  );
create policy "evidence_owner_delete" on storage.objects
  for delete using (
    bucket_id = 'evidence' and auth.uid()::text = (storage.foldername(name))[1]
  );
