from fastapi import APIRouter, HTTPException

from database import supabase


router = APIRouter()


# =========================================================
# CREATE NEW CONVERSATION
# =========================================================

@router.post("/conversations")
def create_conversation():

    response = (
        supabase
        .table("conversations")
        .insert({
            "title": "New Chat"
        })
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=500,
            detail="Failed to create conversation"
        )

    return response.data[0]


# =========================================================
# GET ALL CONVERSATIONS
# =========================================================

@router.get("/conversations")
def get_conversations():

    response = (
        supabase
        .table("conversations")
        .select("*")
        .order(
            "updated_at",
            desc=True
        )
        .execute()
    )

    return response.data


# =========================================================
# GET MESSAGES FOR ONE CONVERSATION
# =========================================================

@router.get(
    "/conversations/{conversation_id}"
)
def get_conversation(
    conversation_id: str
):

    response = (
        supabase
        .table("messages")
        .select("*")
        .eq(
            "conversation_id",
            conversation_id
        )
        .order("created_at")
        .execute()
    )

    return response.data


# =========================================================
# DELETE CONVERSATION
# =========================================================

@router.delete(
    "/conversations/{conversation_id}"
)
def delete_conversation(
    conversation_id: str
):

    response = (
        supabase
        .table("conversations")
        .delete()
        .eq(
            "id",
            conversation_id
        )
        .execute()
    )

    return {
        "message": "Conversation deleted"
    }