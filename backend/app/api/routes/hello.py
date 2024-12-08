from fastapi import APIRouter
from supabase import create_client
from app.core.config import settings

router = APIRouter(tags=["hello"])

@router.get("/hello")
async def hello_world() -> dict[str, str | int]:
    # Initialize Supabase client
    supabase = create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_KEY
    )
    
    # Example query to count all rows in a 'messages' table
    result = supabase.table('messages').select("*", count='exact').execute()
    
    return {
        "message": "Hello from Supabase!",
        "message_count": result.count
    } 