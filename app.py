import json
import os
from typing import Any

import requests
import streamlit as st
from google import genai
from google.genai import types
from streamlit.errors import StreamlitSecretNotFoundError

PRODUCTS_API_URL = "https://dummyjson.com/products"
DEFAULT_MODEL = "gemini-3.1-flash-lite-preview"
PRODUCT_PAGE_SIZE = 100

SYSTEM_INSTRUCTION = """You are a professional AI product assistant.
You answer only from the product catalog provided in the context.
Do not use outside knowledge.
Do not invent products, prices, stock, ratings, or features.
If the catalog does not contain the answer, say you could not find it in the provided product data.
Keep answers concise, helpful, and professional.
When asked about products, cite the product titles you relied on.
"""

st.set_page_config(
    page_title="AI Product Chatbot",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;700&display=swap');

    :root {
        color-scheme: dark;
    }

    .stApp {
        background:
            radial-gradient(circle at 12% 18%, rgba(255, 196, 77, 0.16), transparent 22%),
            radial-gradient(circle at 88% 14%, rgba(95, 188, 255, 0.14), transparent 20%),
            radial-gradient(circle at 80% 92%, rgba(138, 92, 255, 0.10), transparent 24%),
            linear-gradient(180deg, #07111d 0%, #0a1320 44%, #080d14 100%);
        color: #f3f4f6;
    }

    .main .block-container {
        padding-top: 2.35rem;
        padding-bottom: 2.8rem;
        max-width: 1280px;
    }

    h1, h2, h3, h4, p, label, span, div {
        font-family: Inter, "Segoe UI", sans-serif;
    }

    .hero-shell {
        border: 1px solid rgba(255, 255, 255, 0.08);
        background: linear-gradient(135deg, rgba(12, 18, 30, 0.92), rgba(8, 13, 22, 0.76));
        backdrop-filter: blur(18px);
        border-radius: 28px;
        padding: 1.65rem 1.7rem;
        box-shadow: 0 28px 72px rgba(0, 0, 0, 0.30);
    }

    .eyebrow {
        display: inline-flex;
        align-items: center;
        gap: 0.45rem;
        border: 1px solid rgba(255, 255, 255, 0.10);
        background: rgba(255, 255, 255, 0.04);
        border-radius: 999px;
        padding: 0.35rem 0.8rem;
        color: rgba(243, 244, 246, 0.88);
        font-size: 0.76rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 1.15rem;
    }

    .hero-grid {
        display: grid;
        grid-template-columns: 1.6fr 0.95fr;
        gap: 1.35rem;
        align-items: stretch;
    }

    .hero-title {
        font-family: "Space Grotesk", Inter, sans-serif;
        font-size: clamp(2.1rem, 4vw, 3.3rem);
        font-weight: 700;
        letter-spacing: -0.05em;
        line-height: 0.98;
        margin: 0 0 0.9rem 0;
    }

    .hero-subtitle {
        color: rgba(243, 244, 246, 0.78);
        margin: 0;
        font-size: 1rem;
        line-height: 1.65;
        max-width: 54rem;
    }

    .hero-panel {
        border: 1px solid rgba(255, 255, 255, 0.08);
        background: rgba(255, 255, 255, 0.03);
        border-radius: 22px;
        padding: 1.15rem 1.15rem;
    }

    .hero-panel-title {
        color: #ffffff;
        font-weight: 700;
        font-size: 0.95rem;
        margin-bottom: 0.4rem;
    }

    .hero-panel-copy {
        color: rgba(243, 244, 246, 0.74);
        font-size: 0.92rem;
        line-height: 1.6;
        margin: 0;
    }

    .metric-card {
        border: 1px solid rgba(255, 255, 255, 0.08);
        background: linear-gradient(180deg, rgba(14, 21, 33, 0.92), rgba(9, 14, 24, 0.92));
        border-radius: 18px;
        padding: 1.1rem 1.15rem;
        height: 100%;
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04);
    }

    .metric-label {
        color: rgba(243, 244, 246, 0.66);
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.10em;
        margin-bottom: 0.45rem;
    }

    .metric-value {
        color: #ffffff;
        font-size: 1.35rem;
        font-weight: 800;
        letter-spacing: -0.03em;
    }

    .metric-detail {
        color: rgba(243, 244, 246, 0.68);
        font-size: 0.86rem;
        margin-top: 0.3rem;
    }

    .section-title {
        font-family: "Space Grotesk", Inter, sans-serif;
        font-size: 1.15rem;
        font-weight: 700;
        letter-spacing: -0.03em;
        margin: 1.1rem 0 0.85rem 0;
    }

    .stChatMessage {
        border-radius: 18px;
    }

    .stChatMessage + .stChatMessage {
        margin-top: 0.65rem;
    }

    .stChatMessage[data-testid="stChatMessage"] {
        border: 1px solid rgba(255, 255, 255, 0.06);
        background: rgba(255, 255, 255, 0.02);
        box-shadow: 0 16px 40px rgba(0, 0, 0, 0.16);
    }

    .stChatMessage [data-testid="stMarkdownContainer"] p {
        line-height: 1.65;
    }

    .stTextInput input {
        background-color: rgba(255, 255, 255, 0.04) !important;
        color: white !important;
        border-radius: 14px !important;
        border: 1px solid rgba(255, 255, 255, 0.10) !important;
    }

    .stButton button {
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.10);
        background: linear-gradient(135deg, #d4a64a, #f0c36f);
        color: #111827;
        font-weight: 700;
        padding: 0.62rem 1rem;
    }

    .stSidebar {
        background: linear-gradient(180deg, rgba(7, 11, 18, 0.98), rgba(12, 18, 28, 0.98));
        border-right: 1px solid rgba(255, 255, 255, 0.06);
    }

    .stSidebar .block-container {
        padding-top: 1.6rem;
        padding-bottom: 1.6rem;
    }

    .sidebar-card {
        border: 1px solid rgba(255, 255, 255, 0.08);
        background: rgba(255, 255, 255, 0.03);
        border-radius: 18px;
        padding: 1.05rem;
        margin-top: 0.85rem;
    }

    .sidebar-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        border-radius: 999px;
        padding: 0.25rem 0.7rem;
        background: rgba(212, 166, 74, 0.14);
        color: #f7d48a;
        font-size: 0.76rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    .sidebar-note {
        color: rgba(243, 244, 246, 0.76);
        font-size: 0.9rem;
        line-height: 1.6;
        margin: 0.8rem 0 0 0;
    }

    .chat-section-gap {
        margin-top: 1.3rem;
    }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def load_gemini_api_key() -> str:
    api_key = os.getenv("GEMINI_API_KEY", "")
    if api_key:
        return api_key

    try:
        return str(st.secrets.get("GEMINI_API_KEY", ""))
    except StreamlitSecretNotFoundError:
        return ""


@st.cache_data(show_spinner=False)
def fetch_products() -> list[dict[str, Any]]:
    products: list[dict[str, Any]] = []
    skip = 0

    while True:
        response = requests.get(
            PRODUCTS_API_URL,
            params={"limit": PRODUCT_PAGE_SIZE, "skip": skip},
            timeout=30,
        )
        response.raise_for_status()
        payload = response.json()
        page_products = payload.get("products", [])

        if not page_products:
            break

        products.extend(page_products)

        total = payload.get("total", len(products))
        skip += len(page_products)
        if skip >= total:
            break

    return products


@st.cache_data(show_spinner=False)
def build_catalog_context() -> str:
    products = fetch_products()
    catalog = []
    for product in products:
        catalog.append(
            {
                "id": product.get("id"),
                "title": product.get("title"),
                "description": product.get("description"),
                "category": product.get("category"),
                "brand": product.get("brand"),
                "price": product.get("price"),
                "rating": product.get("rating"),
                "stock": product.get("stock"),
                "tags": product.get("tags", []),
            }
        )
    return json.dumps(catalog, ensure_ascii=False, indent=2)


@st.cache_data(show_spinner=False)
def build_catalog_summary() -> dict[str, Any]:
    products = fetch_products()
    categories = sorted({str(product.get("category", "Unknown")).title() for product in products if product.get("category")})
    brands = sorted({str(product.get("brand", "Unknown")).title() for product in products if product.get("brand")})
    prices = [float(product.get("price", 0) or 0) for product in products if product.get("price") is not None]
    ratings = [float(product.get("rating", 0) or 0) for product in products if product.get("rating") is not None]

    return {
        "total_products": len(products),
        "categories": len(categories),
        "brands": len(brands),
        "min_price": min(prices) if prices else 0,
        "max_price": max(prices) if prices else 0,
        "average_rating": (sum(ratings) / len(ratings)) if ratings else 0,
        "top_category": categories[0] if categories else "Unknown",
    }


@st.cache_resource(show_spinner=False)
def get_client(api_key: str) -> genai.Client:
    return genai.Client(api_key=api_key)


def build_prompt(chat_history: list[dict[str, str]], user_message: str, catalog_context: str) -> str:
    conversation_lines = []
    for item in chat_history[-12:]:
        speaker = "User" if item["role"] == "user" else "Assistant"
        conversation_lines.append(f"{speaker}: {item['content']}")

    conversation_block = "\n".join(conversation_lines) if conversation_lines else "No prior conversation."

    summary = build_catalog_summary()

    return f"""{SYSTEM_INSTRUCTION}

Catalog summary:
- Total products: {summary['total_products']}
- Categories: {summary['categories']}
- Brands: {summary['brands']}
- Average rating: {summary['average_rating']:.1f}/5
- Price range: ${summary['min_price']:,.0f} to ${summary['max_price']:,.0f}
- Top category: {summary['top_category']}

Product catalog JSON:
{catalog_context}

Conversation so far:
{conversation_block}

User question:
{user_message}

Write the next assistant reply based only on the catalog above.
"""


st.markdown(
    """
    <div class="hero-shell">
        <div class="eyebrow">Live product intelligence</div>
        <div class="hero-grid">
            <div>
                <div class="hero-title">AI Product Chatbot</div>
                <p class="hero-subtitle">
                    Ask natural-language product questions and get answers grounded only in the live
                    DummyJSON catalog. The assistant stays model-led and does not use local response rules.
                </p>
            </div>
            <div class="hero-panel">
                <div class="hero-panel-title">How it works</div>
                <p class="hero-panel-copy">
                    The app loads the full catalog, packages it into the model prompt, and lets Gemini
                    write the response directly from that data.
                </p>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

products = []
products_error = None
with st.spinner("Loading catalog from product API..."):
    try:
        products = fetch_products()
    except Exception as exc:  # pragma: no cover - surfaced in UI
        products_error = str(exc)

catalog_stats = build_catalog_summary()
st.markdown('<div class="section-title">Catalog Snapshot</div>', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4, gap="medium")
with col1:
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">Catalog status</div><div class="metric-value">{"Ready" if products else "Unavailable"}</div><div class="metric-detail">DummyJSON source connected</div></div>',
        unsafe_allow_html=True,
    )
with col2:
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">Products loaded</div><div class="metric-value">{catalog_stats["total_products"]}</div><div class="metric-detail">Full paginated catalog</div></div>',
        unsafe_allow_html=True,
    )
with col3:
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">Categories</div><div class="metric-value">{catalog_stats["categories"]}</div><div class="metric-detail">Top category: {catalog_stats["top_category"]}</div></div>',
        unsafe_allow_html=True,
    )
with col4:
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">Average rating</div><div class="metric-value">{catalog_stats["average_rating"]:.1f}/5</div><div class="metric-detail">Price range ${catalog_stats["min_price"]:,.0f} - ${catalog_stats["max_price"]:,.0f}</div></div>',
        unsafe_allow_html=True,
    )

if products_error:
    st.error(f"Could not load product data: {products_error}")
    st.stop()

st.markdown('<div class="chat-section-gap"></div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<div class="sidebar-pill">Connection</div>', unsafe_allow_html=True)
    api_key = st.text_input(
        "Gemini API key",
        value=load_gemini_api_key(),
        type="password",
        help="Set GEMINI_API_KEY in the environment or Streamlit secrets, or enter it here.",
    )
    model_name = st.text_input("Model name", value=DEFAULT_MODEL)
    st.markdown(
        f"""
        <div class="sidebar-card">
            <div class="hero-panel-title">Catalog source</div>
            <p class="sidebar-note">
                Answers are generated only from the live DummyJSON product catalog. The current model
                target is <strong>{DEFAULT_MODEL}</strong>.
                <br><br>
                Loaded products: <strong>{catalog_stats['total_products']}</strong>
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("The assistant does not use local product rules for answers.")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": f"Ask me anything about the product catalog. I have access to {catalog_stats['total_products']} products from the API.",
        }
    ]

catalog_context = build_catalog_context()
client = get_client(api_key) if api_key else None

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_prompt = st.chat_input("Ask about products in the catalog...")

if user_prompt:
    if not api_key:
        st.error("Add your Gemini API key in the sidebar before chatting.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        with st.spinner("Gemini is analyzing the catalog..."):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=build_prompt(st.session_state.messages[:-1], user_prompt, catalog_context),
                    config=types.GenerateContentConfig(
                    ),
                )
                answer = response.text or "I could not generate a response from the catalog."
            except Exception as exc:  # pragma: no cover - surfaced in UI
                answer = f"Model request failed: {exc}"

        response_placeholder.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})
