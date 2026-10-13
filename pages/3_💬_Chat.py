"""
pages/3_💬_Chat.py — Full conversational AI chatbot
Powered by Groq Llama3 with a BIS + construction expert system prompt.
Supports multi-turn conversation, starter questions, streaming-style UX.
"""
import streamlit as st
import os, sys
from groq import Groq
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv()

st.set_page_config(page_title="Chat · BIS AI Assistant", page_icon="💬", layout="wide")

# ── CSS ──
def load_css():
    css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "styles", "main.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# Extra chat-specific styles injected inline
st.markdown("""
<style>
/* ── Full-height chat layout ── */
.chat-wrapper {
    display: flex;
    flex-direction: column;
    gap: 16px;
    max-width: 820px;
    margin: 0 auto;
    padding-bottom: 20px;
}

/* ── User bubble ── */
.msg-user {
    display: flex;
    justify-content: flex-end;
    align-items: flex-end;
    gap: 10px;
    animation: fadeUp 0.25s ease;
}
.msg-user .bubble {
    background: linear-gradient(135deg, #7A4E0A 0%, #C87C18 100%);
    color: #FDE8A0;
    padding: 13px 18px;
    border-radius: 18px 18px 4px 18px;
    max-width: 72%;
    font-size: 0.91rem;
    line-height: 1.6;
    box-shadow: 0 4px 16px rgba(200,120,24,0.25);
}
.msg-user .avatar {
    width: 34px; height: 34px;
    border-radius: 50%;
    background: linear-gradient(135deg, #7A4E0A, #C87C18);
    display: flex; align-items: center; justify-content: center;
    font-size: 1rem;
    flex-shrink: 0;
    box-shadow: 0 2px 8px rgba(200,120,24,0.3);
}

/* ── Bot bubble ── */
.msg-bot {
    display: flex;
    justify-content: flex-start;
    align-items: flex-end;
    gap: 10px;
    animation: fadeUp 0.25s ease;
}
.msg-bot .bubble {
    background: linear-gradient(145deg, #071420 0%, #050E18 100%);
    border: 1px solid rgba(26,154,80,0.22);
    border-left: 3px solid #1A9A50;
    color: #C0D0D8;
    padding: 14px 18px;
    border-radius: 18px 18px 18px 4px;
    max-width: 78%;
    font-size: 0.91rem;
    line-height: 1.75;
    box-shadow: 0 4px 16px rgba(0,0,0,0.4);
}
.msg-bot .bubble strong { color: #E8C56A; }
.msg-bot .bubble code {
    background: rgba(255,255,255,0.06);
    border-radius: 4px;
    padding: 1px 6px;
    font-size: 0.82rem;
    color: #7AB8D0;
}
.msg-bot .bubble ul, .msg-bot .bubble ol {
    padding-left: 18px;
    margin: 8px 0;
}
.msg-bot .bubble li { margin: 4px 0; }
.msg-bot .bubble hr { margin: 10px 0; opacity: 0.15; }
.msg-bot .avatar {
    width: 34px; height: 34px;
    border-radius: 50%;
    background: linear-gradient(135deg, #0D5C2C, #1A9A50);
    display: flex; align-items: center; justify-content: center;
    font-size: 1rem;
    flex-shrink: 0;
    box-shadow: 0 2px 8px rgba(26,154,80,0.3);
}

/* ── Thinking indicator ── */
.typing-dot {
    display: inline-block;
    width: 7px; height: 7px;
    margin: 0 2px;
    border-radius: 50%;
    background: #1A9A50;
    animation: typingBounce 1.2s infinite ease-in-out;
}
.typing-dot:nth-child(2) { animation-delay: 0.2s; }
.typing-dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes typingBounce {
    0%, 80%, 100% { transform: translateY(0); opacity: 0.4; }
    40% { transform: translateY(-6px); opacity: 1; }
}

@keyframes fadeUp {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* ── Input area ── */
.chat-input-bar {
    position: sticky;
    bottom: 0;
    background: linear-gradient(0deg, #04090F 70%, transparent 100%);
    padding: 16px 0 8px;
    z-index: 100;
}

/* ── Starter buttons ── */
.starter-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin: 0 auto 28px;
    max-width: 820px;
}
.starter-card {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(210,140,40,0.18);
    border-radius: 10px;
    padding: 13px 16px;
    cursor: pointer;
    transition: all 0.2s ease;
    text-align: left;
}
.starter-card:hover {
    background: rgba(210,140,40,0.07);
    border-color: rgba(210,140,40,0.4);
    transform: translateY(-2px);
}
.starter-card .icon { font-size: 1.3rem; margin-bottom: 6px; display: block; }
.starter-card .text { font-size: 0.82rem; color: #7A9AAA; line-height: 1.45; }
</style>
""", unsafe_allow_html=True)

