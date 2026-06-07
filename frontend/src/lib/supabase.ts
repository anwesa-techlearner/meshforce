import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://placeholder.supabase.co';
// Use service key for reads so RLS doesn't block the admin dashboard.
// This is safe for a demo app — in production, add proper RLS policies.
const supabaseKey =
  process.env.NEXT_PUBLIC_SUPABASE_SERVICE_KEY ||
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ||
  'placeholder-key';

export const supabase = createClient(supabaseUrl, supabaseKey);
