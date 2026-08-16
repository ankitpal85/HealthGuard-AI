"""Quick Supabase connection test script."""
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv
load_dotenv()

from database.supabase_manager import get_supabase_client, is_supabase_active

def main():
    print("=== Supabase Cloud Connection Test ===")
    url = os.getenv("SUPABASE_URL", "NOT SET")
    key = os.getenv("SUPABASE_KEY", "")
    print(f"SUPABASE_URL : {url}")
    print(f"SUPABASE_KEY : {'SET [OK]' if key else 'NOT SET [MISSING]'}")

    client = get_supabase_client()

    if not client:
        print("Supabase Client: NOT INITIALIZED")
        print("Check your SUPABASE_URL and SUPABASE_KEY in .env file.")
        sys.exit(1)

    print("Supabase Client: INITIALIZED [OK]")

    tables_to_check = [
        "users", "medications", "medication_logs", "health_metrics",
        "health_goals", "nutrition_logs", "chat_history",
        "indian_medications", "ayurvedic_herbs", "doctor_appointments",
        "insurance_policies", "family_members", "caregiver_contacts", "health_alerts_log"
    ]

    all_ok = True
    for table in tables_to_check:
        try:
            res = client.table(table).select("id").limit(1).execute()
            print(f"  {table}: EXISTS [OK] (rows in DB: {len(res.data)})")
        except Exception as e:
            print(f"  {table}: ERROR -- {e}")
            all_ok = False

    if all_ok:
        print("\n=== ALL 14 SUPABASE TABLES VERIFIED SUCCESSFULLY! ===")
    else:
        print("\n=== SOME TABLES HAD ERRORS -- Re-run the DDL SQL in Supabase ===")

if __name__ == "__main__":
    main()

