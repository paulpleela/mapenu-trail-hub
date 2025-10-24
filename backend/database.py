"""
Database client initialization for Supabase.
"""
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY, SUPABASE_SERVICE_ROLE_KEY

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Optional service-role client for server-side writes that must bypass RLS
supabase_service = None
if SUPABASE_SERVICE_ROLE_KEY:
    try:
        supabase_service: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        print("✅ Supabase service-role client initialized")
    except Exception as e:
        print(f"⚠️  Could not initialize supabase service client: {e}")

print("✅ Supabase client initialized")
