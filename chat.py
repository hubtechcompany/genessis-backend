from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from database import supabase
from rag import ask_question


router = APIRouter()


class ChatRequest(BaseModel):
    conversation_id: str
    question: str


@router.post("/chat")
def chat(request: ChatRequest):

    # ------------------------------------------------
    # 1. Check conversation
    # ------------------------------------------------

    conversation = (
        supabase
        .table("conversations")
        .select("*")
        .eq("id", request.conversation_id)
        .single()
        .execute()
    )

    if not conversation.data:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

    # ------------------------------------------------
    # 2. Save user message
    # ------------------------------------------------

    supabase.table("messages").insert({
        "conversation_id": request.conversation_id,
        "role": "user",
        "content": request.question
    }).execute()

    # ------------------------------------------------
    # 3. Get previous conversation messages
    # ------------------------------------------------

    history_response = (
        supabase
        .table("messages")
        .select("role, content")
        .eq(
            "conversation_id",
            request.conversation_id
        )
        .order("created_at")
        .execute()
    )

    history = history_response.data or []

    # ------------------------------------------------
    # 4. RAG
    # ------------------------------------------------

    result = ask_question(
        request.question,
        history=history
    )

    answer = result["answer"]

    # ------------------------------------------------
    # 5. Save assistant message
    # ------------------------------------------------

    supabase.table("messages").insert({
        "conversation_id": request.conversation_id,
        "role": "assistant",
        "content": answer
    }).execute()

    # ------------------------------------------------
    # 6. Update conversation
    # ------------------------------------------------

    supabase.table("conversations").update({
        "updated_at": "now()"
    }).eq(
        "id",
        request.conversation_id
    ).execute()

    return {
        "conversation_id": request.conversation_id,
        "answer": answer,
        "sources": result["sources"]
    }