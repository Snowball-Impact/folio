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
            font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }

        section[data-testid="stSidebar"] {
            display: none;
        }

        .block-container {
            max-width: 1280px;
            padding-top: 18px;
        }

        h1, h2, h3 {
            color: var(--folio-navy);
            letter-spacing: 0;
        }

        .folio-topbar {
            align-items: center;
            background: #08142b;
            border-radius: 8px 8px 0 0;
            color: #ffffff;
            display: flex;
            justify-content: space-between;
            gap: 18px;
            margin-bottom: 0;
            padding: 18px 24px;
            position: sticky;
            top: 0;
            z-index: 999;
            flex-wrap: wrap;
        }

        .folio-brand-group {
            display: flex;
            flex-direction: column;
            gap: 6px;
        }

        .folio-nav-toggle {
            display: none;
        }

        .folio-hamburger {
            align-items: center;
            background: transparent;
            border: 1px solid rgba(255, 255, 255, 0.45);
            border-radius: 12px;
            color: #ffffff;
            cursor: pointer;
            display: none;
            font-size: 1.1rem;
            height: 42px;
            justify-content: center;
            padding: 0 14px;
        }

        .folio-nav {
            align-items: center;
            display: flex;
            gap: 14px;
        }

        .folio-nav-link {
            color: rgba(255, 255, 255, 0.92) !important;
            font-weight: 700;
            text-decoration: none;
            padding: 10px 14px;
            border-radius: 999px;
            transition: background 0.2s ease, color 0.2s ease;
        }

        .folio-nav-link:hover,
        .folio-nav-link-active {
            background: rgba(255, 255, 255, 0.16);
            color: rgba(255, 255, 255, 1) !important;
        }

        .folio-nav-link-logout {
            border: 1px solid var(--folio-border);
        }

        @media (max-width: 860px) {
            .folio-topbar {
                padding: 16px 20px;
            }

            .folio-hamburger {
                display: inline-flex;
            }

            .folio-nav {
                display: none;
                flex-direction: column;
                gap: 10px;
                margin-top: 12px;
                width: 100%;
                padding: 16px;
                background: rgba(8, 20, 43, 0.98);
                border-radius: 12px;
            }

            .folio-nav-toggle:checked + .folio-hamburger + .folio-nav {
                display: flex;
            }
        }

        .folio-brand {
            font-size: 1.8rem;
            font-weight: 900;
        }

        .folio-tagline {
            color: #b7c6e7;
            font-size: 0.95rem;
        }

        .stButton>button {
            border-radius: 999px;
            min-height: 42px;
            padding: 0.8rem 1.2rem;
            font-weight: 600;
            transition: transform 0.12s ease, box-shadow 0.12s ease;
        }

        .stButton>button:hover {
            transform: translateY(-1px);
        }

        .stButton>button[kind="secondary"] {
            background: #ffffff;
            border-color: #d8e3f7;
            color: var(--folio-navy);
        }

        .stButton>button[kind="primary"] {
            background: var(--folio-blue);
            border-color: var(--folio-blue);
            color: #ffffff;
        }

        .stTextInput>div>div>input,
        .stTextArea>div>div>textarea,
        .stSelectbox>div>div>div>select,
        .stMultiSelect>div>div>div>div {
            border-radius: 14px !important;
            border: 1px solid var(--folio-border) !important;
            padding: 14px !important;
            background: #ffffff !important;
            box-shadow: none !important;
        }

        .stTextInput>div>label,
        .stTextArea>div>label,
        .stSelectbox>div>label {
            font-weight: 700;
            color: var(--folio-navy);
        }

        .stTextInput>div>div>label,
        .stTextArea>div>div>label,
        .stSelectbox>div>div>label {
            display: none;
        }

        .folio-filter-row {
            align-items: center;
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-bottom: 18px;
        }

        .folio-search-box {
            width: 100%;
        }

        .folio-search-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
            gap: 16px;
        }

        .folio-search-title {
            color: rgba(255, 255, 255, 0.9);
            font-size: 0.95rem;
            font-weight: 700;
            letter-spacing: 0.02em;
        }

        .stTextInput>div>div>input {
            border-radius: 999px !important;
            padding: 14px 18px !important;
            background: rgba(255, 255, 255, 0.12) !important;
            color: #ffffff !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
        }

        .stTextInput>div>div>input::placeholder {
            color: rgba(255, 255, 255, 0.7) !important;
        }

        .stButton>button {
            min-height: 48px;
            padding: 0 18px;
            border-radius: 999px;
            background: rgba(255, 255, 255, 0.16);
            color: #ffffff;
            border: 1px solid rgba(255, 255, 255, 0.24);
        }

        .stButton>button:hover {
            background: rgba(255, 255, 255, 0.2);
        }

        .folio-pills {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 10px;
        }

        .folio-pills span {
            background: #edf4ff;
            border: 1px solid #d8e3f7;
            border-radius: 999px;
            color: var(--folio-navy);
            font-weight: 700;
            padding: 8px 14px;
        }

        .folio-home-cta {
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            margin-top: 24px;
        }

        .folio-home-hero {
            align-items: center;
            background:
                radial-gradient(circle at 76% 30%, rgba(20, 89, 200, 0.35), transparent 26%),
                linear-gradient(135deg, #071126, #111c36 62%, #0a1430);
            border-radius: 0 0 8px 8px;
            color: #ffffff;
            display: grid;
            gap: 24px;
            grid-template-columns: minmax(0, 1fr) minmax(300px, 0.9fr);
            min-height: 350px;
            padding: 40px 56px;
            margin-top: 0;
        }

        .folio-home-copy h1 {
            color: #ffffff;
            font-size: 3rem;
            line-height: 1.18;
            margin: 0 0 20px;
        }

        .folio-home-copy p {
            color: #d9e4ff;
            font-size: 1rem;
            line-height: 1.7;
            max-width: 460px;
        }

        .folio-hero-preview {
            min-height: 230px;
            position: relative;
        }

        .folio-preview-window {
            background:
                linear-gradient(90deg, rgba(20, 89, 200, 0.3), transparent),
                #f8fbff;
            border: 8px solid #3c4961;
            border-radius: 10px;
            box-shadow: 0 18px 40px rgba(0, 0, 0, 0.35);
            height: 210px;
            margin: 12px 72px 0 0;
        }

        .folio-preview-card {
            background: #ffffff;
            border-radius: 8px;
            bottom: 10px;
            box-shadow: 0 14px 34px rgba(0, 0, 0, 0.3);
            color: var(--folio-navy);
            display: grid;
            gap: 8px;
            padding: 18px;
            position: absolute;
            right: 0;
            width: 220px;
        }

        .folio-preview-card span {
            color: var(--folio-muted);
            font-size: 0.88rem;
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

        .folio-project-card {
            margin-bottom: 16px;
            padding: 16px;
            border-radius: 18px;
            box-shadow: 0 8px 24px rgba(15, 41, 94, 0.06);
        }

        .folio-gallery-card {
            border: 1px solid var(--folio-border);
            border-radius: 18px;
            background: #ffffff;
            display: grid;
            grid-template-columns: 180px 1fr;
            gap: 18px;
            margin-bottom: 18px;
            padding: 18px;
            align-items: center;
        }

        .folio-gallery-card .folio-thumbnail {
            min-height: 140px;
        }

        .folio-gallery-card h3 {
            margin: 0 0 8px;
        }

        .folio-detail-header {
            border: 1px solid var(--folio-border);
            border-radius: 18px;
            background: #ffffff;
            padding: 24px;
            margin-bottom: 20px;
        }

        .folio-detail-header .folio-meta {
            align-items: center;
            display: flex;
            gap: 14px;
            flex-wrap: wrap;
            margin-top: 12px;
        }

        .folio-detail-panel {
            border: 1px solid var(--folio-border);
            border-radius: 18px;
            background: #ffffff;
            padding: 20px;
        }

        .folio-detail-grid {
            display: grid;
            grid-template-columns: minmax(0, 1.8fr) minmax(280px, 1fr);
            gap: 24px;
        }

        .folio-detail-links {
            display: grid;
            gap: 10px;
            margin-top: 18px;
        }

        .folio-submit-form {
            display: grid;
            grid-template-columns: minmax(0, 1.6fr) minmax(280px, 1fr);
            gap: 24px;
        }

        .folio-submit-panel {
            border: 1px solid var(--folio-border);
            border-radius: 18px;
            background: #ffffff;
            padding: 20px;
        }

        .folio-submit-form h3,
        .folio-submit-panel h3 {
            margin-top: 0;
        }

        .folio-tags {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin: 8px 0 12px;
        }

        .folio-tag {
            background: #e9f7f5;
            border: 1px solid #bfe7e2;
            border-radius: 999px;
            color: #08776d;
            display: inline-flex;
            font-size: 0.82rem;
            font-weight: 700;
            padding: 4px 9px;
        }

        .folio-detail-meta {
            color: var(--folio-muted);
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            margin: -6px 0 8px;
        }

        .folio-home-card {
            border: 1px solid var(--folio-border);
            border-radius: 8px;
            background: #ffffff;
            min-height: 280px;
            padding: 14px;
        }

        .folio-home-card-compact {
            min-height: 170px;
        }

        .folio-home-card h3 {
            font-size: 1rem;
            margin: 10px 0 8px;
        }

        .folio-home-card p {
            color: var(--folio-muted);
            font-size: 0.88rem;
            min-height: 44px;
        }

        .folio-home-thumb {
            border-radius: 6px;
            height: 130px;
            object-fit: cover;
            width: 100%;
        }

        .folio-home-thumb-fallback {
            align-items: center;
            background: #edf5ff;
            color: var(--folio-blue);
            display: flex;
            font-weight: 900;
            justify-content: center;
        }

        .folio-home-metrics {
            color: var(--folio-muted);
            font-size: 0.82rem;
        }

        .folio-thumbnail {
            align-items: center;
            background: linear-gradient(135deg, #e8f3ff, #dff8f2);
            border: 1px solid var(--folio-border);
            border-radius: 8px;
            color: var(--folio-blue);
            display: flex;
            font-weight: 800;
            height: 170px;
            justify-content: center;
            width: 100%;
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

        @media (max-width: 860px) {
            .folio-topbar {
                align-items: flex-start;
                flex-direction: column;
                gap: 6px;
            }

            .folio-home-hero {
                grid-template-columns: 1fr;
                padding: 34px 24px;
            }

            .folio-home-copy h1 {
                font-size: 2.2rem;
            }

            .folio-hero-preview {
                display: none;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
