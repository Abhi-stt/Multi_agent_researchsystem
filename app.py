import streamlit as st
import time
from pipeline import run_research_pipeline

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Research Mind",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

  /* ── Reset & base ── */
  html, body, [class*="css"] { font-family: 'Syne', sans-serif; }

  .stApp {
    background: radial-gradient(1200px 700px at 50% -10%, #2a2450 0%, #131224 45%, #0b0b14 100%);
    color: #eceaf6;
  }

  /* ── Hide Streamlit chrome ── */
  #MainMenu, footer, header { visibility: hidden; }

  /* ── Hero banner ── */
  .hero {
    text-align: center;
    padding: 3.5rem 1rem 2rem;
    position: relative;
  }
  .hero-label {
    display: inline-block;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #b7afff;
    border: 1px solid #7c6af744;
    padding: 0.25rem 0.85rem;
    border-radius: 2rem;
    margin-bottom: 1.1rem;
    background: #7c6af71a;
  }
  .hero h1 {
    font-size: clamp(2.4rem, 5vw, 4rem);
    font-weight: 800;
    line-height: 1.1;
    letter-spacing: -0.02em;
    background: linear-gradient(135deg, #f3f1ff 20%, #b8acff 65%, #8f7dff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 0 0.6rem;
  }
  .hero p {
    font-size: 1.05rem;
    color: #b5b0d1;
    max-width: 520px;
    margin: 0 auto;
    line-height: 1.65;
  }

  /* ── Input area ── */
  .stTextInput > div > div > input {
    background: #151427 !important;
    border: 1.5px solid #2a2840 !important;
    border-radius: 10px !important;
    color: #eceaf6 !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 1rem !important;
    padding: 0.75rem 1.1rem !important;
    transition: border-color 0.2s;
  }
  .stTextInput > div > div > input:focus {
    border-color: #7c6af7 !important;
    box-shadow: 0 0 0 3px #7c6af740 !important;
  }
  .stTextInput > div > div > input::placeholder { color: #7b7698 !important; }

  /* ── Button ── */
  .stButton > button {
    background: linear-gradient(135deg, #7c6af7, #9f7aea) !important;
    color: #fff !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.04em !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.65rem 2rem !important;
    width: 100% !important;
    transition: opacity 0.2s, transform 0.15s !important;
  }
  .stButton > button:hover {
    opacity: 0.94 !important;
    transform: translateY(-1px) !important;
  }
  .stButton > button:active { transform: translateY(0) !important; }

  /* ── Pipeline step cards ── */
  .step-card {
    background: linear-gradient(145deg, #151427, #191733);
    border: 1px solid #2c2945;
    border-radius: 14px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 1rem;
    position: relative;
    overflow: hidden;
    box-shadow: 0 8px 24px rgba(5, 5, 10, 0.32);
  }
  .step-card.active  { border-color: #8f7dff; box-shadow: 0 0 0 1px #8f7dff, 0 10px 28px #7c6af72e; }
  .step-card.done    { border-color: #22c55e7a; }
  .step-card.pending { opacity: 0.55; }

  .step-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 0.3rem;
  }
  .step-badge {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    font-weight: 500;
    padding: 0.18rem 0.55rem;
    border-radius: 4px;
    text-transform: uppercase;
    letter-spacing: 0.1em;
  }
  .badge-search  { background: #1d3458; color: #8ec5ff; }
  .badge-scrape  { background: #1e3b2d; color: #6ee7a1; }
  .badge-write   { background: #3a2556; color: #d8b4fe; }
  .badge-critic  { background: #4a3220; color: #fdba74; }

  .step-title {
    font-size: 0.98rem;
    font-weight: 700;
    color: #eceaf6;
  }
  .step-desc {
    font-size: 0.82rem;
    color: #a49fbe;
    font-family: 'JetBrains Mono', monospace;
  }
  .step-status {
    margin-left: auto;
    font-size: 1.1rem;
  }

  /* ── Result expanders / text areas ── */
  .stExpander {
    background: #131224 !important;
    border: 1px solid #2c2945 !important;
    border-radius: 10px !important;
  }
  .result-box {
    background: #0f0f1b;
    border: 1px solid #25223a;
    border-radius: 8px;
    padding: 1rem 1.2rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    color: #c9c5df;
    line-height: 1.7;
    max-height: 340px;
    overflow-y: auto;
    white-space: pre-wrap;
    word-break: break-word;
  }

  /* ── Final report card ── */
  .report-card {
    background: linear-gradient(145deg, #141329, #1b1934);
    border: 1.5px solid #4b3fa3;
    border-radius: 16px;
    padding: 2rem;
    margin-top: 1.5rem;
    box-shadow: 0 12px 32px rgba(7, 7, 14, 0.35);
  }
  .report-card h2 {
    font-size: 1.5rem;
    font-weight: 800;
    color: #eae7ff;
    margin: 0 0 1.2rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
  .report-body {
    color: #cbc6e5;
    line-height: 1.8;
    font-size: 0.97rem;
  }

  /* ── Feedback card ── */
  .feedback-card {
    background: linear-gradient(145deg, #17131f, #1d1627);
    border: 1.5px solid #7a5033;
    border-radius: 16px;
    padding: 1.6rem;
    margin-top: 1rem;
  }
  .feedback-card h3 {
    font-size: 1.1rem;
    font-weight: 700;
    color: #f1b36f;
    margin: 0 0 0.8rem;
    display: flex;
    align-items: center;
    gap: 0.4rem;
  }
  .feedback-body {
    color: #d5c4b6;
    line-height: 1.75;
    font-size: 0.93rem;
  }

  /* ── Divider ── */
  hr { border-color: #2b2940 !important; }

  /* ── Spinner text ── */
  .stSpinner > div { color: #a699ff !important; }
</style>
""", unsafe_allow_html=True)

# ── Hero ────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-label">AI Research Mind</div>
  <h1>Deep Research,<br>On Demand</h1>
  <p>Enter any topic and watch the pipeline search, scrape, write, and critique — all in one pass.</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ── Input ───────────────────────────────────────────────────────────────────────
col_input, col_btn = st.columns([4, 1], gap="small")
with col_input:
    topic = st.text_input(
        label="Research topic",
        placeholder="e.g. Advances in quantum computing 2025",
        label_visibility="collapsed",
    )
with col_btn:
    run_clicked = st.button("Run →")

# ── Pipeline step definitions ───────────────────────────────────────────────────
STEPS = [
    ("01", "badge-search", "Search Agent",   "Scanning the web for relevant sources",     "🔍"),
    ("02", "badge-scrape", "Scraper Agent",  "Extracting deep content from top URLs",      "🕸️"),
    ("03", "badge-write",  "Writer Agent",   "Synthesising research into a report draft",  "✍️"),
    ("04", "badge-critic", "Critic Agent",   "Reviewing & scoring the final report",       "🧐"),
]

def render_steps(active: int = -1, done_up_to: int = -1):
    """Render pipeline step cards. active = 0-based index currently running."""
    for i, (num, badge, title, desc, _icon) in enumerate(STEPS):
        if i < done_up_to:
            css, status = "done",    "✅"
        elif i == active:
            css, status = "active",  "⏳"
        else:
            css, status = "pending", "○"

        st.markdown(f"""
        <div class="step-card {css}">
          <div class="step-header">
            <span class="step-badge {badge}">Step {num}</span>
            <span class="step-title">{title}</span>
            <span class="step-status">{status}</span>
          </div>
          <div class="step-desc">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

# ── Run pipeline ────────────────────────────────────────────────────────────────
if run_clicked:
    if not topic.strip():
        st.warning("Please enter a research topic first.")
    else:
        st.markdown("### ⚙️ Pipeline Progress")
        steps_placeholder = st.empty()
        status_placeholder = st.empty()

        # Show all steps as pending initially
        with steps_placeholder.container():
            render_steps(active=0, done_up_to=0)

        with st.spinner("Running research pipeline — this may take a minute..."):
            try:
                state = run_research_pipeline(topic)
            except Exception as e:
                st.error(f"Pipeline error: {e}")
                st.stop()

        # All done — show completed state
        with steps_placeholder.container():
            render_steps(active=-1, done_up_to=len(STEPS))

        st.success("✅ Pipeline complete!")

        st.markdown("---")

        # ── Intermediate results (collapsed by default) ─────────────────────
        st.markdown("### 📂 Intermediate Results")

        with st.expander("🔍 Search Results", expanded=False):
            st.markdown(f'<div class="result-box">{state.get("search_results", "—")}</div>',
                        unsafe_allow_html=True)

        with st.expander("🕸️ Scraped Content", expanded=False):
            st.markdown(f'<div class="result-box">{state.get("scraped_content", "—")}</div>',
                        unsafe_allow_html=True)

        # ── Final report ─────────────────────────────────────────────────────
        report = state.get("report", "")
        if report:
            st.markdown("---")
            st.markdown(f"""
            <div class="report-card">
              <h2>📄 Final Report</h2>
              <div class="report-body">{report}</div>
            </div>
            """, unsafe_allow_html=True)

            # Download button
            st.download_button(
                label="⬇️ Download Report (.txt)",
                data=report,
                file_name=f"report_{topic[:40].replace(' ', '_')}.txt",
                mime="text/plain",
            )

        # ── Critic feedback ───────────────────────────────────────────────────
        feedback = state.get("feedback", "")
        if feedback:
            st.markdown(f"""
            <div class="feedback-card">
              <h3>🧐 Critic Feedback</h3>
              <div class="feedback-body">{feedback}</div>
            </div>
            """, unsafe_allow_html=True)

else:
    # Idle state — show greyed-out steps
    st.markdown("### Pipeline Steps")
    render_steps()