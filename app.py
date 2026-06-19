import streamlit as st
from groq import Groq
import PyPDF2
import os
import io
import re
from datetime import datetime

# ── PDF export ────────────────────────────────────────────────────────────────
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# ── CONFIG ────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="PDF Chat AI", page_icon="📄", layout="wide")
MODEL = "llama-3.3-70b-versatile"

@st.cache_resource
def get_client():
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        st.error("⚠️ GROQ_API_KEY not set.")
        st.stop()
    return Groq(api_key=api_key)

client = get_client()

# ── HELPERS ───────────────────────────────────────────────────────────────────
def read_pdf_by_pages(file):
    """Returns list of (page_num, text) tuples"""
    try:
        reader = PyPDF2.PdfReader(file)
        pages = []
        for i, page in enumerate(reader.pages, 1):
            text = page.extract_text() or ""
            if text.strip():
                pages.append((i, text))
        return pages, len(reader.pages)
    except Exception as e:
        return [], 0

def build_context_with_pages(pages, max_chars=12000):
    """Build context string with page markers"""
    context = ""
    for page_num, text in pages:
        chunk = f"\n[PAGE {page_num}]\n{text}\n"
        if len(context) + len(chunk) > max_chars:
            context += f"\n[Remaining pages truncated — document too long]"
            break
        context += chunk
    return context

def stream_ai(messages, max_tokens=1500):
    """Stream response, return full text"""
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            max_tokens=max_tokens,
            stream=True
        )
        box = st.empty()
        full = ""
        for chunk in response:
            delta = chunk.choices[0].delta.content or ""
            full += delta
            box.markdown(full + "▌")
        box.markdown(full)
        return full
    except Exception as e:
        st.error(f"AI error: {e}")
        return None

def call_ai(messages, max_tokens=1500):
    """Non-streaming AI call"""
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return None

def word_count(pages):
    return sum(len(t.split()) for _, t in pages)

def reading_time(words):
    mins = words // 200
    return f"{mins} min read" if mins > 0 else "< 1 min read"

def export_chat_txt(filename, messages):
    lines = [f"PDF Chat Export — {filename}", f"Generated: {datetime.now().strftime('%B %d, %Y %H:%M')}", "="*60, ""]
    for m in messages:
        role = "You" if m["role"] == "user" else "AI"
        lines.append(f"{role}: {m['content']}")
        lines.append("")
    return "\n".join(lines)

def export_chat_pdf(filename, messages):
    if not PDF_AVAILABLE:
        return None
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=0.75*inch, leftMargin=0.75*inch,
                            topMargin=0.75*inch, bottomMargin=0.75*inch)
    styles = getSampleStyleSheet()
    story = []
    title_style = ParagraphStyle("T", parent=styles["Title"], fontSize=16,
                                  spaceAfter=4, textColor=colors.HexColor("#1a1a2e"))
    story.append(Paragraph(f"📄 PDF Chat — {filename}", title_style))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y %H:%M')}", styles["Normal"]))
    story.append(Spacer(1, 0.2*inch))
    for m in messages:
        role = "You" if m["role"] == "user" else "AI Assistant"
        role_style = ParagraphStyle(
            "R", parent=styles["Normal"],
            textColor=colors.HexColor("#0984e3") if m["role"] == "user" else colors.HexColor("#00b894"),
            fontName="Helvetica-Bold", fontSize=10, spaceBefore=8
        )
        story.append(Paragraph(role, role_style))
        for line in m["content"].split("\n"):
            if line.strip():
                story.append(Paragraph(line.strip(), styles["Normal"]))
        story.append(Spacer(1, 0.05*inch))
    doc.build(story)
    buffer.seek(0)
    return buffer

