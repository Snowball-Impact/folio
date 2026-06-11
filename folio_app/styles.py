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
            min-width: 0;
        }

        .folio-nav-toggle {
            display: none;
        }

        .folio-hamburger {
            align-items: center;
            background: transparent;
            border: 1px solid rgba(255, 255, 255, 0.45);
            border-radius: 8px;
            color: #ffffff;
            cursor: pointer;
            display: inline-flex;
            font-size: 1.1rem;
            height: 42px;
            justify-content: center;
            margin-left: auto;
            padding: 0 14px;
        }

        .folio-nav {
            align-items: center;
            background: rgba(8, 20, 43, 0.98);
            border: 1px solid rgba(255, 255, 255, 0.14);
            border-radius: 8px;
            box-shadow: 0 18px 38px rgba(5, 15, 35, 0.24);
            display: none;
            flex-direction: column;
            gap: 8px;
            justify-content: flex-end;
            margin-left: auto;
            min-width: 132px;
            padding: 6px;
            position: absolute;
            right: 24px;
            top: 62px;
            z-index: 1000;
        }

        .folio-nav-link {
            color: rgba(255, 255, 255, 0.92) !important;
            font-weight: 700;
            text-decoration: none !important;
            padding: 9px 11px;
            border-radius: 6px;
            transition: background 0.2s ease, color 0.2s ease;
            width: 100%;
        }

        .folio-nav-link:visited,
        .folio-nav-link:active,
        .folio-nav-link:focus,
        .folio-nav-link:hover {
            text-decoration: none !important;
        }

        .folio-nav-link:hover,
        .folio-nav-link-active {
            background: rgba(255, 255, 255, 0.16);
            color: rgba(255, 255, 255, 1) !important;
        }

        .folio-nav-toggle:checked + .folio-hamburger + .folio-nav {
            display: flex;
        }

        .folio-nav-link-logout {
            border: 1px solid var(--folio-border);
        }

        @media (max-width: 860px) {
            .folio-topbar {
                padding: 16px 20px;
            }

            .folio-nav {
                margin-left: 0;
                min-width: min(150px, calc(100vw - 40px));
                right: 20px;
                top: 60px;
            }
        }

        .folio-brand {
            font-size: 1.8rem;
            font-weight: 900;
        }

        .folio-tagline {
            color: #b7c6e7;
            font-size: 0.95rem;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
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
            background: #ffffff !important;
            color: var(--folio-navy) !important;
            border: 1px solid var(--folio-border) !important;
        }

        .stTextInput>div>div>input::placeholder {
            color: var(--folio-muted) !important;
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
            border-radius: 0 !important;
            color: #ffffff;
            display: grid;
            gap: 18px;
            grid-template-columns: minmax(0, 1fr) minmax(300px, 0.9fr);
            min-height: 290px;
            padding: 32px 52px;
            margin-top: 0;
        }

        .folio-home-copy h1 {
            color: #ffffff;
            font-size: 2.6rem;
            line-height: 1.14;
            margin: 0 0 12px;
            max-width: 680px;
            text-wrap: balance;
            word-break: keep-all;
        }

        .folio-home-copy h1 span {
            display: block;
        }

        .folio-home-copy p {
            color: #d9e4ff;
            font-size: 0.98rem;
            line-height: 1.55;
            max-width: 520px;
            word-break: keep-all;
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
            border-radius: 0 !important;
            background: #ffffff;
            padding: 28px 30px;
            margin-bottom: 20px;
        }

        .folio-hero h1 {
            line-height: 1.22;
            margin: 0 0 10px;
            max-width: 760px;
            text-wrap: balance;
            word-break: keep-all;
        }

        .folio-hero p {
            line-height: 1.65;
            margin: 0;
            max-width: 760px;
            word-break: keep-all;
        }

        .folio-back-link,
        .folio-back-link:visited,
        .folio-back-link:hover,
        .folio-back-link:active {
            color: var(--folio-muted) !important;
            display: inline-flex;
            font-size: 0.92rem;
            font-weight: 700;
            margin: 4px 0 12px;
            text-decoration: none !important;
        }

        .folio-back-link:hover {
            color: var(--folio-blue) !important;
        }

        .folio-back-link-bottom {
            background: #ffffff;
            border: 1px solid var(--folio-blue);
            border-radius: 999px;
            color: var(--folio-blue) !important;
            margin: 28px 0 6px;
            padding: 12px 18px;
        }

        .folio-back-link-bottom:hover {
            background: #edf4ff;
            color: var(--folio-navy) !important;
        }

        .folio-attachment-links {
            margin-top: -12px;
        }

        .folio-attachment-links h3 {
            margin-top: 0;
        }

        .folio-attachment-links-bottom {
            margin-top: 24px;
        }

        .folio-detail-hero {
            align-items: flex-end;
            display: flex;
            gap: 24px;
            justify-content: space-between;
        }

        .folio-detail-hero h1 {
            margin-bottom: 8px;
            max-width: 760px;
            word-break: keep-all;
        }

        .folio-detail-hero-meta {
            align-items: flex-end;
            display: flex;
            flex-direction: column;
            gap: 2px;
            text-align: right;
        }

        .folio-detail-hero-meta .folio-tags {
            justify-content: flex-end;
            margin: 0 0 4px;
        }

        .folio-detail-hero-meta .folio-detail-meta {
            justify-content: flex-end;
            margin: 0;
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

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.folio-auth-card-header) {
            background: transparent;
            border: 0;
            border-radius: 0;
            box-shadow: none;
            margin: 0 auto;
            max-width: 440px;
            padding: 0;
            width: min(440px, calc(100vw - 48px));
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.folio-auth-card-signup) {
            max-width: 520px;
            width: min(520px, calc(100vw - 48px));
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.folio-auth-form-card):not(:has(.folio-auth-card-header)) {
            background: #ffffff;
            border: 1px solid rgba(216, 227, 247, 0.96);
            border-radius: 0 0 8px 8px;
            border-top: 0;
            box-shadow: 0 18px 42px rgba(15, 41, 94, 0.08);
            padding: 24px;
        }

        .folio-auth-form-card {
            height: 0;
            overflow: hidden;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.folio-auth-form-card) .stTextInput div[data-baseweb="input"] {
            align-items: center;
            background: #ffffff !important;
            border: 1px solid var(--folio-border) !important;
            border-radius: 999px !important;
            box-shadow: none !important;
            display: flex;
            min-height: 48px;
            overflow: hidden;
            padding: 0;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.folio-auth-form-card) .stTextInput div[data-baseweb="input"] input {
            background: transparent !important;
            border: 0 !important;
            box-shadow: none !important;
            flex: 1;
            min-height: 46px;
            padding: 12px 16px !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.folio-auth-form-card) .stTextInput:has(input[type="password"]) button {
            align-items: center;
            background: transparent !important;
            border: 0 !important;
            border-radius: 999px;
            box-shadow: none !important;
            color: var(--folio-muted) !important;
            display: inline-flex;
            flex: 0 0 38px;
            height: 38px;
            justify-content: center;
            margin: 0 6px 0 0;
            min-height: 38px;
            padding: 0;
            position: static;
            transform: none;
            width: 38px;
            z-index: 2;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.folio-auth-card-header) .stTextInput {
            margin-bottom: 4px;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.folio-auth-card-header) .stAlert {
            margin: 6px 0 12px;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.folio-auth-card-header) .stAlert [data-testid="stMarkdownContainer"] p {
            font-size: 0.9rem;
            line-height: 1.5;
            word-break: keep-all;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.folio-auth-card-header) details {
            border: 1px solid var(--folio-border);
            border-radius: 8px;
            margin-top: 16px;
            padding: 2px 10px;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.folio-auth-card-header) details summary {
            color: var(--folio-navy);
            font-weight: 800;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.folio-auth-card-header) hr {
            margin: 18px 0;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.folio-auth-card-header) .stButton>button,
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.folio-auth-card-header) .stFormSubmitButton>button {
            background: var(--folio-blue);
            border: 1px solid var(--folio-blue);
            box-shadow: 0 10px 22px rgba(20, 89, 200, 0.18);
            color: #ffffff;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.folio-auth-card-header) .stButton>button:hover,
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.folio-auth-card-header) .stFormSubmitButton>button:hover {
            background: #0d47a8;
            border-color: #0d47a8;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.folio-auth-card-header) .stButton>button:disabled,
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.folio-auth-card-header) .stFormSubmitButton>button:disabled {
            background: #d8e3f7;
            border-color: #d8e3f7;
            box-shadow: none;
            color: #7182a3;
        }

        .folio-auth-card-header {
            background: linear-gradient(135deg, #08142b, #0b1f3f 72%, #0d314f);
            border: 1px solid #0b1f3f;
            border-radius: 0;
            margin-bottom: 0;
            padding: 22px 24px;
            text-align: left;
        }

        .folio-auth-card-header h2 {
            color: #ffffff;
            font-size: 1.6rem;
            line-height: 1.25;
            margin: 0 0 8px;
            word-break: keep-all;
        }

        .folio-auth-card-header p {
            color: #cbd8f5;
            font-size: 0.92rem;
            line-height: 1.55;
            margin: 0;
            word-break: keep-all;
        }

        .folio-auth-switch,
        .folio-auth-switch:visited,
        .folio-auth-switch:active {
            align-items: center;
            background: #f8fbff;
            border: 1px solid #c8d8f3;
            border-radius: 999px;
            color: var(--folio-blue) !important;
            display: flex;
            font-weight: 800;
            justify-content: center;
            margin-top: 14px;
            min-height: 44px;
            padding: 11px 14px;
            text-decoration: none !important;
        }

        .folio-auth-switch:hover {
            background: #e8f1ff;
            color: var(--folio-navy) !important;
            text-decoration: none !important;
        }

        div[data-testid="stForm"] {
            background: transparent;
            border: 0;
            padding: 0;
        }

        div[data-testid="stForm"] .stButton button,
        div[data-testid="stForm"] button {
            margin-top: 6px;
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

        .folio-gallery-content {
            align-self: stretch;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            min-width: 0;
        }

        .folio-gallery-footer {
            align-items: flex-end;
            display: flex;
            flex-direction: column;
            gap: 2px;
            justify-content: flex-end;
            text-align: right;
        }

        .folio-gallery-footer .folio-tags {
            justify-content: flex-end;
            margin: 8px 0 4px;
        }

        .folio-gallery-footer .folio-detail-meta {
            justify-content: flex-end;
            margin: 0;
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
            transition: border-color 0.16s ease, box-shadow 0.16s ease, transform 0.16s ease;
        }

        .folio-card-link,
        .folio-card-link:visited,
        .folio-card-link:active {
            color: inherit;
            display: block;
            text-decoration: none !important;
        }

        .folio-card-link:hover,
        .folio-card-link:hover *,
        .folio-card-link *,
        .folio-card-link:visited * {
            color: inherit;
            text-decoration: none !important;
        }

        .folio-card-link:hover .folio-home-card,
        .folio-card-link:hover .folio-gallery-card {
            border-color: rgba(20, 89, 200, 0.45);
            box-shadow: 0 14px 30px rgba(15, 41, 94, 0.1);
            transform: translateY(-2px);
        }

        .folio-card-link .folio-home-card h3,
        .folio-card-link .folio-gallery-card h3 {
            color: var(--folio-navy);
        }

        .folio-card-link .folio-home-card p,
        .folio-card-link .folio-gallery-card p,
        .folio-card-link .folio-home-metrics,
        .folio-card-link .folio-detail-meta {
            color: var(--folio-muted);
        }

        .folio-card-link .folio-tag {
            color: #08776d;
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
                align-items: center;
                flex-direction: row;
                gap: 12px;
            }

            .folio-home-hero {
                grid-template-columns: 1fr;
                min-height: 220px;
                padding: 28px 22px;
            }

            .folio-home-copy h1 {
                font-size: 1.85rem;
            }

            .folio-home-copy p,
            .folio-hero p,
            .folio-auth-card-header p {
                line-height: 1.6;
            }

            .folio-hero-preview {
                display: none;
            }

            .folio-detail-hero {
                align-items: flex-start;
                flex-direction: column;
            }

            .folio-detail-hero-meta {
                align-items: flex-start;
                text-align: left;
            }

            .folio-detail-hero-meta .folio-tags,
            .folio-detail-hero-meta .folio-detail-meta {
                justify-content: flex-start;
            }

            .folio-gallery-card {
                grid-template-columns: 1fr;
            }

            .folio-gallery-footer {
                align-items: flex-start;
                text-align: left;
            }

            .folio-gallery-footer .folio-tags,
            .folio-gallery-footer .folio-detail-meta {
                justify-content: flex-start;
            }

            div[data-testid="stVerticalBlockBorderWrapper"]:has(.folio-auth-card-header) {
                border-radius: 0;
                box-shadow: none;
                margin-top: 0;
                padding: 0;
                width: min(100%, calc(100vw - 28px));
            }

            div[data-testid="stVerticalBlockBorderWrapper"]:has(.folio-auth-form-card):not(:has(.folio-auth-card-header)) {
                padding: 18px;
            }

            .folio-auth-card-header {
                margin-bottom: 0;
                padding: 18px;
            }

            .folio-auth-card-header h2 {
                font-size: 1.35rem;
            }

            .folio-auth-card-header p {
                font-size: 0.9rem;
            }

            .stTextInput>div>div>input {
                min-height: 46px;
                padding: 12px 14px !important;
            }

            .stButton>button {
                min-height: 46px;
            }

            div[data-testid="stVerticalBlockBorderWrapper"]:has(.folio-auth-card-header) .stFormSubmitButton>button {
                min-height: 46px;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
