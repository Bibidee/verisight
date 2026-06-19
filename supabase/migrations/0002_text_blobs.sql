-- Convert bytea columns holding encrypted material to text (base64) for
-- straightforward JSON transport via PostgREST.

alter table public.wallets
  alter column encrypted_private_key type text using encode(encrypted_private_key, 'base64');

alter table public.wallet_key_wraps
  alter column encrypted_wallet_key type text using encode(encrypted_wallet_key, 'base64'),
  alter column salt type text using encode(salt, 'base64');
