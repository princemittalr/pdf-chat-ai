# 📄 PDF Chat AI

<div align="center">

**Chat with any PDF in any language — instant summary, page citations, smart questions, and exported conversations.**

[![Live Demo](https://img.shields.io/badge/🚀_Live_Demo-Streamlit-FF4B4B?style=for-the-badge)](https://pdf-chatai.streamlit.app)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Groq](https://img.shields.io/badge/Groq-LLaMA_3.3_70B-F55036?style=for-the-badge)](https://groq.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

</div>

---

## 🔥 The Problem

PDFs are where important information goes to die.

Government scheme documents. Legal agreements. Research papers. Medical reports. NGO field manuals. Academic textbooks.

Most people — especially students and citizens in rural India — cannot extract what they need from a 40-page government PDF written in bureaucratic English.

> **This tool lets anyone have a conversation with any document — in their own language, at their own level.**

---

## ✨ What It Does

Upload any PDF → get an instant AI briefing → ask questions in plain language → get cited, accurate answers → export the conversation.

No reading required. No technical knowledge needed. Works in English, Tamil, and Hindi.

---

## 🎯 Key Features

| Feature | Description |
|---|---|
| **Auto Document Briefing** | On upload: instant summary, key points, entities, and document type — no questions needed |
| **Page Citations** | Every answer includes "(Page X)" — know exactly where the information came from |
| **5 AI-Suggested Questions** | Clickable questions generated from your specific document — no blank page problem |
| **5 Answer Styles** | Balanced · Detailed · Bullet Points · Simple · Expert — switch anytime |
| **4 Language Support** | English · Simple English · தமிழ் · हिंदी — full responses in chosen language |
| **Streaming Responses** | Answers appear word-by-word — no waiting |
| **Smart Entity Extraction** | Auto-finds: people, organizations, dates, amounts, locations |
| **Export Chat** | Download full conversation as TXT or PDF |
| **Document Stats** | Pages · Word count · Reading time shown on upload |
| **Sidebar Controls** | Answer style + language switcher always accessible |

---

## 🧠 Auto Document Briefing

The moment you upload a PDF, before you ask a single question, the tool generates:

```
📄 Document Type     →  Government Scheme Notification
💡 One-line Summary  →  Guidelines for AICTE Pragati Scholarship 2026 applications
📌 Key Points        →  5 most important facts from the document
🔍 Key Entities      →  People · Dates · Amounts · Locations found
💡 Smart Questions   →  5 relevant questions to ask this specific document
```

---

## 📍 Page Citation System

Other PDF chat tools tell you *what* is in the document.

This tool tells you *where.*

```
User:  What is the income limit for this scholarship?

AI:    The annual family income must not exceed ₹8 lakh per annum 
       for the student to be eligible. (Page 3)
       
       Students from families earning above this threshold are 
       explicitly excluded from consideration. (Page 3)
```

Every factual claim is traceable. Critical for legal documents, government schemes, and academic papers.

---

## 🌐 Language + Answer Style Matrix

| | Balanced | Detailed | Bullet Points | Simple | Expert |
|---|---|---|---|---|---|
| **English** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Simple English** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **தமிழ்** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **हिंदी** | ✅ | ✅ | ✅ | ✅ | ✅ |

20 possible combinations — every user gets answers in their preferred style and language.

---

## 🏗️ Tech Stack

```
Frontend          →  Streamlit
AI Engine         →  Groq API (LLaMA 3.3 70B) — streaming
PDF Parsing       →  PyPDF2 (page-by-page extraction)
PDF Export        →  ReportLab
Language          →  Python 3.10+
Deployment        →  Streamlit Community Cloud
```

---

## 🏗️ Architecture

```
User uploads PDF
      │
      ▼
PyPDF2 extracts text page-by-page
(preserves page numbers for citation)
      │
      ▼
Context built with [PAGE N] markers
      │
      ├──► Auto-briefing AI call (summary + entities + suggested questions)
      │
      ▼
User selects answer style + language (sidebar)
      │
      ▼
System prompt built dynamically
(citation rules + mode instructions + language rules)
      │
      ▼
Streaming chat with full conversation history
      │
      ▼
Export conversation as TXT or PDF
```

---

## 🚀 Run Locally

```bash
# Clone
git clone https://github.com/princemittalr/pdf-chat-ai.git
cd pdf-chat-ai

# Install
pip install streamlit groq PyPDF2 reportlab

# Set API key
export GROQ_API_KEY="your_groq_api_key"   # Free at console.groq.com

# Run
streamlit run app.py
```

---

## 📁 Project Structure

```
pdf-chat-ai/
├── app.py              # Main application
├── requirements.txt    # Dependencies
└── README.md
```

---

## 💡 Design Decisions

**Why page-by-page extraction instead of full text dump?**
Preserving page structure enables citations. A tool that says "this is on Page 7" is fundamentally more trustworthy and useful than one that gives an answer with no traceability — especially for legal, medical, or government documents.

**Why auto-briefing on upload?**
Most users don't know what questions to ask. The blank chat input is a barrier. Auto-briefing + suggested questions removes that barrier entirely — the tool starts being useful before the user types anything.

**Why 5 answer styles?**
A first-generation student reading a government scheme PDF needs Simple English. A lawyer reviewing a contract needs Expert mode with full detail. A journalist scanning for key facts needs Bullet Points. One mode fits none of them well.

**Why Tamil and Hindi support?**
The documents that matter most to underserved Indian communities — government schemes, legal notices, health guidelines — are often in English. Language should not be a barrier to understanding your own rights and entitlements.

---

## 🌍 Use Cases

| User | Document | What They Need |
|---|---|---|
| **Engineering student** | Scholarship scheme PDF | Am I eligible? What documents do I need? |
| **Rural citizen** | Government welfare notification | What benefits can I claim? How do I apply? |
| **NGO worker** | Field operations manual | What is the protocol for case X? |
| **Researcher** | 80-page academic paper | What were the key findings? What methodology was used? |
| **Job seeker** | Company policy document | What are the leave policies? What does clause 7 mean? |

---

## 🗺️ Roadmap

- [ ] Multi-PDF support — chat across multiple documents simultaneously
- [ ] Highlight mode — show exact sentences from PDF that answer the question
- [ ] Voice input — speak your question, get spoken answer
- [ ] Document comparison — "How does Document A differ from Document B?"
- [ ] Offline mode — local LLM support for sensitive documents

---

## 👨‍💻 Author

**Prince Mittal**
B.Tech CSE (AI/ML) · Dayananda Sagar University

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0077B5?style=flat&logo=linkedin)](https://linkedin.com/in/princemittalr)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-181717?style=flat&logo=github)](https://github.com/princemittalr)

---

## 📄 License

MIT License — free to use, modify, and deploy.

---

<div align="center">

*Built on the belief that no one should be locked out of information just because it's buried in a PDF.*

</div>