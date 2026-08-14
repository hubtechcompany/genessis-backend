from langchain_groq import ChatGroq
from config import GROQ_API_KEY, GROQ_MODEL


llm = ChatGroq(
    model=GROQ_MODEL,
    api_key=GROQ_API_KEY,
    temperature=0
)


response = llm.invoke(
    "Explain machine learning in simple terms."
)

print(response.content)