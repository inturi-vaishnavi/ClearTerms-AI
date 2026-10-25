import html

import streamlit as st

from analyzer import PolicyAnalysisError, analyze_policy


SAMPLE_POLICY = """Fictional Example Service Privacy Policy

This fictional service collects your email address and the profile details you
choose to provide when you create an account. It uses this information to
operate and improve the service.

The service may share limited usage data with fictional analytics provider
Example Metrics. Account information is retained while your account is active.
You can request account deletion through the service's support page.
"""

FINDING_LABELS = {
    "summary": "Plain-English Summary",
    "data_collected": "Data Collected",
    "information_sharing": "Information Sharing",
    "retention_and_deletion": "Retention and Account Deletion",
}
STATUS_CLASSES = {
    "Explicitly stated": "explicit",
    "Unclear": "unclear",
    "Not found in provided text": "not-found",
}


def load_sample_policy() -> None:
    if st.session_state.policy_source == "Load fictional sample":
        st.session_state.policy_text = SAMPLE_POLICY
    else:
        st.session_state.policy_text = ""
    st.session_state.analysis_result = None
    st.session_state.analysis_source = None


def render_finding(label: str, finding: dict[str, str], number: str) -> None:
    explanation = html.escape(finding["explanation"])
    evidence = html.escape(finding["evidence"])
    status = html.escape(finding["status"])
    status_class = STATUS_CLASSES[finding["status"]]
    if finding["evidence"]:
        evidence_content = f"<blockquote>{evidence}</blockquote>"
    else:
        evidence_content = (
            '<p class="ct-no-evidence">No verbatim excerpt was identified in '
            "the provided text.</p>"
        )

    st.markdown(
        f"""
        <article class="ct-finding">
          <div class="ct-finding-heading">
            <div class="ct-finding-title">
              <span class="ct-number">{number}</span>
              <h3>{html.escape(label)}</h3>
            </div>
            <span class="ct-status ct-status-{status_class}">{status}</span>
          </div>
          <div class="ct-finding-content">
            <div>
              <p class="ct-eyebrow">PLAIN-ENGLISH EXPLANATION</p>
              <p class="ct-explanation">{explanation}</p>
            </div>
            <div class="ct-evidence">
              <p class="ct-eyebrow">ORIGINAL POLICY TEXT</p>
              {evidence_content}
            </div>
          </div>
        </article>
        """,
        unsafe_allow_html=True,
    )


st.set_page_config(page_title="ClearTerms", page_icon="📝", layout="wide")

