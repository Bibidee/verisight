-- One-off admin promotion. Run from the Supabase SQL editor when you want
-- a specific account to see /admin. Replace the email and run.
--
-- Example:
--   update public.profiles
--     set role = 'admin'
--     where email = 'you@example.com';

update public.profiles
  set role = 'admin'
  where email = 'replace-me@example.com';