# ── System Prompt ──
SYSTEM_PROMPT = """You are an expert assistant specializing in BIS (Bureau of Indian Standards) and general engineering and construction topics in India. You are designed to help beginners and non-technical people — including students, homeowners, contractors, and small business owners.

You can answer any type of question, including but not limited to:
- "What is IS 2185?"
- "How do I build a strong concrete wall?"
- "What materials should I use for my roof?"
- "What is the difference between M20 and M25 concrete?"
- "Is this product BIS certified?"
- "What are the steps to construct a foundation?"
- "Why is my cement cracking?"
- "What does compressive strength mean?"

PERSONALITY & TONE:
- Friendly, patient, and encouraging — never condescending
- Write like you are explaining to a curious, intelligent person who is new to the topic
- Use simple words. If you must use a technical term, immediately explain it in brackets (e.g. "compressive strength (how much weight it can hold before breaking)")
- Be conversational, not robotic

HOW TO ANSWER EVERY QUESTION:

For BIS standard questions:
1. Plain-English summary of what the standard is about (1-2 sentences)
2. Why it exists — what problem it solves or who it protects
3. Key requirements in simple bullet points with real-world analogies
4. Relevant IS number(s) with full official names
5. End with "In practice, this means..." with a practical takeaway

For general engineering/construction questions:
1. Answer the question directly and clearly first
2. Break complex processes into numbered steps
3. Use comparisons to everyday objects when helpful (e.g. "reinforcement bars are like the skeleton inside your body — they give the structure its strength")
4. Mention safety tips where relevant
5. If a BIS standard applies, mention it naturally

For troubleshooting questions (e.g. "why is my wall cracking"):
1. Explain the most likely causes simply
2. Give actionable advice on what to do
3. Say when they should consult a professional

For comparison questions (e.g. "which is better, brick or block?"):
1. Give a clear recommendation for a beginner
2. Explain the pros and cons in plain language
3. Mention cost, availability, and ease of use where relevant

ALWAYS:
- Keep answers well-structured with short paragraphs
- Never dump a wall of text — use bullet points and numbered lists
- End every answer with a follow-up invitation like "Want me to explain any part of this in more detail?" or "Have a follow-up question? Just ask!"
- If you don't know something specific (like a local price or a very new regulation), say so honestly and suggest where they can find the answer

NEVER:
- Use unexplained jargon
- Give just a list of standard numbers with no explanation
- Be dismissive of "basic" questions — every question deserves a full, helpful answer
- Refuse to answer construction or engineering questions because they seem too simple"""


def get_groq_response(messages: list[dict]) -> str:
    """Call Groq API with full conversation history."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        try:
            import streamlit as st
            api_key = st.secrets.get("GROQ_API_KEY")
        except Exception:
            pass
    if not api_key:
        return "⚠️ GROQ_API_KEY not set. Please add it to your .env file or Streamlit secrets."
    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.5,
            max_tokens=1200,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Error reaching AI: {e}"


def render_message(role: str, content: str):
    """Render a single chat message bubble."""
    if role == "user":
        st.markdown(
            f'<div class="msg-user">'
            f'  <div class="bubble">{content}</div>'
            f'  <div class="avatar">🧑</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    else:
        # Use st.markdown for bot so markdown (bold, lists, code) renders properly
        col_av, col_bub = st.columns([0.055, 0.945])
        with col_av:
            st.markdown(
                '<div class="avatar" style="width:34px;height:34px;border-radius:50%;'
                'background:linear-gradient(135deg,#0D5C2C,#1A9A50);'
                'display:flex;align-items:center;justify-content:center;'
                'font-size:1rem;margin-top:4px;">🤖</div>',
                unsafe_allow_html=True,
            )
        with col_bub:
            st.markdown(
                f'<div style="background:linear-gradient(145deg,#071420,#050E18);'
                f'border:1px solid rgba(26,154,80,0.22);border-left:3px solid #1A9A50;'
                f'color:#C0D0D8;padding:14px 18px;border-radius:18px 18px 18px 4px;'
                f'font-size:0.91rem;line-height:1.75;box-shadow:0 4px 16px rgba(0,0,0,0.4);">'
                f'{content}'
                f'</div>',
                unsafe_allow_html=True,
            )


# ── Session State ──
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []   # full conversation: [{role, content}]
if "pending_input" not in st.session_state:
    st.session_state.pending_input = None

# ── Header ──
st.markdown("""
<div class="page-header">
    <h1>💬 BIS AI Assistant</h1>
    <p>Ask anything about BIS standards, construction materials, or building practices — in plain language.</p>
