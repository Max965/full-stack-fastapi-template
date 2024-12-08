from supabase import create_client
from app.core.config import settings

def test_supabase_connection():
    """Simple test to verify Supabase connection"""
    try:
        # Initialize Supabase client
        supabase = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY
        )
        
        # Query to list all tables in the public schema
        result = supabase.table("todos").select("*").execute()

        print("\n=== Supabase Connection Test ===")
        print(f"Connection successful!")
        print(f"Available tables: {result}")
        
        return True
        
    except Exception as e:
        print("\n=== Supabase Connection Error ===")
        print(f"Error: {str(e)}")
        raise e

if __name__ == "__main__":
    test_supabase_connection()