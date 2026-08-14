import os

from dotenv import load_dotenv

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq

from database import supabase


load_dotenv()


# =========================================================
# EMBEDDING MODEL
# =========================================================

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


# =========================================================
# GROQ
# =========================================================

llm = ChatGroq(
    model=os.getenv("GROQ_MODEL"),
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.2
)


# =========================================================
# VECTOR SEARCH
# =========================================================

def search_documents(
    question: str,
    limit: int = 5
):

    question_embedding = (
        embeddings.embed_query(question)
    )

    response = supabase.rpc(
        "match_documents",
        {
            "query_embedding": question_embedding,
            "match_count": limit
        }
    ).execute()

    return response.data or []


# =========================================================
# GENERATE ANSWER
# =========================================================

def ask_question(
    question: str,
    history=None
):

    if history is None:
        history = []


    # -----------------------------------------------------
    # SEARCH BOOKS
    # -----------------------------------------------------

    documents = search_documents(
        question,
        limit=5
    )


    if not documents:

        return {
            "answer":
                "I could not find relevant information "
                "in the provided books.",

            "sources": []
        }


    # -----------------------------------------------------
    # CONVERSATION HISTORY
    # -----------------------------------------------------

    history_text = ""

    for message in history[-10:]:

        history_text += (
            f"{message['role'].upper()}: "
            f"{message['content']}\n\n"
        )


    # -----------------------------------------------------
    # BOOK CONTEXT
    # -----------------------------------------------------

    context_parts = []


    for doc in documents:

        context_parts.append(
            f"""
Book: {doc.get('filename', '')}

Chapter: {doc.get('chapter', '')}

Content:

{doc.get('content', '')}
"""
        )


    context = "\n\n".join(
        context_parts
    )


    # -----------------------------------------------------
    # PROMPT
    # -----------------------------------------------------

    prompt = f"""
You are Genesis, a book research assistant.

Answer the user's question using ONLY the
provided book context.

Rules:

1. Use the book context as the primary source.
2. Do not invent information.
3. If the answer cannot be found in the
   provided books, say so.
4. Use conversation history to understand
   references such as:
   "it", "this", "that", "the first one", etc.
5. Give a clear and useful answer.
6. Do not claim information that is not
   supported by the book context.

========================================
CONVERSATION HISTORY
========================================

{history_text}

========================================
BOOK CONTEXT
========================================

{context}

========================================
CURRENT QUESTION
========================================

{question}

========================================
ANSWER
========================================
"""


    # -----------------------------------------------------
    # CALL GROQ
    # -----------------------------------------------------

    response = llm.invoke(prompt)

    answer = response.content


    # -----------------------------------------------------
    # SOURCES
    # -----------------------------------------------------

    sources = []

    for doc in documents:

        sources.append({
            "filename":
                doc.get("filename"),

            "chapter":
                doc.get("chapter"),

            "chunk_number":
                doc.get("chunk_number"),

            "similarity":
                doc.get("similarity")
        })


    return {
        "answer": answer,
        "sources": sources
    }