# ── SESSION STATE ─────────────────────────────────────────────────────────────
defaults = {
    "pdf_messages": [],
    "pdf_summary": "",
    "pdf_suggestions": [],
    "pdf_entities": "",
    "pdf_name": "",
    "pdf_pages": [],
    "pdf_total_pages": 0,
    "pdf_context": "",
    "answer_mode": "Balanced",
    "language": "English",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── SYSTEM PROMPT BUILDER ─────────────────────────────────────────────────────
def build_system_prompt(context, mode, language):
    lang_map = {
        "English": "Respond in English.",
        "தமிழ் (Tamil)": "Respond entirely in Tamil language.",
        "हिंदी (Hindi)": "Respond entirely in Hindi language.",
        "Simple English": "Respond in very simple English. Short sentences. Easy words. Like explaining to a 12-year-old."
    }
    mode_map = {
        "Balanced":   "Give clear, balanced answers — not too long, not too short.",
        "Detailed":   "Give thorough, detailed answers with full context from the document.",
        "Bullet Points": "Always answer in bullet points. Be concise.",
        "Simple":     "Use very simple language. Short answers. Plain words only.",
        "Expert":     "Give expert-level analysis. Include implications, comparisons, and deeper insights."
    }
    return f"""You are an expert document assistant. Answer questions ONLY using the document content below.

RULES:
1. Always cite the page number: say "(Page X)" at the end of relevant points
2. If answer not found in document: say "This information is not in the document."
3. Never make up information not in the document
4. {mode_map.get(mode, '')}
5. {lang_map.get(language, 'Respond in English.')}

DOCUMENT: {st.session_state.pdf_name}

{context}"""

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("⚙️ Settings")

    st.session_state.answer_mode = st.selectbox(
        "Answer Style",
        ["Balanced", "Detailed", "Bullet Points", "Simple", "Expert"],
        index=0
    )
    st.session_state.language = st.selectbox(
        "Response Language",
        ["English", "Simple English", "தமிழ் (Tamil)", "हिंदी (Hindi)"],
        index=0
    )

    st.divider()

    if st.session_state.pdf_name:
        st.markdown(f"**📄 {st.session_state.pdf_name}**")
        st.caption(f"{st.session_state.pdf_total_pages} pages · {word_count(st.session_state.pdf_pages):,} words · {reading_time(word_count(st.session_state.pdf_pages))}")

        st.divider()

        # Export chat
        if st.session_state.pdf_messages:
            st.markdown("**💾 Export Chat**")
            col1, col2 = st.columns(2)
            with col1:
                txt = export_chat_txt(st.session_state.pdf_name, st.session_state.pdf_messages)
                st.download_button("📥 TXT", data=txt,
                    file_name=f"chat_{st.session_state.pdf_name[:20]}.txt",
                    mime="text/plain", use_container_width=True)
            with col2:
                if PDF_AVAILABLE:
                    pdf = export_chat_pdf(st.session_state.pdf_name, st.session_state.pdf_messages)
                    if pdf:
                        st.download_button("📥 PDF", data=pdf,
                            file_name=f"chat_{st.session_state.pdf_name[:20]}.pdf",
                            mime="application/pdf", use_container_width=True)

        st.divider()
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.pdf_messages = []
            st.rerun()
        if st.button("📂 Load New PDF", use_container_width=True):
            for k, v in defaults.items():
                st.session_state[k] = v
            st.rerun()

# ── MAIN ──────────────────────────────────────────────────────────────────────
st.title("📄 PDF Chat AI")
st.caption("Upload any PDF — get instant summary, smart insights, and chat in any language.")

# ── FILE UPLOAD ───────────────────────────────────────────────────────────────
if not st.session_state.pdf_name:
    uploaded_file = st.file_uploader("Upload your PDF", type="pdf")

    if uploaded_file:
        with st.spinner("Reading PDF..."):
            pages, total_pages = read_pdf_by_pages(uploaded_file)

        if not pages:
            st.error("Could not read this PDF. Make sure it's not scanned/image-only.")
        else:
            st.session_state.pdf_pages       = pages
            st.session_state.pdf_total_pages = total_pages
            st.session_state.pdf_name        = uploaded_file.name
            st.session_state.pdf_context     = build_context_with_pages(pages)

            words = word_count(pages)
            c1, c2, c3 = st.columns(3)
            c1.metric("📄 Pages", total_pages)
            c2.metric("📝 Words", f"{words:,}")
            c3.metric("⏱️ Reading Time", reading_time(words))

            # Auto-generate summary + suggestions + entities
            context = st.session_state.pdf_context

            with st.spinner("Generating document briefing..."):
                summary_prompt = f"""Analyze this document and respond in EXACTLY this format:

DOCUMENT TYPE: [what kind of document is this]

ONE-LINE SUMMARY: [single sentence describing the document]

KEY POINTS:
- [key point 1]
- [key point 2]
- [key point 3]
- [key point 4]
- [key point 5]

KEY ENTITIES:
- People/Organizations: [names found or None]
- Dates/Deadlines: [dates found or None]
- Numbers/Amounts: [important figures or None]
- Locations: [places mentioned or None]

5 SMART QUESTIONS TO ASK:
1. [relevant question]
2. [relevant question]
3. [relevant question]
4. [relevant question]
5. [relevant question]

Document:
{context[:8000]}"""

                result = call_ai([{"role": "user", "content": summary_prompt}], max_tokens=1000)

            if result:
                # Parse suggestions
                suggestions = re.findall(r'\d\.\s(.+)', result)
                st.session_state.pdf_suggestions = suggestions[:5]
                st.session_state.pdf_summary     = result
                st.session_state.pdf_entities    = result

            st.rerun()

    else:
        st.info("👆 Upload a PDF to get started.")

        # Feature showcase
        st.markdown("---")
        st.markdown("### ✨ What makes this different")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("**🎯 Smart Briefing**\nAuto-generates summary, key points, and entities the moment you upload")
            st.markdown("**💬 5 Answer Styles**\nBalanced · Detailed · Bullet Points · Simple · Expert")
        with col2:
            st.markdown("**📍 Page Citations**\nEvery answer tells you which page the info came from")
            st.markdown("**🌐 4 Languages**\nEnglish · Simple English · Tamil · Hindi")
        with col3:
            st.markdown("**💡 Smart Questions**\nAI suggests relevant questions based on your document")
            st.markdown("**📥 Export Chat**\nDownload full conversation as TXT or PDF")

# ── MAIN INTERFACE (after PDF loaded) ─────────────────────────────────────────
else:
    # ── Document Briefing ──
    if st.session_state.pdf_summary:
        with st.expander("📋 Document Briefing (auto-generated)", expanded=not st.session_state.pdf_messages):
            # Extract sections for display
            summary = st.session_state.pdf_summary

            # One-line summary
            one_line = re.search(r"ONE-LINE SUMMARY:\s*(.+)", summary)
            if one_line:
                st.info(f"💡 {one_line.group(1).strip()}")

            col_left, col_right = st.columns(2)

            with col_left:
                # Key points
                key_points_match = re.search(r"KEY POINTS:(.*?)KEY ENTITIES:", summary, re.DOTALL)
                if key_points_match:
                    st.markdown("**📌 Key Points**")
                    points = re.findall(r"-\s(.+)", key_points_match.group(1))
                    for p in points:
                        st.markdown(f"• {p.strip()}")

            with col_right:
                # Entities
                entities_match = re.search(r"KEY ENTITIES:(.*?)5 SMART QUESTIONS", summary, re.DOTALL)
                if entities_match:
                    st.markdown("**🔍 Key Information Found**")
                    entities = re.findall(r"-\s(.+)", entities_match.group(1))
                    for e in entities:
                        if "None" not in e:
                            st.markdown(f"• {e.strip()}")

    # ── Suggested Questions ──
    if st.session_state.pdf_suggestions:
        st.markdown("**💡 Suggested Questions — click to ask:**")
        cols = st.columns(len(st.session_state.pdf_suggestions))
        for i, (col, q) in enumerate(zip(cols, st.session_state.pdf_suggestions)):
            with col:
                if st.button(q[:60] + ("..." if len(q) > 60 else ""),
                             key=f"sugg_{i}", use_container_width=True):
                    st.session_state["prefill_question"] = q
                    st.rerun()

    st.divider()

    # ── Chat History ──
    for message in st.session_state.pdf_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # ── Chat Input ──
    prefill = st.session_state.pop("prefill_question", "")
    user_question = prefill if prefill else st.chat_input(
        f"Ask anything about {st.session_state.pdf_name}..."
    )

    if user_question:
        st.session_state.pdf_messages.append({"role": "user", "content": user_question})
        with st.chat_message("user"):
            st.markdown(user_question)

        system = build_system_prompt(
            st.session_state.pdf_context,
            st.session_state.answer_mode,
            st.session_state.language
        )

        with st.chat_message("assistant"):
            result = stream_ai([
                {"role": "system", "content": system},
                *st.session_state.pdf_messages
            ])

        if result:
            st.session_state.pdf_messages.append({"role": "assistant", "content": result})
            st.rerun()

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.divider()
c1, c2, c3 = st.columns(3)
c1.caption("📄 PDF Chat AI")
c2.caption("🤖 Powered by Groq (LLaMA 3.3 70B) — Free")
c3.caption("Page citations · Multi-language · Smart briefing")