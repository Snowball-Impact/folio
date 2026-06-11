import streamlit as st


def apply_global_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            --folio-navy: #0b1f3f;
            --folio-blue: #1459c8;
            --folio-mint: #0f9b8e;
            --folio-bg: #f7faff;
            --folio-border: #d8e3f7;
            --folio-muted: #60708f;
        }

        .stApp {
            background: var(--folio-bg);
        }

        h1, h2, h3 {
            color: var(--folio-navy);
            letter-spacing: 0;
        }

        .folio-hero {
            border: 1px solid var(--folio-border);
            border-radius: 8px;
            background: #ffffff;
            padding: 28px 30px;
            margin-bottom: 20px;
        }

        .folio-eyebrow {
            color: var(--folio-mint);
            font-weight: 700;
            font-size: 0.9rem;
            margin-bottom: 6px;
        }

        .folio-muted {
            color: var(--folio-muted);
        }

        .folio-card {
            border: 1px solid var(--folio-border);
            border-radius: 8px;
            background: #ffffff;
            padding: 18px;
            height: 100%;
        }

        .folio-metric {
            color: var(--folio-blue);
            font-size: 1.6rem;
            font-weight: 800;
        }

        .folio-nav-status {
            color: var(--folio-muted);
            font-size: 0.9rem;
            margin-bottom: 12px;
        }

        div.stButton > button {
            border-radius: 6px;
            border: 1px solid var(--folio-blue);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
