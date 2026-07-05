import streamlit as st


def apply_global_styles() -> None:
    st.markdown(
        """
        <style>
        /* ── Design Tokens ── */
        :root {
            --folio-navy:   #0b1f3f;
            --folio-blue:   #1459c8;
            --folio-mint:   #0a9485;
            --folio-bg:     #f4f7fd;
            --folio-surface:#ffffff;
            --folio-border: #dce5f7;
            --folio-muted:  #5c6f8a;
            --folio-subtle: #eef3fd;
        }

        /* ── Global ── */
        .stApp {
            background: var(--folio-bg);
            font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }

        section[data-testid="stSidebar"],
        header[data-testid="stHeader"],
        footer[data-testid="stFooter"] {
            display: none;
        }

        /* Hide EncryptedCookieManager's invisible sync iframe */
        .st-key-CookieManager-sync_cookies {
            display: none !important;
        }

        .block-container {
            max-width: 1280px;
            padding-top: 0 !important;
        }

        [data-testid="stMainBlockContainer"] {
            padding-top: 0 !important;
        }

        section.stMain {
            padding-top: 0 !important;
        }

        h1, h2, h3 {
            color: var(--folio-navy);
            letter-spacing: -0.01em;
        }

        /* ── Header (light) ── */
        .st-key-folio_header {
            --text-color: rgba(200, 215, 255, 0.85);
            background: var(--folio-navy) !important;
            border: none !important;
            border-radius: 12px !important;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.22) !important;
            color: rgba(200, 215, 255, 0.85) !important;
            margin-bottom: 0 !important;
            padding: 0 20px !important;
            position: sticky;
            top: 0;
            z-index: 999;
        }

        /* Zero out ALL internal gaps and padding inside the header */
        .st-key-folio_header [data-testid="stVerticalBlock"],
        .st-key-folio_header [data-testid="stElementContainer"],
        .st-key-folio_header [data-testid="stMarkdown"] {
            gap: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        .st-key-folio_header [data-testid="stHorizontalBlock"] {
            align-items: center;
            gap: 0 !important;
            min-height: 52px;
            padding: 0 !important;
        }

        /* Force button text visible on dark header — Streamlit wraps button text in p/div */
        .st-key-folio_header button p,
        .st-key-folio_header button div,
        .st-key-folio_header button span {
            color: inherit !important;
        }

        /* Zero out inner column wrappers inside the header */
        .st-key-folio_header [data-testid="stVerticalBlockBorderWrapper"] {
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            padding: 0 !important;
        }

        .st-key-folio_header [data-testid="stVerticalBlockBorderWrapper"] > div {
            padding: 0 !important;
        }

        /* Header nav buttons (dark bg) */
        .st-key-folio_header .stButton > button {
            background: transparent !important;
            border: none !important;
            border-radius: 8px !important;
            color: rgba(200, 215, 255, 0.75) !important;
            font-size: 0.86rem !important;
            font-weight: 600 !important;
            min-height: 34px !important;
            padding: 5px 10px !important;
            transform: none !important;
            transition: background 0.14s, color 0.14s !important;
        }

        .st-key-folio_header .stButton > button:hover {
            background: rgba(255, 255, 255, 0.1) !important;
            color: #ffffff !important;
            transform: none !important;
        }

        /* Active nav button — rendered as disabled, styled as selected */
        .st-key-folio_header .stButton > button:disabled {
            background: rgba(255, 255, 255, 0.12) !important;
            border: none !important;
            color: #ffffff !important;
            cursor: default !important;
            font-weight: 700 !important;
            opacity: 1 !important;
        }

        /* FOLIO brand button — must come AFTER general button CSS to override */
        .st-key-folio_header .st-key-nav_brand_home button {
            background: transparent !important;
            border: none !important;
            color: #ffffff !important;
            font-size: 1.5rem !important;
            font-weight: 900 !important;
            letter-spacing: -0.04em !important;
            line-height: 1 !important;
            min-height: unset !important;
            padding: 6px 0 !important;
        }

        .st-key-folio_header .st-key-nav_brand_home button p,
        .st-key-folio_header .st-key-nav_brand_home button div,
        .st-key-folio_header .st-key-nav_brand_home button span {
            font-weight: 900 !important;
        }

        .st-key-folio_header .st-key-nav_brand_home button:hover {
            background: transparent !important;
            color: rgba(180, 205, 255, 0.88) !important;
            transform: none !important;
        }

        /* Direct Login button (non-logged-in state) */
        .st-key-folio_header .st-key-nav_Login,
        .st-key-folio_header .st-key-nav_Login .stButton {
            margin-left: auto !important;
            width: fit-content !important;
        }

        .st-key-folio_header .st-key-nav_Login button {
            background: transparent !important;
            border: none !important;
            border-radius: 0 !important;
            color: rgba(225, 234, 255, 0.86) !important;
            font-size: 0.88rem !important;
            font-weight: 700 !important;
            min-height: 34px !important;
            padding: 5px 2px !important;
            position: relative;
            width: auto !important;
        }

        .st-key-folio_header .st-key-nav_Login button:hover {
            background: transparent !important;
            color: #ffffff !important;
            transform: none !important;
        }

        .st-key-folio_header .st-key-nav_Login button::after {
            background: rgba(255, 255, 255, 0.72);
            bottom: 3px;
            content: "";
            height: 1px;
            left: 50%;
            position: absolute;
            transform: translateX(-50%) scaleX(0);
            transition: transform 0.16s ease;
            width: calc(100% - 4px);
        }

        .st-key-folio_header .st-key-nav_Login button:hover::after {
            transform: translateX(-50%) scaleX(1);
        }

        /* Menu popover trigger button in header */
        .st-key-folio_header [data-testid="stPopover"] {
            margin-left: auto !important;
            width: 34px !important;
        }

        .st-key-folio_header [data-testid="stPopover"] > button,
        .st-key-folio_header button[data-testid="stPopoverButton"],
        .st-key-folio_header [data-testid="stPopoverButton"] > button {
            background: transparent !important;
            border: none !important;
            border-radius: 0 !important;
            box-shadow: none !important;
            color: #ffffff !important;
            font-size: 1.3rem !important;
            font-weight: 400 !important;
            min-height: 34px !important;
            min-width: 34px !important;
            padding: 4px 0 !important;
            transform: none !important;
            transition: color 0.15s ease, opacity 0.15s ease !important;
            width: 34px !important;
        }

        .st-key-folio_header [data-testid="stPopover"] > button *,
        .st-key-folio_header button[data-testid="stPopoverButton"] *,
        .st-key-folio_header [data-testid="stPopoverButton"] > button * {
            color: #ffffff !important;
            fill: currentColor !important;
        }

        .st-key-folio_header [data-testid="stPopover"] > button:hover,
        .st-key-folio_header button[data-testid="stPopoverButton"]:hover,
        .st-key-folio_header [data-testid="stPopoverButton"] > button:hover {
            background: transparent !important;
            color: #ffffff !important;
            opacity: 1;
        }

        /* Hide dropdown arrow from popover trigger in header */
        .st-key-folio_header [data-testid="stPopoverButton"] > div:last-child {
            display: none !important;
        }

        /* ── Home Hero (light) ── */
        .folio-home-hero {
            align-items: center;
            background: var(--folio-surface);
            border: 1px solid var(--folio-border);
            border-radius: 16px;
            color: var(--folio-navy);
            display: grid;
            gap: 24px;
            grid-template-columns: minmax(0, 1fr) minmax(260px, 0.8fr);
            margin-top: 16px;
            min-height: 248px;
            padding: 52px 28px 44px;
        }

        .folio-home-eyebrow {
            color: var(--folio-blue);
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.12em;
            margin-bottom: 14px;
            text-transform: uppercase;
        }

        .folio-home-copy h1 {
            color: var(--folio-navy);
            font-size: 2.6rem;
            font-weight: 800;
            line-height: 1.13;
            margin: 0 0 16px;
            text-wrap: balance;
            word-break: keep-all;
        }

        .folio-home-copy h1 em {
            color: var(--folio-blue);
            font-style: normal;
        }

        .folio-home-copy p {
            color: var(--folio-muted);
            font-size: 0.98rem;
            line-height: 1.65;
            margin: 0;
            max-width: 460px;
            word-break: keep-all;
        }

        .folio-hero-preview {
            align-items: center;
            display: flex;
            justify-content: flex-end;
        }

        .folio-hero-preview-image {
            border: 1px solid var(--folio-border);
            border-radius: 14px;
            box-shadow: 0 16px 48px rgba(11, 31, 63, 0.11);
            display: block;
            height: auto;
            max-height: 230px;
            max-width: 100%;
            object-fit: cover;
            width: min(100%, 400px);
        }

        /* ── Page Hero (sub-pages) ── */
        .folio-page-hero {
            align-items: center;
            background: var(--folio-surface);
            border: 1px solid var(--folio-border);
            border-radius: 16px;
            display: grid;
            gap: 28px;
            grid-template-columns: minmax(0, 1fr) minmax(300px, 0.78fr);
            margin-top: 16px;
            margin-bottom: 28px;
            min-height: 230px;
            overflow: hidden;
            padding: 34px 28px;
        }

        .folio-page-hero-copy {
            padding-left: 2px;
        }

        .folio-page-hero-eyebrow {
            color: var(--folio-blue);
            font-size: 0.82rem;
            font-weight: 800;
            letter-spacing: 0.12em;
            margin-bottom: 12px;
            text-transform: uppercase;
        }

        .folio-page-hero h1 {
            color: var(--folio-navy);
            font-size: 2.15rem;
            font-weight: 800;
            line-height: 1.16;
            margin: 0 0 12px;
            word-break: keep-all;
        }

        .folio-page-hero p {
            color: var(--folio-muted);
            font-size: 0.98rem;
            line-height: 1.65;
            margin: 0;
            max-width: 480px;
            word-break: keep-all;
        }

        .folio-page-hero-visual {
            align-items: center;
            display: flex;
            justify-content: flex-end;
        }

        .folio-page-hero-visual img {
            border: 1px solid rgba(20, 89, 200, 0.12);
            border-radius: 14px;
            box-shadow: 0 14px 38px rgba(11, 31, 63, 0.12);
            display: block;
            height: 176px;
            object-fit: cover;
            width: min(100%, 390px);
        }

        .folio-hero {
            background: var(--folio-surface);
            border-bottom: 1px solid var(--folio-border);
            margin-bottom: 28px;
            padding: 28px 0 22px;
        }

        .folio-page-hero-dark {
            background: linear-gradient(135deg, #071126, #0f1f3d 70%);
            border: none;
            color: #ffffff;
            margin-bottom: 28px;
            padding: 34px 28px;
        }

        .folio-page-hero-dark h1 {
            color: #ffffff;
            font-size: 2rem;
            font-weight: 800;
            line-height: 1.2;
            margin: 0 0 10px;
            word-break: keep-all;
        }

        .folio-page-hero-dark p,
        .folio-page-hero-dark .folio-muted {
            color: rgba(210, 225, 255, 0.85);
            font-size: 0.98rem;
            line-height: 1.58;
            margin: 0;
            word-break: keep-all;
        }

        /* ── Global Buttons ── */
        .stButton > button {
            background: var(--folio-surface);
            border: 1px solid var(--folio-border);
            border-radius: 10px;
            color: var(--folio-navy);
            font-weight: 600;
            min-height: 40px;
            padding: 0 18px;
            transition: background 0.13s, border-color 0.13s, transform 0.13s;
        }

        .stButton > button:hover {
            background: var(--folio-subtle);
            border-color: #b8d0f0;
            color: var(--folio-blue);
            transform: translateY(-1px);
        }

        /* ── Form Inputs ── */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea {
            background: var(--folio-surface) !important;
            border: 1px solid var(--folio-border) !important;
            border-radius: 10px !important;
            color: var(--folio-navy) !important;
            padding: 12px 16px !important;
        }

        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus {
            border-color: var(--folio-blue) !important;
            box-shadow: 0 0 0 3px rgba(20, 89, 200, 0.1) !important;
        }

        .stTextInput > div > div > input::placeholder,
        .stTextArea > div > div > textarea::placeholder {
            color: var(--folio-muted) !important;
        }

        .stTextInput > div > label,
        .stTextArea > div > label,
        .stSelectbox > div > label {
            color: var(--folio-navy);
            font-weight: 700;
        }

        .stTextInput > div > div > label,
        .stTextArea > div > div > label,
        .stSelectbox > div > div > label {
            display: none;
        }

        /* ── Browse Panel ── */
        .folio-search-container {
            align-items: flex-end;
            display: flex;
            justify-content: space-between;
            margin-bottom: 18px;
        }

        .folio-search-title {
            color: var(--folio-navy);
            font-size: 1.3rem;
            font-weight: 800;
            letter-spacing: -0.02em;
        }

        .folio-search-subtitle {
            color: var(--folio-muted);
            font-size: 0.85rem;
            line-height: 1.45;
            margin-top: 3px;
            word-break: keep-all;
        }

        .folio-search-count {
            color: var(--folio-muted);
            font-size: 0.88rem;
            font-weight: 700;
            padding-bottom: 2px;
        }

        .st-key-folio_browse_panel {
            background: #eaf1ff !important;
            border: none !important;
            border-radius: 12px !important;
            box-shadow: none !important;
            margin: 28px 0 24px !important;
            padding: 26px 28px 24px !important;
        }

        .st-key-folio_browse_panel > [data-testid="stVerticalBlock"] {
            gap: 0 !important;
        }

        .st-key-folio_browse_panel .stTextInput > div > div > input {
            background: var(--folio-surface) !important;
            border: 1px solid var(--folio-border) !important;
            border-radius: 10px !important;
            min-height: 46px;
            padding: 12px 16px !important;
        }

        .st-key-folio_browse_panel .stTextInput > div > div > input:focus {
            background: var(--folio-surface) !important;
            border-color: var(--folio-blue) !important;
            box-shadow: 0 0 0 3px rgba(20, 89, 200, 0.1) !important;
        }

        .st-key-folio_browse_panel [data-testid="stHorizontalBlock"] {
            align-items: flex-end;
            gap: 14px !important;
        }

        .st-key-folio_browse_panel .stButton > button {
            background: var(--folio-surface);
            border: 1px solid var(--folio-border);
            border-radius: 8px;
            color: var(--folio-muted);
            font-size: 0.84rem;
            font-weight: 600;
            min-height: 38px;
            padding: 0 14px;
        }

        .st-key-folio_browse_panel .stFormSubmitButton > button[kind="primaryFormSubmit"] {
            background: var(--folio-blue) !important;
            border-color: var(--folio-blue) !important;
            color: #ffffff !important;
            min-height: 46px !important;
        }

        .st-key-folio_browse_panel .stFormSubmitButton > button[kind="primaryFormSubmit"]:hover {
            background: #0e42a8 !important;
            border-color: #0e42a8 !important;
            color: #ffffff !important;
        }

        .st-key-folio_browse_panel .stFormSubmitButton > button[kind="secondaryFormSubmit"] {
            background: transparent !important;
            border-color: transparent !important;
            color: var(--folio-muted) !important;
            padding-inline: 8px !important;
        }

        .st-key-folio_browse_panel .stButton > button:hover {
            background: var(--folio-subtle);
            border-color: #b8d0f0;
            color: var(--folio-blue);
        }

        /* ── Project Cards (grid) ── */
        .folio-home-card {
            background: var(--folio-surface);
            border: 1px solid var(--folio-border);
            border-radius: 14px;
            display: flex;
            flex-direction: column;
            min-height: 280px;
            padding: 16px 16px 14px;
            transition: border-color 0.16s, box-shadow 0.16s, transform 0.16s;
        }

        .folio-home-card-compact {
            min-height: 160px;
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
            border-color: rgba(20, 89, 200, 0.4);
            box-shadow: 0 8px 28px rgba(11, 31, 63, 0.1);
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
            color: #0a7a72;
        }

        .folio-home-card h3 {
            color: var(--folio-navy);
            font-size: 0.94rem;
            font-weight: 700;
            line-height: 1.38;
            margin: 12px 0 6px;
            word-break: keep-all;
        }

        .folio-home-card p {
            color: var(--folio-muted);
            font-size: 0.85rem;
            line-height: 1.55;
            margin: 0;
            min-height: 40px;
            word-break: keep-all;
        }

        .folio-home-card .folio-tags {
            margin: 10px 0 0;
        }

        .folio-home-thumb {
            border-radius: 8px;
            height: 124px;
            object-fit: cover;
            width: 100%;
        }

        .folio-home-thumb-fallback {
            align-items: center;
            background: linear-gradient(135deg, #eef3fd 0%, #e4efff 100%);
            border-radius: 8px;
            color: var(--folio-blue);
            display: flex;
            font-size: 0.72rem;
            font-weight: 700;
            height: 124px;
            justify-content: center;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            width: 100%;
        }

        .folio-home-metrics {
            color: var(--folio-muted);
            font-size: 0.8rem;
            margin-top: auto;
            padding-top: 12px;
        }

        /* ── Gallery Card (single featured result) ── */
        .folio-gallery-card {
            align-items: center;
            background: var(--folio-surface);
            border: 1px solid var(--folio-border);
            border-radius: 16px;
            display: grid;
            gap: 20px;
            grid-template-columns: 200px 1fr;
            margin-bottom: 18px;
            padding: 20px;
        }

        .folio-gallery-content {
            align-self: stretch;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            min-width: 0;
        }

        .folio-gallery-card h3 {
            color: var(--folio-navy);
            font-size: 1.2rem;
            font-weight: 700;
            margin: 0 0 8px;
            word-break: keep-all;
        }

        .folio-gallery-footer {
            align-items: flex-end;
            display: flex;
            flex-direction: column;
            gap: 4px;
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

        .folio-thumbnail {
            align-items: center;
            background: linear-gradient(135deg, #eef3fd 0%, #e4efff 100%);
            border: 1px solid var(--folio-border);
            border-radius: 10px;
            color: var(--folio-blue);
            display: flex;
            font-size: 0.76rem;
            font-weight: 700;
            height: 160px;
            justify-content: center;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            width: 100%;
        }

        .folio-featured-result .folio-gallery-card {
            grid-template-columns: 220px 1fr;
            min-height: 200px;
        }

        .folio-featured-result .folio-thumbnail {
            height: 160px;
            min-height: 160px;
        }

        .folio-featured-result .folio-gallery-card h3 {
            font-size: 1.25rem;
        }

        /* ── Tags ── */
        .folio-tags {
            display: flex;
            flex-wrap: wrap;
            gap: 5px;
            margin: 8px 0 10px;
        }

        .folio-tag {
            background: #eaf5f3;
            border: 1px solid #c0e5e0;
            border-radius: 999px;
            color: #0a7a72;
            display: inline-flex;
            font-size: 0.76rem;
            font-weight: 700;
            padding: 3px 9px;
        }

        /* ── Detail Meta ── */
        .folio-detail-meta {
            color: var(--folio-muted);
            display: flex;
            flex-wrap: wrap;
            font-size: 0.84rem;
            gap: 10px;
            margin: -4px 0 6px;
        }

        /* ── Muted helper ── */
        .folio-muted {
            color: var(--folio-muted);
        }

        /* ── Project Detail Hero ── */
        .folio-hero.folio-detail-hero-wrap {
            border-bottom: 1px solid var(--folio-border);
            margin-bottom: 24px;
            padding: 20px 0;
        }

        .folio-detail-hero {
            align-items: flex-end;
            display: flex;
            gap: 24px;
            justify-content: space-between;
        }

        .folio-detail-hero h1 {
            font-size: 1.9rem;
            font-weight: 800;
            margin-bottom: 6px;
            max-width: 760px;
            word-break: keep-all;
        }

        .folio-detail-hero-meta {
            align-items: flex-end;
            display: flex;
            flex-direction: column;
            gap: 4px;
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

        .st-key-detail_like_action {
            display: flex;
            justify-content: flex-end;
            margin: -18px 0 22px;
        }

        .st-key-detail_like_action button {
            border-radius: 999px;
            min-height: 38px;
            padding: 0 16px;
        }

        /* ── Auth Cards ── */
        .st-key-folio_auth_shell {
            background: transparent;
            border: 0;
            border-radius: 0;
            box-sizing: border-box;
            box-shadow: none;
            margin: 0 auto;
            max-width: 440px;
            padding: 0;
            width: min(440px, calc(100vw - 48px));
        }

        .st-key-folio_auth_shell:has(.folio-auth-card-signup) {
            max-width: 520px;
            width: min(520px, calc(100vw - 48px));
        }

        .st-key-folio_auth_form {
            background: var(--folio-surface);
            border: 1px solid var(--folio-border);
            border-radius: 0 0 14px 14px;
            border-top: 0;
            box-sizing: border-box;
            box-shadow: 0 16px 40px rgba(11, 31, 63, 0.08);
            padding: 24px;
        }

        /* Auth card inputs */
        .st-key-folio_auth_form .stTextInput div[data-baseweb="input"] {
            align-items: center;
            background: var(--folio-surface) !important;
            border: 1px solid var(--folio-border) !important;
            border-radius: 10px !important;
            box-shadow: none !important;
            display: flex;
            min-height: 48px;
            overflow: hidden;
            padding: 0;
        }

        .st-key-folio_auth_form .stTextInput div[data-baseweb="input"] input {
            background: var(--folio-surface) !important;
            border: 0 !important;
            box-shadow: none !important;
            flex: 1;
            min-height: 46px;
            padding: 12px 16px !important;
        }

        .st-key-folio_auth_form .stTextInput input:-webkit-autofill,
        .st-key-folio_auth_form .stTextInput input:-webkit-autofill:hover,
        .st-key-folio_auth_form .stTextInput input:-webkit-autofill:focus {
            -webkit-box-shadow: 0 0 0 1000px #ffffff inset !important;
            -webkit-text-fill-color: var(--folio-navy) !important;
            caret-color: var(--folio-navy);
        }

        .st-key-folio_auth_form .stTextInput div[data-testid="InputInstructions"] {
            display: none !important;
        }

        .st-key-folio_auth_form .st-key-login_to_signup button {
            width: calc(100% - 48px) !important;
        }

        .st-key-folio_auth_form .stTextInput:has(input[type="password"]) div[data-baseweb="input"],
        .st-key-folio_auth_form .stTextInput:has(input[type="password"]) div[data-baseweb="input"] > div {
            background: var(--folio-surface) !important;
            width: 100%;
        }

        .st-key-folio_auth_form .stTextInput:has(input[type="password"]) div[data-baseweb="input"]:focus-within,
        .st-key-folio_auth_form .stTextInput:has(input[type="password"]) div[data-baseweb="input"]:has(input:not(:placeholder-shown)) {
            background: var(--folio-surface) !important;
        }

        .st-key-folio_auth_form .stTextInput:has(input[type="password"]) div[data-baseweb="input"]:focus-within *,
        .st-key-folio_auth_form .stTextInput:has(input[type="password"]) div[data-baseweb="input"]:has(input:not(:placeholder-shown)) * {
            background-color: transparent !important;
        }

        .st-key-folio_auth_form .stTextInput:has(input[type="password"]) button {
            align-items: center;
            align-self: stretch;
            background: transparent !important;
            border: 0 !important;
            border-radius: 8px;
            box-shadow: none !important;
            color: var(--folio-muted) !important;
            display: inline-flex;
            flex: 0 0 38px;
            height: auto;
            justify-content: center;
            margin: 0 6px 0 0;
            min-height: 46px;
            padding: 0;
            position: static;
            transform: none;
            width: 38px;
        }

        .st-key-folio_auth_shell .stTextInput {
            margin-bottom: 4px;
        }

        .st-key-folio_auth_shell .stAlert {
            margin: 6px 0 12px;
        }

        .st-key-folio_auth_shell .stAlert [data-testid="stMarkdownContainer"] p {
            font-size: 0.88rem;
            line-height: 1.5;
            word-break: keep-all;
        }

        .st-key-folio_auth_shell details {
            border: 1px solid var(--folio-border);
            border-radius: 8px;
            margin-top: 16px;
            padding: 2px 10px;
        }

        .st-key-folio_auth_shell details summary {
            color: var(--folio-navy);
            font-weight: 700;
        }

        .st-key-folio_auth_shell hr {
            margin: 18px 0;
        }

        /* Auth submit buttons */
        .st-key-folio_auth_shell .stButton > button,
        .st-key-folio_auth_shell .stFormSubmitButton > button {
            background: var(--folio-blue);
            border: 1px solid var(--folio-blue);
            border-radius: 10px;
            box-shadow: 0 6px 18px rgba(20, 89, 200, 0.2);
            color: #ffffff;
            font-weight: 700;
            min-height: 44px;
            padding: 0 1.2rem;
        }

        .st-key-folio_auth_shell .stButton > button:hover,
        .st-key-folio_auth_shell .stFormSubmitButton > button:hover {
            background: #0e42a8;
            border-color: #0e42a8;
            transform: none;
        }

        .st-key-folio_auth_shell .stButton > button:disabled,
        .st-key-folio_auth_shell .stFormSubmitButton > button:disabled {
            background: #d4e0f8;
            border-color: #d4e0f8;
            box-shadow: none;
            color: #7a8fb0;
        }

        .folio-auth-card-header {
            background: linear-gradient(135deg, #08142b, #0b1f3f 72%, #0c2a48);
            border-radius: 14px 14px 0 0;
            box-sizing: border-box;
            margin-bottom: 0;
            max-width: calc(100vw - 48px);
            padding: 24px 24px 22px;
            width: 440px;
        }

        .folio-auth-card-signup {
            width: 520px;
        }

        .folio-auth-card-header h2 {
            color: #ffffff;
            font-size: 1.55rem;
            font-weight: 800;
            line-height: 1.2;
            margin: 0 0 8px;
            word-break: keep-all;
        }

        .folio-auth-card-header p {
            color: rgba(200, 215, 248, 0.9);
            font-size: 0.9rem;
            line-height: 1.55;
            margin: 0;
            word-break: keep-all;
        }

        /* ── Onboarding ── */
        .folio-onboarding-hero {
            margin: 12px auto 18px;
            max-width: 680px;
        }

        .st-key-folio_onboarding_card {
            background: var(--folio-surface);
            border: 1px solid var(--folio-border);
            border-radius: 14px;
            box-shadow: 0 16px 40px rgba(11, 31, 63, 0.08);
            margin: 0 auto;
            max-width: 560px;
            padding: 24px;
            width: min(560px, calc(100vw - 48px));
        }

        .folio-onboarding-card {
            height: 0;
            overflow: hidden;
        }

        /* ── Forms ── */
        div[data-testid="stForm"] {
            background: transparent;
            border: 0;
            padding: 0;
        }

        div[data-testid="stForm"] .stButton button,
        div[data-testid="stForm"] button {
            margin-top: 6px;
        }

        /* ── Submit / Edit panels ── */
        .folio-project-form-intro {
            align-items: center;
            display: flex;
            justify-content: space-between;
            margin: 4px 0 18px;
        }

        .folio-project-form-intro strong {
            color: var(--folio-navy);
            font-size: 1.05rem;
        }

        .folio-project-form-intro span {
            color: var(--folio-muted);
            font-size: 0.82rem;
        }

        .folio-project-form-intro b {
            color: var(--folio-blue);
        }

        [class*="form_section_"] {
            background: var(--folio-surface) !important;
            border: 1px solid var(--folio-border) !important;
            border-radius: 14px !important;
            box-shadow: none !important;
            margin-bottom: 18px !important;
            padding: 24px 26px !important;
        }

        [class*="form_section_"] [data-testid="stWidgetLabel"] {
            display: flex !important;
        }

        [class*="form_section_"] [data-testid="stWidgetLabel"] p {
            color: var(--folio-navy) !important;
            font-size: 0.86rem !important;
            font-weight: 700 !important;
        }

        .folio-form-section-heading {
            align-items: center;
            display: flex;
            gap: 12px;
            margin-bottom: 18px;
        }

        .folio-form-section-heading > span {
            align-items: center;
            background: var(--folio-subtle);
            border-radius: 50%;
            color: var(--folio-blue);
            display: inline-flex;
            flex: 0 0 32px;
            font-size: 0.86rem;
            font-weight: 800;
            height: 32px;
            justify-content: center;
        }

        .folio-form-section-heading strong,
        .folio-form-section-heading small {
            display: block;
        }

        .folio-form-section-heading strong {
            color: var(--folio-navy);
            font-size: 1rem;
        }

        .folio-form-section-heading small {
            color: var(--folio-muted);
            font-size: 0.82rem;
            margin-top: 2px;
        }

        [class*="form_section_"] .stTextInput input,
        [class*="form_section_"] .stTextArea textarea,
        [class*="form_section_"] [data-baseweb="select"] > div {
            background: var(--folio-bg) !important;
        }

        .folio-submit-panel,
        .folio-detail-panel {
            background: var(--folio-surface);
            border: 1px solid var(--folio-border);
            border-radius: 14px;
            padding: 20px;
        }

        .folio-submit-panel h3,
        .folio-detail-panel h3 {
            margin-top: 0;
        }

        .folio-submit-form {
            display: grid;
            grid-template-columns: minmax(0, 1.6fr) minmax(280px, 1fr);
            gap: 24px;
        }

        .folio-detail-grid {
            display: grid;
            grid-template-columns: minmax(0, 1.8fr) minmax(280px, 1fr);
            gap: 24px;
        }

        /* ── Back links ── */
        .folio-back-link,
        .folio-back-link:visited,
        .folio-back-link:hover,
        .folio-back-link:active {
            color: var(--folio-muted) !important;
            display: inline-flex;
            font-size: 0.9rem;
            font-weight: 600;
            margin: 4px 0 12px;
            text-decoration: none !important;
        }

        .folio-back-link:hover {
            color: var(--folio-blue) !important;
        }

        .folio-back-link-bottom {
            background: var(--folio-surface);
            border: 1px solid var(--folio-blue);
            border-radius: 10px;
            color: var(--folio-blue) !important;
            margin: 28px 0 8px;
            padding: 10px 18px;
            transition: background 0.14s;
        }

        .folio-back-link-bottom:hover {
            background: var(--folio-subtle);
            color: var(--folio-navy) !important;
        }

        .folio-attachment-links {
            margin-top: -8px;
        }

        .folio-attachment-links h3 {
            margin-top: 0;
        }

        .folio-attachment-links-bottom {
            margin-top: 24px;
        }

        /* ── Portfolio item cards ── */
        .folio-portfolio-card {
            background: var(--folio-surface);
            border: 0;
            border-radius: 0;
            margin-bottom: 4px;
            padding: 4px 2px 8px;
        }

        [class*="st-key-portfolio_item_"] {
            background: var(--folio-surface);
            border-color: var(--folio-border) !important;
            border-radius: 14px !important;
            margin-bottom: 14px;
            padding: 16px 18px !important;
        }

        .folio-portfolio-card-title {
            color: var(--folio-navy);
            font-size: 0.98rem;
            font-weight: 700;
            margin: 0 0 5px;
            word-break: keep-all;
        }

        .folio-portfolio-card-liner {
            color: var(--folio-muted);
            font-size: 0.86rem;
            line-height: 1.5;
            margin: 0 0 8px;
            word-break: keep-all;
        }

        .folio-portfolio-card-meta {
            color: var(--folio-muted);
            font-size: 0.82rem;
            margin: 8px 0 0;
        }

        /* ── Profile ── */
        .folio-profile-header {
            align-items: center;
            display: flex;
            gap: 18px;
            margin-bottom: 20px;
        }

        .folio-avatar {
            align-items: center;
            background: linear-gradient(135deg, var(--folio-blue), #2d6fd8);
            border-radius: 50%;
            color: #ffffff;
            display: flex;
            flex-shrink: 0;
            font-size: 1.4rem;
            font-weight: 800;
            height: 56px;
            justify-content: center;
            width: 56px;
        }

        .folio-profile-info-name {
            color: var(--folio-navy);
            font-size: 1.3rem;
            font-weight: 800;
            margin: 0 0 3px;
        }

        .folio-profile-info-org {
            color: var(--folio-muted);
            font-size: 0.9rem;
            margin: 0;
        }

        .folio-profile-bio {
            color: var(--folio-navy);
            font-size: 0.92rem;
            line-height: 1.6;
            margin: 12px 0 0;
            word-break: keep-all;
        }

        .st-key-profile_overview {
            background: var(--folio-surface) !important;
            border: 1px solid var(--folio-border) !important;
            border-radius: 14px !important;
            margin-bottom: 24px !important;
            padding: 24px 26px !important;
        }

        .st-key-profile_overview [data-testid="stMetric"] {
            background: var(--folio-bg);
            border: 1px solid var(--folio-border);
            border-radius: 12px;
            padding: 16px 18px;
        }

        /* ── Generic card ── */
        .folio-card {
            background: var(--folio-surface);
            border: 1px solid var(--folio-border);
            border-radius: 10px;
            height: 100%;
            padding: 18px;
        }

        .folio-metric {
            color: var(--folio-blue);
            font-size: 1.55rem;
            font-weight: 800;
        }

        .folio-nav-status {
            color: var(--folio-muted);
            font-size: 0.88rem;
            margin-bottom: 12px;
        }

        /* ── Pills (tag filter display) ── */
        .folio-pills {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin-top: 8px;
        }

        .folio-pills span {
            background: var(--folio-subtle);
            border: 1px solid var(--folio-border);
            border-radius: 999px;
            color: var(--folio-navy);
            font-weight: 600;
            padding: 6px 14px;
        }

        /* ── Footer ── */
        .folio-footer {
            border-top: 1px solid var(--folio-border);
            color: var(--folio-muted);
            font-size: 0.82rem;
            margin-top: 52px;
            padding: 22px 0;
            text-align: center;
        }

        /* ── Responsive ── */
        @media (max-width: 860px) {
            .folio-home-hero {
                grid-template-columns: 1fr;
                min-height: 200px;
                padding: 32px 8px 28px;
            }

            .folio-home-copy h1 {
                font-size: 1.9rem;
            }

            .folio-hero-preview {
                display: none;
            }

            .st-key-folio_browse_panel {
                margin: 22px 0 18px !important;
                padding: 22px 18px 20px !important;
            }

            .folio-search-container {
                align-items: flex-start;
            }

            .folio-home-card {
                min-height: 240px;
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

            .folio-project-form-intro {
                align-items: flex-start;
                flex-direction: column;
                gap: 5px;
            }

            [class*="form_section_"] {
                padding: 20px 18px !important;
            }

            .folio-page-hero h1,
            .folio-hero h1 {
                font-size: 1.5rem;
            }

            .folio-page-hero {
                grid-template-columns: 1fr;
                min-height: 190px;
                padding: 28px 20px;
            }

            .folio-page-hero-visual {
                display: none;
            }

            .folio-page-hero-dark h1 {
                font-size: 1.65rem;
            }

            .st-key-folio_auth_shell {
                width: min(100%, calc(100vw - 28px));
            }

            .st-key-folio_auth_form {
                padding: 18px;
            }

            .folio-auth-card-header {
                padding: 18px;
            }

            .folio-auth-card-header h2 {
                font-size: 1.35rem;
            }

            .stButton > button {
                min-height: 44px;
            }

            .st-key-folio_auth_shell .stFormSubmitButton > button {
                min-height: 44px;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