st.markdown(
    """
    <style>
      :root {
        --ct-forest: #123d2b;
        --ct-green: #2f6b4f;
        --ct-pale: #edf6ef;
        --ct-mist: #f6faf7;
        --ct-ink: #17251d;
        --ct-muted: #637168;
        --ct-line: #dce8df;
      }
      [data-testid="stAppViewContainer"] {
        background: var(--ct-mist);
        color: var(--ct-ink);
      }
      [data-testid="stHeader"] {
        background: transparent;
      }
      .block-container {
        max-width: 1120px;
        padding-top: 2rem;
        padding-bottom: 3rem;
      }
      .ct-intro h1, .ct-section-heading h2, .ct-finding-title h3 {
        color: var(--ct-forest);
        letter-spacing: -0.035em;
      }
      .ct-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        padding: 1rem 1.25rem;
        margin-bottom: 2rem;
        border: 1px solid var(--ct-line);
        border-radius: 18px;
        background: rgba(255, 255, 255, 0.88);
        box-shadow: 0 8px 28px rgba(18, 61, 43, 0.05);
      }
      .ct-brand {
        display: flex;
        align-items: center;
        gap: 0.8rem;
      }
      .ct-brand-mark {
        display: grid;
        width: 42px;
        height: 42px;
        place-items: center;
        border-radius: 13px;
        color: white;
        background: var(--ct-forest);
        font-size: 1.15rem;
        font-weight: 700;
      }
      .ct-brand-name {
        margin: 0;
        color: var(--ct-forest);
        font-size: 1.2rem;
        font-weight: 700;
      }
      .ct-brand-tagline {
        margin: 0.12rem 0 0;
        color: var(--ct-muted);
        font-size: 0.82rem;
      }
      .ct-header-note {
        padding: 0.45rem 0.75rem;
        border-radius: 999px;
        color: var(--ct-green);
        background: var(--ct-pale);
        font-size: 0.75rem;
        font-weight: 600;
      }
      .ct-intro {
        max-width: 760px;
        padding: 0.25rem 0 1rem;
      }
      .ct-kicker, .ct-eyebrow {
        margin: 0 0 0.5rem;
        color: var(--ct-green);
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.1em;
      }
      .ct-intro h1 {
        margin: 0 0 0.65rem;
        font-size: clamp(2rem, 5vw, 3.1rem);
        line-height: 1.08;
      }
      .ct-intro-copy {
        margin: 0;
        color: var(--ct-muted);
        font-size: 1.03rem;
        line-height: 1.65;
      }
      .ct-finding, .ct-summary-card, .ct-disclaimer,
      .ct-empty-state {
        border: 1px solid var(--ct-line);
        border-radius: 18px;
        background: #fff;
        box-shadow: 0 8px 24px rgba(18, 61, 43, 0.045);
      }
      div[data-testid="stVerticalBlockBorderWrapper"] {
        border: 1px solid var(--ct-line);
        border-radius: 18px;
        background: #fff;
        box-shadow: 0 8px 24px rgba(18, 61, 43, 0.045);
      }
      .ct-panel-title {
        margin: 0 0 0.35rem;
        color: var(--ct-forest);
        font-size: 1.1rem;
        font-weight: 700;
      }
      .ct-panel-copy {
        margin: 0 0 1rem;
        color: var(--ct-muted);
        font-size: 0.88rem;
      }
      [data-testid="stTextArea"] textarea {
        min-height: 260px;
        border-color: var(--ct-line);
        border-radius: 12px;
        background: #fbfdfb;
        line-height: 1.6;
      }
      [data-testid="stSelectbox"] [data-baseweb="select"] > div {
        border-color: var(--ct-line);
        border-radius: 10px;
      }
      [data-testid="stButton"] button[kind="primary"] {
        min-height: 46px;
        border: 0;
        border-radius: 11px;
        background: var(--ct-forest);
        font-weight: 650;
      }
      [data-testid="stButton"] button[kind="primary"]:hover {
        background: var(--ct-green);
      }
      .ct-section-heading {
        margin: 2rem 0 1rem;
      }
      .ct-section-heading h2 {
        margin: 0;
        font-size: 1.55rem;
      }
      .ct-section-heading p {
        margin: 0.4rem 0 0;
        color: var(--ct-muted);
      }
      .ct-summary-card {
        height: 100%;
        box-sizing: border-box;
        padding: 1rem 1.1rem;
        background: linear-gradient(150deg, #fff, #f4faf5);
      }
      .ct-summary-card .ct-explanation {
        margin: 0.55rem 0 0;
        font-size: 0.9rem;
      }
      .ct-finding {
        padding: 1.25rem;
        margin: 0.85rem 0;
      }
      .ct-finding-heading, .ct-finding-title {
        display: flex;
        align-items: center;
        gap: 0.7rem;
      }
      .ct-finding-heading {
        justify-content: space-between;
        flex-wrap: wrap;
        padding-bottom: 0.9rem;
        border-bottom: 1px solid var(--ct-line);
      }
      .ct-finding-title h3 {
        margin: 0;
        font-size: 1.05rem;
        letter-spacing: -0.015em;
      }
      .ct-number {
        display: inline-grid;
        width: 30px;
        height: 30px;
        place-items: center;
        border-radius: 9px;
        color: var(--ct-green);
        background: var(--ct-pale);
        font-size: 0.72rem;
        font-weight: 700;
      }
      .ct-status {
        display: inline-block;
        padding: 0.38rem 0.7rem;
        border-radius: 999px;
        font-size: 0.72rem;
        font-weight: 650;
      }
      .ct-status-explicit {
        color: #1f6344;
        background: #e4f4e9;
      }
      .ct-status-unclear {
        color: #835617;
        background: #fff2d8;
      }
      .ct-status-not-found {
        color: #58645c;
        background: #edf1ee;
      }
      .ct-finding-content {
        display: grid;
        grid-template-columns: minmax(0, 1.15fr) minmax(0, 0.85fr);
        gap: 1.4rem;
        padding-top: 1.1rem;
      }
      .ct-eyebrow {
        margin-bottom: 0.45rem;
        color: #718078;
        font-size: 0.64rem;
      }
      .ct-explanation {
        margin: 0;
        color: var(--ct-ink);
        font-size: 0.95rem;
        line-height: 1.65;
      }
      .ct-evidence {
        padding: 0.9rem;
        border-radius: 12px;
        background: var(--ct-pale);
      }
      .ct-evidence blockquote {
        margin: 0;
        padding: 0;
        color: #42534a;
        font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
        font-size: 0.82rem;
        line-height: 1.65;
        white-space: pre-wrap;
        overflow-wrap: anywhere;
      }
      .ct-no-evidence {
        margin: 0;
        color: var(--ct-muted);
        font-size: 0.84rem;
        line-height: 1.5;
      }
      .ct-disclaimer {
        padding: 1rem 1.1rem;
        margin: 1.3rem 0;
        color: #42534a;
        background: #eef6f0;
        font-size: 0.84rem;
        line-height: 1.55;
      }
      .ct-disclaimer strong {
        color: var(--ct-forest);
      }
      .ct-empty-state {
        padding: 1.5rem;
        color: var(--ct-muted);
        text-align: center;
      }
      @media (max-width: 720px) {
        .block-container {
          padding: 1rem 1rem 2rem;
        }
        .ct-header {
          align-items: flex-start;
          padding: 0.85rem;
        }
        .ct-header-note {
          display: none;
        }
        .ct-panel {
          padding: 1rem;
        }
        .ct-finding-content {
          grid-template-columns: 1fr;
          gap: 1rem;
        }
      }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <header class="ct-header">
      <div class="ct-brand">
        <div class="ct-brand-mark">C</div>
        <div>
          <p class="ct-brand-name">ClearTerms</p>
          <p class="ct-brand-tagline">See what you're agreeing to.</p>
        </div>
      </div>
      <span class="ct-header-note">PLAIN-LANGUAGE POLICY REVIEW</span>
    </header>
    <section class="ct-intro">
      <p class="ct-kicker">A CLEARER LOOK AT THE FINE PRINT</p>
      <h1>Understand the terms.<br>Keep the context.</h1>
      <p class="ct-intro-copy">Explore what a policy says about your data,
      sharing, and account details—with plain-English explanations grounded
      in the original text.</p>
    </section>
    """,
    unsafe_allow_html=True,
)

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "analysis_source" not in st.session_state:
    st.session_state.analysis_source = None

