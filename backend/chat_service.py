import os

from dotenv import load_dotenv
from openai import OpenAI
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

load_dotenv()

client = OpenAI( 
    api_key=os.environ["OPENAI_API_KEY"],
) 

MODEL = "gpt-5.6-luna"

# --- Knowledge base -----------------------------------------------------

KB_ENTRIES = [
    "Q: What is Artha Support Bot?\nA: A demo AI assistant that answers questions about our (fictional) SaaS product, Artha.",
    "Q: What are your business hours?\nA: Support is available Monday-Friday, 9am-6pm IST.",
    "Q: How do I reset my password?\nA: Go to Settings > Account > Reset Password. A reset link is emailed within a few minutes.",
    "Q: Do you offer a free trial?\nA: Yes, a 14-day free trial with no credit card required.",
    "Q: How do I cancel my subscription?\nA: Settings > Billing > Cancel Subscription. You keep access until the end of the billing period.",
    "Q: Is there an API available?\nA: Yes, a REST API is available on paid plans. Docs are at /docs once the API key is issued.",
]

# --- Retrieval ------------------------------------------------------------

_vectorizer = TfidfVectorizer(stop_words="english")
_kb_matrix = _vectorizer.fit_transform(KB_ENTRIES)


def retrieve_relevant_entries(query: str, top_k: int = 3) -> list[str]:
    query_vec = _vectorizer.transform([query])
    scores = cosine_similarity(query_vec, _kb_matrix)[0]
    ranked_indices = scores.argsort()[::-1]
    top_indices = [i for i in ranked_indices[:top_k] if scores[i] > 0]
    if not top_indices:
        return KB_ENTRIES  # fall back to full KB if nothing scores above 0
    return [KB_ENTRIES[i] for i in top_indices]


def build_system_prompt(context_entries: list[str]) -> str:
    context = "\n\n".join(context_entries)
    return f"""You are a helpful support assistant. Answer user questions using ONLY \
the knowledge base excerpts below. If the answer isn't in them, say you don't \
have that information and suggest contacting human support.

KNOWLEDGE BASE:
{context}
"""


def get_chat_reply(user_message: str) -> str:
    relevant_entries = retrieve_relevant_entries(user_message)
    system_prompt = build_system_prompt(relevant_entries)

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        max_completion_tokens=400,
    )
    return response.choices[0].message.content