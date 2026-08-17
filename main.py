from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from conversations import router as conversation_router
from chat import router as chat_router


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
    allow_origins=[
        "https://genessis-frontend-azcq.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================================
# ROUTES
# =========================================================

app.include_router(
    conversation_router
)

app.include_router(
    chat_router
)


# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root():

    return {
        "message": "Genesis API is running"
    }
