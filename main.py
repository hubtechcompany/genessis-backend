from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from conversations import router as conversation_router
from chat import router as chat_router
from database import supabase


app = FastAPI(
    title="Genesis API",
    version="1.0.0"
)


# =========================================================
# CORS
# =========================================================

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
# =========================================================
# ROUTES
# =========================================================

app.include_router(conversation_router)
app.include_router(chat_router)

# =========================================================
# ROUTES
# =========================================================

app.include_router(
    conversation_router
)

app.include_router(
    chat_router
)

# ============================================================
# DATABASE TEST
# ============================================================

@app.get("/test-db")
def test_database():

    try:

        response = (
            supabase
            .table("conversations")
            .select("*")
            .limit(5)
            .execute()
        )

        return {
            "success": True,
            "data": response.data
        }

    except Exception as e:

        print("DATABASE ERROR:", repr(e))

        return {
            "success": False,
            "error": str(e)
        }
# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root():

    return {
        "message": "Genesis API is running"
    }
