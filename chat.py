from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from uuid import UUID

from database import supabase
from rag import ask_question


router = APIRouter()
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from uuid import UUID

from database import supabase
from rag import ask_question


router = APIRouter()


# =========================================================
# REQUEST MODEL
# =========================================================

class ChatRequest(BaseModel):
    conversation_id: str
    question: str


# =========================================================
# POST /chat
# =========================================================

@router.post("/chat")
def chat(request: ChatRequest):

    # -----------------------------------------------------
    # Validate question
    # -----------------------------------------------------

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    # -----------------------------------------------------
    # Validate UUID
    # -----------------------------------------------------

    try:

        conversation_id = UUID(
            request.conversation_id
        )

    except (ValueError, AttributeError):

        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid conversation_id. "
                "Please create a conversation first."
            )
        )

    conversation_id = str(conversation_id)

    # -----------------------------------------------------
    # Check conversation
    # -----------------------------------------------------

    try:

        conversation_response = (
            supabase
            .table("conversations")
            .select("id")
            .eq("id", conversation_id)
            .maybe_single()
            .execute()
        )

    except Exception as e:

        print(
            "CONVERSATION LOOKUP ERROR:",
            repr(e)
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to check conversation."
        )

    if not conversation_response.data:

        raise HTTPException(
            status_code=404,
            detail="Conversation not found."
        )

    # -----------------------------------------------------
    # Save user message
    # -----------------------------------------------------

    try:

        supabase.table("messages").insert({
            "conversation_id": conversation_id,
            "role": "user",
            "content": question
        }).execute()

    except Exception as e:

        print(
            "USER MESSAGE ERROR:",
            repr(e)
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to save user message."
        )

    # -----------------------------------------------------
    # RAG
    # -----------------------------------------------------

    try:

        result = ask_question(question)

        answer = result.get(
            "answer",
            "I could not generate an answer."
        )

        sources = result.get(
            "sources",
            []
        )

    except Exception as e:

        print(
            "RAG ERROR:",
            repr(e)
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to generate AI answer."
        )

    # -----------------------------------------------------
    # Save assistant message
    # -----------------------------------------------------

    try:

        supabase.table("messages").insert({
            "conversation_id": conversation_id,
            "role": "assistant",
            "content": answer
        }).execute()

    except Exception as e:

        print(
            "ASSISTANT MESSAGE ERROR:",
            repr(e)
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to save assistant message."
        )

    # -----------------------------------------------------
    # Update conversation timestamp
    # -----------------------------------------------------

    try:

        supabase.table("conversations").update({
            "updated_at": "now()"
        }).eq(
            "id",
            conversation_id
        ).execute()

    except Exception as e:

        print(
            "CONVERSATION UPDATE ERROR:",
            repr(e)
        )

    # -----------------------------------------------------
    # Return
    # -----------------------------------------------------

    return {
        "conversation_id": conversation_id,
        "answer": answer,
        "sources": sources
    }

# =========================================================
# REQUEST MODEL
# =========================================================

class ChatRequest(BaseModel):
    conversation_id: str
    question: str


# =========================================================
# CHAT
# =========================================================

@router.post("/chat")
def chat(request: ChatRequest):

    # -----------------------------------------------------
    # Validate conversation UUID
    # -----------------------------------------------------

    try:
        conversation_id = UUID(request.conversation_id)

    except ValueError:

        raise HTTPException(
            status_code=400,
            detail="Invalid conversation_id. Expected a valid UUID."
        )


    # -----------------------------------------------------
    # Check conversation exists
    # -----------------------------------------------------

    conversation = (
        supabase
        .table("conversations")
        .select("id")
        .eq("id", str(conversation_id))
        .maybe_single()
        .execute()
    )


    if not conversation.data:

        raise HTTPException(
            status_code=404,
            detail="Conversation not found."
        )


    # -----------------------------------------------------
    # Save user message
    # -----------------------------------------------------

    supabase.table("messages").insert({

        "conversation_id": str(conversation_id),

        "role": "user",

        "content": request.question

    }).execute()


    # -----------------------------------------------------
    # RAG
    # -----------------------------------------------------

    try:

        result = ask_question(request.question)

    except Exception as e:

        print("RAG ERROR:", repr(e))

        raise HTTPException(
            status_code=500,
            detail="Failed to generate AI answer."
        )


    answer = result["answer"]

    sources = result.get("sources", [])


    # -----------------------------------------------------
    # Save assistant message
    # -----------------------------------------------------

    supabase.table("messages").insert({

        "conversation_id": str(conversation_id),

        "role": "assistant",

        "content": answer

    }).execute()


    # -----------------------------------------------------
    # Update conversation
    # -----------------------------------------------------

    supabase.table("conversations").update({

        "updated_at": "now()"

    }).eq(
        "id",
        str(conversation_id)
    ).execute()


    # -----------------------------------------------------
    # Return
    # -----------------------------------------------------

    return {

        "conversation_id": str(conversation_id),

        "answer": answer,

        "sources": sources

    }
