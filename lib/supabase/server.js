import 'server-only'
import { createClient } from '@supabase/supabase-js'

// Server-only Supabase admin client. Uses the SECRET key which bypasses RLS.
// Because this module is server-only, the secret key is never shipped to the browser.
export function supabaseAdmin() {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL
  const key = process.env.SUPABASE_SECRET_KEY
  if (!url) throw new Error('Missing NEXT_PUBLIC_SUPABASE_URL')
  if (!key) throw new Error('Missing SUPABASE_SECRET_KEY')
  return createClient(url, key, {
    auth: { autoRefreshToken: false, persistSession: false },
  })
}