</div>
""", unsafe_allow_html=True)

# ── Starter suggestions (only shown on empty chat) ──
starters = [
    ("🏗️", "What is IS 269 and why do I need it?"),
    ("🧱", "What is the difference between M20 and M25 concrete?"),
    ("🔩", "Why do buildings use TMT steel bars instead of regular iron?"),
    ("🏠", "My cement wall is cracking — what are the possible reasons?"),
    ("📋", "What materials should I use for a strong roof slab?"),
    ("⚙️",  "What does 'compressive strength' mean in simple words?"),
]

if not st.session_state.chat_messages:
    st.markdown('<div class="starter-grid">', unsafe_allow_html=True)
    # Use Streamlit columns so buttons are actually clickable
    col1, col2 = st.columns(2)
    for i, (icon, q) in enumerate(starters):
        col = col1 if i % 2 == 0 else col2
        with col:
            if st.button(f"{icon}  {q}", key=f"start_{i}", use_container_width=True):
                st.session_state.pending_input = q
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

# ── Render conversation ──
if st.session_state.chat_messages:
    st.markdown('<div class="chat-wrapper">', unsafe_allow_html=True)
    for msg in st.session_state.chat_messages:
        render_message(msg["role"], msg["content"])
    st.markdown('</div>', unsafe_allow_html=True)

# ── Handle pending input (from starters or send button) ──
if st.session_state.pending_input:
    user_text = st.session_state.pending_input
    st.session_state.pending_input = None

    # Append user message
    st.session_state.chat_messages.append({"role": "user", "content": user_text})

    # Build Groq message list: system + full history
    groq_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.chat_messages
    ]

    with st.spinner("🤖 Thinking…"):
        reply = get_groq_response(groq_messages)

    st.session_state.chat_messages.append({"role": "assistant", "content": reply})
    st.rerun()

# ── Input bar ──
st.markdown("<br>", unsafe_allow_html=True)
st.divider()

inp_col, send_col, clear_col = st.columns([6, 1, 1])
with inp_col:
    user_input = st.text_input(
        "Message",
        placeholder="Ask anything about BIS standards or construction…",
        label_visibility="collapsed",
        key="chat_input_box",
    )
with send_col:
    send_btn = st.button("Send ➤", type="primary", use_container_width=True)
with clear_col:
    if st.button("🗑️ Clear", use_container_width=True):
        st.session_state.chat_messages = []
        st.session_state.pending_input = None
        st.rerun()

if send_btn and user_input.strip():
    st.session_state.pending_input = user_input.strip()
    st.rerun()

# ── Empty state placeholder ──
if not st.session_state.chat_messages:
    st.markdown("""
    <div style="text-align:center; color:#2A4050; padding:32px;
                border: 1px dashed rgba(26,154,80,0.15); border-radius:14px;
                max-width:820px; margin:0 auto;">
        <div style="font-size:2.5rem; margin-bottom:10px;">💬</div>
        <div style="color:#3A5565; font-size:0.9rem;">
            Pick a suggestion above or type your question below.<br>
            No jargon, no judgment — just clear, helpful answers.
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown(
    '<div style="text-align:center;color:#2A4050;font-size:0.75rem;">'
    'Powered by Groq Llama 3 · Specialized in BIS Standards & Indian Construction'
    '</div>',
    unsafe_allow_html=True,
)
