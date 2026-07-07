import json

import streamlit.components.v1 as components


def render_google_analytics(measurement_id: str) -> None:
    """Inject a GA4 gtag.js tag into the top-level document.

    st.markdown()/st.html() strip <script> tags for security, so the tag
    cannot be injected that way. Instead this renders a components.v1.html()
    iframe whose script reaches into window.parent.document (same-origin)
    to attach the tag to the real page <head> exactly once per browser tab.
    """
    if not measurement_id:
        return

    components.html(
        f"""
        <script>
        (function() {{
            var doc = window.parent.document;
            if (doc.getElementById('folio-ga-tag')) {{
                return;
            }}

            var loader = doc.createElement('script');
            loader.id = 'folio-ga-tag';
            loader.async = true;
            loader.src = 'https://www.googletagmanager.com/gtag/js?id={measurement_id}';
            doc.head.appendChild(loader);

            var inline = doc.createElement('script');
            inline.id = 'folio-ga-inline';
            inline.innerHTML = "window.dataLayer = window.dataLayer || [];"
                + "function gtag(){{ dataLayer.push(arguments); }}"
                + "gtag('js', new Date());"
                + "gtag('config', '{measurement_id}');";
            doc.head.appendChild(inline);
        }})();
        </script>
        """,
        height=0,
        width=0,
    )


def track_page_view(page_title: str, page_path: str) -> None:
    """Record a virtual pageview for an internal navigate() transition.

    Streamlit routes "pages" through st.query_params + st.rerun() rather than
    a real browser navigation, so GA never sees these as separate pageviews
    on its own. Call this once per rendered page/screen.
    """
    track_event("page_view", {"page_title": page_title, "page_path": page_path})


def track_event(event_name: str, params: dict | None = None) -> None:
    """Fire a gtag() custom event against the tag installed by render_google_analytics().

    No-ops silently if the GA tag was never installed (e.g. GA_MEASUREMENT_ID
    unset locally), since window.parent.gtag will not exist in that case.
    """
    event_name_json = json.dumps(event_name)
    params_json = json.dumps(params or {}, ensure_ascii=False)
    components.html(
        f"""
        <script>
        (function() {{
            if (typeof window.parent.gtag !== 'function') {{
                return;
            }}
            window.parent.gtag('event', {event_name_json}, {params_json});
        }})();
        </script>
        """,
        height=0,
        width=0,
    )
