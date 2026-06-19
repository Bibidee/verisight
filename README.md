# VeriSight

**Analytics Assurance Desk** — verifies whether dashboard insights, KPI narratives, and AI-generated report summaries are actually supported by the underlying data. Final verdicts are produced by **GenLayer validator consensus**, not by VeriSight.

- **Frontend:** Next.js 15 · App Router · Tailwind · TypeScript
- **Auth + DB + Storage:** Supabase
- **Wallet:** auto-provisioned embedded wallet, AES-256-GCM with PBKDF2 (600k iters) + 24-word recovery phrase
- **Source of truth for verdicts:** GenLayer Intelligent Contract `VeriSightInsightAuditor` on StudioNet

## Local dev

```bash
npm install
cp .env.example .env.local   # then fill values (see below)
npm run dev
```

Then open http://localhost:3000.

## Environment variables

| Var | Purpose |
|---|---|
| `NEXT_PUBLIC_SUPABASE_URL` | Supabase project URL |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Supabase anon key (browser) |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase service role key (server only) |
| `NEXT_PUBLIC_GENLAYER_RPC_URL` | StudioNet RPC, e.g. `https://studio.genlayer.com:8443/api` |
| `NEXT_PUBLIC_GENLAYER_CHAIN_ID` | `61999` for StudioNet |
| `NEXT_PUBLIC_VERISIGHT_CONTRACT_ADDRESS` | Deployed `VeriSightInsightAuditor` contract address |
| `GENLAYER_RELAY_PRIVATE_KEY` | EOA private key used by VeriSight to dispatch `submit_audit` |
| `GENLAYER_RELAY_ADDRESS` | Its address (must be funded with StudioNet GEN) |
| `WALLET_PEPPER` | 64-hex secret used in PBKDF2 derivation for wallet encryption |

## Supabase setup

Apply, in order:

1. `supabase/migrations/0001_init.sql` — tables, RLS, storage bucket.
2. `supabase/migrations/0002_text_blobs.sql` — encrypted-blob columns as text.
3. `supabase/migrations/0003_grants.sql` — explicit table grants for `anon`, `authenticated`, `service_role`.

Apply them in the Supabase SQL editor (or `supabase db push` once linked).

Optional:

- `supabase/migrations/0004_make_me_admin.example.sql` — promote your account to `role = 'admin'` so `/admin` becomes visible.

## GenLayer contract

The contract lives at `contracts/verisight_insight_auditor.py`. Deploy it via [GenLayer Studio](https://studio.genlayer.com) on **StudioNet** (chain id `61999`). After deploy, paste the address into `NEXT_PUBLIC_VERISIGHT_CONTRACT_ADDRESS`.

The contract uses `gl.eq_principle.prompt_non_comparative` to ask validators to **independently** decide whether the insight is supported by the evidence. Equivalence criteria collapse semantic variations into one of:

- `supported` · `partially_supported` · `unsupported` · `misleading` · `needs_more_evidence`

The contract refuses any audit packet that pre-decides a verdict.

## Relay signer

Server actions dispatch `submit_audit` using a server-side signer (`GENLAYER_RELAY_PRIVATE_KEY`). This is independent of users' embedded wallets and exists so the app doesn't need the user's password on every submission to unwrap their wallet key.

Before the first audit, send a small amount of StudioNet GEN to `GENLAYER_RELAY_ADDRESS`.

## Product flow

1. Sign up · embedded wallet auto-provisioned · save 24-word recovery phrase.
2. Onboarding · open first analytics workspace.
3. **Open Claim Review** (`/audits/new`) — state the claim, attach metric basis, define reporting context, upload evidence (CSV / JSON / PDF / image, max 4, with size limits), declare 3 candidate interpretations.
4. **Request GenLayer judgment** — server action computes evidence digest, calls `submit_audit(audit_id, packet_json, evidence_digest)` on the contract, logs the tx hash.
5. **Official Audit Judgment** (`/audits/[id]`) — click **Refresh from GenLayer** to read the contract; once validators reach consensus, the verdict + reasoning + business risk + unsupported assumptions + interpretation pick mirror into Supabase and the doc switches to the final judgment.
6. **Decision Memos** (`/memos`) — executive-ready summaries derived from issued judgments.

## Deploy

Frontend: Vercel. Set every env var above in the Vercel project. Contract: GenLayer Studio (already deployed).
