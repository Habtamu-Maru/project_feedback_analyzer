"""Streamlit app to manage the customer feedback analyzer.

Run with:  streamlit run app.py
"""

from __future__ import annotations

import csv
import io

import pandas as pd
import streamlit as st

from analyzer import Analysis, analyze_batch, analyze_review

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Customer Feedback Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
if "history" not in st.session_state:
    st.session_state.history = []


def add_to_history(result: dict) -> None:
    """Append a single analysis result to the in-session history."""
    st.session_state.history.append(result)


def load_sample_reviews() -> list[str]:
    """Load the sample reviews from sample_review.txt (first tuple element)."""
    try:
        with open("sample_review.txt", "r", encoding="utf-8") as f:
            content = f.read()
        # Parse tuples like ("text", "label", score, "theme")
        import re

        pattern = re.compile(r'\("(.*?)",\s*"(positive|negative|neutral)",\s*\d+,\s*"(.*?)"\)', re.DOTALL)
        return [m.group(1) for m in pattern.finditer(content)]
    except FileNotFoundError:
        return []


# ---------------------------------------------------------------------------
# Helpers / UI components
# ---------------------------------------------------------------------------
LABEL_COLORS = {
    "positive": "#2e7d32",
    "negative": "#c62828",
    "neutral": "#f9a825",
}