with st.container(border=True):
    st.markdown(
        """
        <p class="ct-panel-title">Start with a policy</p>
        <p class="ct-panel-copy">Paste the text you want to understand, or load
        the fictional example to explore the experience.</p>
        """,
        unsafe_allow_html=True,
    )
    st.selectbox(
        "Policy text",
        ("Paste your own", "Load fictional sample"),
        key="policy_source",
        on_change=load_sample_policy,
    )
    st.text_area(
        "Paste a privacy policy or terms-of-service document",
        height=280,
        key="policy_text",
        placeholder="Paste the document text here...",
    )

    if st.button("Analyze Policy", type="primary"):
        policy_text = st.session_state.policy_text
        st.session_state.analysis_result = None
        st.session_state.analysis_source = None
        if not policy_text.strip():
            st.error(
                "Please paste a policy or load the fictional sample before analyzing."
            )
        else:
            try:
                with st.spinner("Reviewing the supplied policy text..."):
                    result = analyze_policy(policy_text)
            except PolicyAnalysisError as error:
                st.error(str(error))
            else:
                st.session_state.analysis_result = result
                st.session_state.analysis_source = policy_text

analysis_result = st.session_state.analysis_result
if analysis_result and st.session_state.analysis_source == st.session_state.policy_text:
    st.markdown(
        """
        <div class="ct-section-heading">
          <p class="ct-kicker">YOUR POLICY REVIEW</p>
          <h2>Plain-English overview</h2>
          <p>Findings below are based only on the text you provided.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    summary = analysis_result["summary"]
    st.markdown(
        f"""
        <article class="ct-summary-card">
          <p class="ct-eyebrow">AT A GLANCE · {html.escape(summary["status"])}</p>
          <p class="ct-explanation">{html.escape(summary["explanation"])}</p>
        </article>
        """,
        unsafe_allow_html=True,
    )

    finding_items = [
        (FINDING_LABELS[field], analysis_result[field])
        for field in FINDING_LABELS
    ]
    all_findings = finding_items + [
        ("Important Clause", finding)
        for finding in analysis_result["important_clauses"]
    ]
    status_counts = {
        status: sum(1 for _, finding in all_findings if finding["status"] == status)
        for status in (
            "Explicitly stated",
            "Unclear",
            "Not found in provided text",
        )
    }
    metric_columns = st.columns(3)
    metric_specs = (
        ("Explicitly stated", "EXPLICITLY STATED", "explicit"),
        ("Unclear", "UNCLEAR", "unclear"),
        ("Not found in provided text", "NOT FOUND IN TEXT", "not-found"),
    )
    for column, (status, label, status_class) in zip(metric_columns, metric_specs):
        with column:
            st.markdown(
                f"""
                <div class="ct-summary-card">
                  <p class="ct-eyebrow">{label}</p>
                  <p class="ct-explanation">
                    <span class="ct-status ct-status-{status_class}">
                      {status_counts[status]}
                    </span>
                    finding(s)
                  </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    missing_information_note = html.escape(
        analysis_result["missing_information_note"]
    )
    st.markdown(
        f"""
        <div class="ct-disclaimer">
          <strong>Informational notice:</strong> These automated explanations
          are for educational review only, not legal advice.
          {missing_information_note} Check important details against the
          complete original policy.
        </div>
        <div class="ct-section-heading">
          <p class="ct-kicker">EVIDENCE-BACKED FINDINGS</p>
          <h2>What the policy text says</h2>
          <p>Each explanation is paired with a verbatim excerpt when one was
          identified in the supplied text.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    for index, (label, finding) in enumerate(finding_items, start=1):
        render_finding(label, finding, f"{index:02}")
    for index, finding in enumerate(analysis_result["important_clauses"], start=1):
        render_finding(f"Important Clause {index}", finding, f"{index + 4:02}")

    if not analysis_result["important_clauses"]:
        st.markdown(
            '<div class="ct-empty-state">No additional important clauses were '
            "returned for the supplied text.</div>",
            unsafe_allow_html=True,
        )
elif not analysis_result:
    st.markdown(
        """
        <div class="ct-empty-state">
          <strong>Your findings will appear here.</strong><br>
          Add a policy above and choose Analyze Policy to review its contents.
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        """
        <div class="ct-empty-state">
          <strong>Your policy text has changed.</strong><br>
          Run Analyze Policy again to refresh the findings for this text.
        </div>
        """,
        unsafe_allow_html=True,
    )