def render_result_card(result: Analysis | dict) -> None:
    """Render a single analysis result as a styled card."""
    if isinstance(result, Analysis):
        item = {
            "label": result.label,
            "score": result.score,
            "theme": result.theme,
        }
    else:
        item = result

    label = item.get("label", "unknown")
    score = item.get("score")
    theme = item.get("theme", "")

    color = LABEL_COLORS.get(label, "#616161")
    score_text = f"{score} / 5" if score is not None else "N/A"

    st.markdown(
        f"""
        <div style="border-left:6px solid {color}; background:#f8f9fa; padding:12px 16px; margin-bottom:8px; border-radius:4px;">
            <span style="font-weight:bold; color:{color}; text-transform:uppercase;">{label}</span>
            <span style="margin-left:12px; font-size:0.9rem;">⭐ {score_text}</span>
            <div style="margin-top:6px; color:#424242;">Theme: <b>{theme}</b></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def history_to_df() -> pd.DataFrame:
    return pd.DataFrame(st.session_state.history)


# ---------------------------------------------------------------------------
# Sidebar navigation
# ---------------------------------------------------------------------------
st.sidebar.title("📊 Feedback Analyzer")
st.sidebar.caption("Gemini-powered customer feedback analysis")
page = st.sidebar.radio(
    "Navigation",
    ["Analyze Review", "Batch Analysis", "Dashboard", "History & Export"],
)

st.sidebar.markdown("---")
if st.sidebar.button("Clear History"):
    st.session_state.history = []
    st.sidebar.success("History cleared.")

st.sidebar.markdown("---")
st.sidebar.caption(f"Analyzed reviews in session: **{len(st.session_state.history)}**")


# ---------------------------------------------------------------------------
# Page 1: Single review analysis
# ---------------------------------------------------------------------------
if page == "Analyze Review":
    st.title("🔍 Analyze a Single Review")
    st.write("Enter a customer review below and get its sentiment label, score, and main theme.")

    review_text = st.text_area(
        "Customer review",
        height=180,
        placeholder=("e.g. The delivery was quick and the food arrived hot."),
    )

    col1, col2 = st.columns([1, 5])
    with col1:
        analyze_btn = st.button("Analyze", type="primary", use_container_width=True)
    with col2:
        st.caption("Powered by Google Gemini")

    if analyze_btn:
        if not review_text.strip():
            st.warning("Please enter a review to analyze.")
        else:
            with st.spinner("Analyzing review..."):
                try:
                    result = analyze_review(review_text.strip())
                    st.subheader("Result")
                    render_result_card(result)
                    add_to_history(
                        {
                            "review": review_text.strip(),
                            "label": result.label,
                            "score": result.score,
                            "theme": result.theme,
                        }
                    )
                    st.success("Result added to history.")
                except Exception as exc:  # noqa: BLE001
                    st.error(f"Analysis failed: {exc}")

# ---------------------------------------------------------------------------
# Page 2: Batch analysis
# ---------------------------------------------------------------------------
elif page == "Batch Analysis":
    st.title("📦 Batch Analysis")
    st.write("Analyze multiple reviews at once. Put one review per line, or load the sample reviews.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Load sample reviews", use_container_width=True):
            samples = load_sample_reviews()
            if samples:
                st.session_state.batch_text = "\n".join(samples)
                st.success(f"Loaded {len(samples)} sample reviews.")
            else:
                st.error("Could not find sample_review.txt")
    with col2:
        if st.button("Clear text", use_container_width=True):
            st.session_state.batch_text = ""

    batch_text = st.text_area(
        "Reviews (one per line)",
        height=250,
        key="batch_text",
    )

    if st.button("Analyze batch", type="primary"):
        reviews = [r.strip() for r in batch_text.splitlines() if r.strip()]
        if not reviews:
            st.warning("Paste some reviews first.")
        else:
            with st.spinner(f"Analyzing {len(reviews)} reviews..."):
                results = analyze_batch(reviews)
            for r in results:
                add_to_history(r)
            st.session_state.last_batch = results
            st.success(f"Analyzed {len(results)} reviews.")

    if "last_batch" in st.session_state and st.session_state.last_batch:
        st.subheader("Batch Results")
        df = pd.DataFrame(st.session_state.last_batch)
        st.dataframe(df, use_container_width=True)
        for r in st.session_state.last_batch:
            st.markdown(f"**Review:** {r['review']}")
            render_result_card(r)

# ---------------------------------------------------------------------------
# Page 3: Dashboard
# ---------------------------------------------------------------------------
elif page == "Dashboard":
    st.title("📈 Dashboard")
    df = history_to_df()

    if df.empty:
        st.info("No analyses yet. Run some reviews first to see the dashboard.")
    else:
        valid = df[df["label"] != "error"]

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Reviews", len(df))
        col2.metric("Positive", int((valid["label"] == "positive").sum()))
        col3.metric("Negative", int((valid["label"] == "negative").sum()))
        col4.metric("Neutral", int((valid["label"] == "neutral").sum()))

        if not valid.empty:
            avg_score = valid["score"].dropna().mean()
            st.metric("Average Score", f"{avg_score:.2f} / 5")

        st.subheader("Sentiment Distribution")
        if not valid.empty:
            counts = valid["label"].value_counts()
            colors = [LABEL_COLORS.get(l, "#616161") for l in counts.index]
            st.bar_chart(counts)

        st.subheader("Top Themes")
        if not valid.empty:
            theme_counts = valid["theme"].value_counts().head(8)
            st.dataframe(theme_counts.rename("count"), use_container_width=True)

        st.subheader("Score Distribution")
        if not valid.empty:
            score_counts = valid["score"].value_counts().sort_index()
            st.bar_chart(score_counts)

# ---------------------------------------------------------------------------
# Page 4: History & export
# ---------------------------------------------------------------------------
else:
    st.title("🗂 History & Export")
    df = history_to_df()

    if df.empty:
        st.info("No analyses recorded in this session yet.")
    else:
        st.write(f"Showing **{len(df)}** analyzed reviews.")
        st.dataframe(df, use_container_width=True)

        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        st.download_button(
            label="Download results as CSV",
            data=csv_buffer.getvalue(),
            file_name="feedback_analysis.csv",
            mime="text/csv",
        )

        st.subheader("Detailed Results")
        for _, row in df.iterrows():
            st.markdown(f"**Review:** {row['review']}")
            render_result_card(
                {"label": row["label"], "score": row["score"], "theme": row["theme"]}
            )
