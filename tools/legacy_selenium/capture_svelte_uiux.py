from __future__ import annotations

import json
import os
import re
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE = "http://127.0.0.1:8788"
KNOWN_PROJECT_ID = "dd1ed00c-1458-4f8e-92cb-4f31e319625d"

HERO_SELECTOR = ", ".join(
    [
        ".hero",
        ".home-hero-shell",
        ".page-image-hero",
        ".detail-hero",
        ".reference-hero",
        ".powerbi-hero",
        ".submit-hero",
        ".my-hero",
        ".notification-hero",
        ".policy-page-hero",
        ".about-gapyear-hero",
        ".project-detail-image-hero",
    ]
)

SELECTORS = {
    "header": ".site-header",
    "nav": ".nav",
    "hero": HERO_SELECTOR,
    "project_card": ".project-card",
    "project_rail": ".project-rail-section",
    "reference_card": ".reference-grid .project-card",
    "form_section": ".project-form-section",
    "form_overview": ".project-form-overview-section",
    "tiptap_toolbar": ".rich-editor-toolbar, .editor-toolbar, .tiptap-toolbar, [aria-label='본문 서식 도구'], [aria-label='서식 도구']",
    "thumbnail_preview": ".hero-thumbnail-preview",
    "thumbnail_panel": ".thumbnail-panel",
    "detail_action": ".detail-footer-row, .detail-action-bar",
    "visual_panel": ".visual-panel",
    "report_section": ".report-section",
    "comments": ".comments-panel, .comment-card",
    "comment_form": ".comment-form",
    "notifications": ".notifications-panel, .notification-item",
    "portfolio": ".portfolio-section, .portfolio-card",
    "unread_badge": ".portfolio-unread-badge",
    "profile_edit": ".profile-edit-card",
    "empty_state": ".empty-panel, .comments-empty, .login-required-panel",
    "error_message": ".auth-message.error, .error, [role='alert']",
    "modal": ".detail-report-modal",
    "detail_delete_dialog": ".detail-delete-dialog",
    "detail_loading": ".detail-loading-content, .detail-loading-card",
    "detail_external_only": ".visual-panel.external-only-output, .embed-external-state",
    "detail_embed_failed": ".visual-panel.embed-failed-output, .embed-failed-state",
}

VIEWPORTS = [("desktop", 1440, 1000), ("mobile", 390, 844)]


def page_def(
    name: str,
    path: str,
    *,
    auth_state: str = "anonymous",
    project_owner_state: str = "n/a",
    workflow_state: str = "default",
    fixture_project_id: str = "",
    expect_hero: bool = True,
) -> dict:
    return {
        "name": name,
        "path": path,
        "auth_state": auth_state,
        "project_owner_state": project_owner_state,
        "workflow_state": workflow_state,
        "fixture_project_id": fixture_project_id,
        "expect_hero": expect_hero,
    }


PUBLIC_PAGES = [
    page_def("home", "/"),
    page_def("about", "/about"),
    page_def("reference-powerbi-latest", "/references/powerbi?sort=latest"),
    page_def("reference-powerbi-likes", "/references/powerbi?sort=likes"),
    page_def("reference-powerbi-views", "/references/powerbi?sort=views"),
    page_def("reference-tableau", "/references/tableau"),
    page_def("reference-datastudio", "/references/datastudio"),
    page_def("reference-streamlit", "/references/streamlit"),
    page_def("powerbi-news", "/powerbi"),
    page_def("powerbi-learning", "/powerbi?topic=learning"),
    page_def("powerbi-community", "/powerbi?topic=community"),
    page_def("powerbi-cert", "/powerbi?topic=cert"),
    page_def(
        "project-detail-known",
        f"/projects/{KNOWN_PROJECT_ID}",
        project_owner_state="unknown",
        fixture_project_id=KNOWN_PROJECT_ID,
    ),
    page_def("login", "/login", expect_hero=False),
    page_def("signup", "/signup", expect_hero=False),
    page_def("reset-password", "/reset-password", expect_hero=False),
    page_def("policy-terms", "/policy/terms"),
    page_def("policy-privacy", "/policy/privacy"),
]

AUTH_PAGES = [
    page_def("submit", "/submit", auth_state="authenticated", workflow_state="empty_draft"),
    page_def("my-page", "/my", auth_state="authenticated", project_owner_state="owner_listing"),
    page_def("notifications", "/notifications", auth_state="authenticated"),
    page_def(
        "project-edit-known",
        f"/projects/{KNOWN_PROJECT_ID}/edit",
        auth_state="authenticated",
        project_owner_state="unknown_or_not_owner",
        fixture_project_id=KNOWN_PROJECT_ID,
    ),
    page_def("onboarding", "/onboarding", auth_state="authenticated", expect_hero=False),
]


def load_env() -> None:
    for path in [ROOT / ".env", ROOT / "svelte_app" / ".env"]:
        if not path.exists():
            continue
        for raw in path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def resolve_test_pbix_path() -> Path | None:
    configured = os.environ.get("FOLIO_TEST_PBIX_PATH") or os.environ.get("test_pbix_path")
    candidates = [Path(configured)] if configured else []
    candidates.append(ROOT / "artifacts" / "test.pbix")
    for candidate in candidates:
        if candidate.exists() and candidate.suffix.lower() == ".pbix":
            return candidate.resolve()
    return None
def safe_name(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_.-]+", "-", value).strip("-")


def make_driver(width: int, height: int) -> webdriver.Chrome:
    options = Options()
    chrome = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
    if chrome.exists():
        options.binary_location = str(chrome)
    options.add_argument("--headless=new")
    options.add_argument(f"--window-size={width},{height}")
    options.add_argument("--hide-scrollbars")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=options)


def page_height(driver: webdriver.Chrome) -> int:
    return int(
        driver.execute_script(
            r"""
        const candidates = [document.documentElement, document.body].filter(Boolean);
        const heights = candidates.map((el) => Math.max(
          el.scrollHeight || 0,
          el.offsetHeight || 0,
          el.clientHeight || 0
        ));
        return Math.min(12000, Math.max(900, ...heights));
    """
        )
    )


def visible_text(driver: webdriver.Chrome, selector: str, limit: int = 120) -> list[str]:
    values = driver.execute_script(
        r"""
        const selector = arguments[0];
        const limit = arguments[1];
        return Array.from(document.querySelectorAll(selector))
          .filter((el) => {
            const rect = el.getBoundingClientRect();
            const style = window.getComputedStyle(el);
            return rect.width > 0 && rect.height > 0 && style.visibility !== 'hidden' && style.display !== 'none';
          })
          .map((el) => (el.innerText || el.textContent || '').replace(/\s+/g, ' ').trim())
          .filter(Boolean)
          .slice(0, limit);
    """,
        selector,
        limit,
    )
    return [str(item) for item in values]


def current_path_from_url(url: str) -> str:
    parsed = urlparse(url)
    return parsed.path + (("?" + parsed.query) if parsed.query else "")


def build_warnings(metrics: dict) -> list[str]:
    warnings: list[str] = []
    counts = metrics.get("counts", {})
    selectors = metrics.get("selectors", {})
    scroll = metrics.get("scroll", {})
    body = str(metrics.get("bodyTextStart", ""))
    overflow_nodes = metrics.get("overflowElements", [])
    if scroll.get("overflowX", 0) > 3:
        warnings.append(f"horizontal overflow {scroll.get('overflowX')}px")
    if scroll.get("overflowX", 0) > 3 and overflow_nodes:
        warnings.append(f"overflow elements {len(overflow_nodes)}")
    if "404" in body[:300] or "Not Found" in body[:300]:
        warnings.append("possible 404/not found state")
    if metrics.get("expect_hero", True) and selectors.get("hero", 0) == 0:
        warnings.append("no page hero detected")
    if counts.get("h1", 0) == 0:
        warnings.append("no h1 detected")
    if selectors.get("error_message", 0) > 0:
        warnings.append("visible error message selector detected")
    if "`r`n" in body or "`n" in body:
        warnings.append("literal escaped newline text detected")
    return warnings


def collect_metrics(driver: webdriver.Chrome, page: dict, url: str, viewport: str) -> dict:
    metrics = driver.execute_script(
        r"""
        const selectorCounts = arguments[0];
        const heroSelector = arguments[1];
        const count = (selector) => document.querySelectorAll(selector).length;
        const doc = document.documentElement;
        const body = document.body;
        const rawScrollWidth = Math.max(doc.scrollWidth, body ? body.scrollWidth : 0);
        const scrollWidth = doc.scrollWidth;
        const overflowX = scrollWidth - window.innerWidth;
        const firstHero = document.querySelector(heroSelector);
        const firstAction = document.querySelector('button, a.button-link, a.primary, .hero-cta, .powerbi-hero-cta');
        const heroRect = firstHero ? firstHero.getBoundingClientRect() : null;
        const actionRect = firstAction ? firstAction.getBoundingClientRect() : null;
        const selectors = {};
        for (const [key, selector] of Object.entries(selectorCounts)) selectors[key] = count(selector);
        const norm = (value) => String(value || '').replace(/\s+/g, ' ').trim();
        const describe = (el) => {
          const rect = el.getBoundingClientRect();
          const style = window.getComputedStyle(el);
          return {
            tag: el.tagName.toLowerCase(),
            id: el.id || '',
            className: typeof el.className === 'string' ? el.className : norm(el.getAttribute('class')),
            role: el.getAttribute('role') || '',
            ariaLabel: el.getAttribute('aria-label') || '',
            text: norm(el.innerText || el.textContent).slice(0, 120),
            rect: {
              x: Math.round(rect.x),
              y: Math.round(rect.y),
              width: Math.round(rect.width),
              height: Math.round(rect.height),
              right: Math.round(rect.right),
              left: Math.round(rect.left)
            },
            styles: {
              display: style.display,
              position: style.position,
              width: style.width,
              minWidth: style.minWidth,
              maxWidth: style.maxWidth,
              overflowX: style.overflowX,
              whiteSpace: style.whiteSpace
            }
          };
        };
        const overflowElements = Array.from(document.querySelectorAll('body *'))
          .filter((el) => {
            const rect = el.getBoundingClientRect();
            const style = window.getComputedStyle(el);
            if (style.display === 'none' || style.visibility === 'hidden') return false;
            if (rect.width <= 0 || rect.height <= 0) return false;
            return rect.right > window.innerWidth + 1 || rect.left < -1 || rect.width > window.innerWidth + 1;
          })
          .slice(0, 20)
          .map(describe);
        return {
          title: document.title,
          pathname: location.pathname + location.search,
          viewport: { width: window.innerWidth, height: window.innerHeight },
          scroll: {
            width: scrollWidth,
            rawWidth: rawScrollWidth,
            bodyWidth: body ? body.scrollWidth : 0,
            height: Math.max(doc.scrollHeight, body ? body.scrollHeight : 0),
            overflowX
          },
          counts: {
            h1: count('h1'), h2: count('h2'), links: count('a'), buttons: count('button'),
            inputs: count('input, textarea, select'), forms: count('form'),
            details: count('details'), openDetails: count('details[open]')
          },
          selectors,
          firstHero: heroRect ? { x: Math.round(heroRect.x), y: Math.round(heroRect.y), width: Math.round(heroRect.width), height: Math.round(heroRect.height) } : null,
          firstAction: actionRect ? { text: norm(firstAction.innerText || firstAction.textContent), x: Math.round(actionRect.x), y: Math.round(actionRect.y), width: Math.round(actionRect.width), height: Math.round(actionRect.height) } : null,
          overflowElements,
          bodyTextStart: (document.body ? document.body.innerText : '').slice(0, 1200)
        };
    """,
        SELECTORS,
        HERO_SELECTOR,
    )
    metrics.update(
        {
            "name": page["name"],
            "url": url,
            "viewportName": viewport,
            "auth_state": page.get("auth_state", "unknown"),
            "project_owner_state": page.get("project_owner_state", "unknown"),
            "workflow_state": page.get("workflow_state", "default"),
            "fixture_project_id": page.get("fixture_project_id", ""),
            "expect_hero": page.get("expect_hero", True),
        }
    )
    metrics["h1Text"] = visible_text(driver, "h1", 10)
    metrics["navText"] = visible_text(driver, ".nav a, .nav button", 40)
    metrics["buttonText"] = visible_text(driver, "button, a.button-link, a.primary, .hero-cta, .powerbi-hero-cta", 80)
    metrics["warnings"] = build_warnings(metrics)
    return metrics


def capture_current(
    driver: webdriver.Chrome,
    out_dir: Path,
    viewport: str,
    viewport_width: int,
    viewport_height: int,
    page: dict,
    url: str,
) -> dict:
    height = page_height(driver)
    driver.set_window_size(viewport_width, height + 120)
    time.sleep(0.35)
    screenshot_path = out_dir / f"{viewport}-{safe_name(page['name'])}.png"
    driver.save_screenshot(str(screenshot_path))
    metrics = collect_metrics(driver, page, url, viewport)
    metrics["screenshot"] = str(screenshot_path.relative_to(ROOT))
    return metrics


def capture_page(
    driver: webdriver.Chrome,
    base_url: str,
    out_dir: Path,
    viewport: str,
    viewport_width: int,
    viewport_height: int,
    page: dict,
    wait: float = 2.2,
) -> dict:
    url = urljoin(base_url.rstrip("/") + "/", page["path"].lstrip("/"))
    driver.set_window_size(viewport_width, viewport_height)
    driver.get(url)
    time.sleep(wait)
    return capture_current(driver, out_dir, viewport, viewport_width, viewport_height, page, url)


def login_svelte(driver: webdriver.Chrome, base_url: str) -> bool:
    email = os.environ.get("FOLIO_TEST_ID") or os.environ.get("test_id")
    password = os.environ.get("FOLIO_TEST_PW") or os.environ.get("test_pw")
    if not email or not password:
        return False
    driver.get(urljoin(base_url.rstrip("/") + "/", "login"))
    time.sleep(1.5)
    inputs = driver.find_elements(By.CSS_SELECTOR, "input")
    if len(inputs) < 2:
        return False
    inputs[0].clear()
    inputs[0].send_keys(email)
    inputs[1].clear()
    inputs[1].send_keys(password)
    inputs[1].send_keys(Keys.ENTER)
    time.sleep(4)
    return "login" not in driver.current_url.lower()


def extract_project_id(path: str) -> str:
    match = re.search(r"/projects/([^/]+)/", path)
    return match.group(1) if match else ""


def resolve_auth_pages(driver: webdriver.Chrome, base_url: str) -> list[dict]:
    pages = [dict(page) for page in AUTH_PAGES]
    try:
        driver.get(urljoin(base_url.rstrip("/") + "/", "my"))
        time.sleep(2)
        edit_links = [
            link.get_attribute("href") or ""
            for link in driver.find_elements(By.CSS_SELECTOR, ".portfolio-actions a[href*='/edit'], a.button-link[href*='/edit']")
        ]
        edit_links = [link for link in edit_links if link]
        if edit_links:
            edit_path = current_path_from_url(edit_links[0])
            owner_project_id = extract_project_id(edit_path)
            detail_path = f"/projects/{owner_project_id}" if owner_project_id else edit_path.replace("/edit", "")
            pages.append(
                page_def(
                    "project-detail-owner",
                    detail_path,
                    auth_state="authenticated",
                    project_owner_state="owner",
                    workflow_state="loaded_existing_project",
                    fixture_project_id=owner_project_id,
                )
            )
            pages.append(
                page_def(
                    "project-edit-owner",
                    edit_path,
                    auth_state="authenticated",
                    project_owner_state="owner",
                    workflow_state="loaded_existing_project",
                    fixture_project_id=owner_project_id,
                )
            )
    except Exception as exc:
        pages.append(
            {
                "name": "auth-page-resolution-error",
                "path": "/my",
                "auth_state": "authenticated",
                "project_owner_state": "unknown",
                "workflow_state": f"resolve_error:{type(exc).__name__}",
                "fixture_project_id": "",
                "expect_hero": False,
            }
        )
    return pages


def set_text_inputs(driver: webdriver.Chrome, values: dict[str, str]) -> None:
    driver.execute_script(
        r"""
        const values = arguments[0];
        const norm = (value) => String(value || '').toLowerCase();
        const isVisible = (el) => {
          const rect = el.getBoundingClientRect();
          const style = window.getComputedStyle(el);
          return rect.width > 0 && rect.height > 0 && style.display !== 'none' && style.visibility !== 'hidden';
        };
        const fields = Array.from(document.querySelectorAll('input:not([type]), input[type="text"], input[type="url"], textarea'))
          .filter(isVisible);
        const setValue = (el, value) => {
          const proto = el instanceof HTMLTextAreaElement ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
          Object.getOwnPropertyDescriptor(proto, 'value').set.call(el, value);
          el.dispatchEvent(new Event('input', { bubbles: true }));
          el.dispatchEvent(new Event('change', { bubbles: true }));
        };
        for (const [needle, value] of Object.entries(values)) {
          const target = fields.find((el) => norm(el.placeholder).includes(norm(needle)) || norm(el.name).includes(norm(needle)));
          if (target) setValue(target, value);
        }
    """,
        values,
    )


def click_radio_value(driver: webdriver.Chrome, value: str) -> None:
    driver.execute_script(
        r"""
        const value = arguments[0];
        const input = document.querySelector(`input[type="radio"][value="${CSS.escape(value)}"]`);
        if (input) input.click();
    """,
        value,
    )
    time.sleep(0.35)


def clear_submit_drafts(driver: webdriver.Chrome) -> None:
    driver.execute_script(
        r"""
        for (const key of Object.keys(localStorage)) {
          if (key.startsWith('folio-submit-draft:')) localStorage.removeItem(key);
        }
    """
    )


def inject_my_unread_badge(driver: webdriver.Chrome) -> bool:
    return bool(
        driver.execute_script(
            r"""
            const titleLine = document.querySelector('.portfolio-card .portfolio-title-line');
            if (!titleLine || titleLine.querySelector('.portfolio-unread-badge')) return false;
            const title = titleLine.querySelector('strong');
            const badge = document.createElement('span');
            badge.className = 'portfolio-unread-badge';
            badge.setAttribute('aria-label', '안 본 댓글 있음');
            badge.textContent = 'NEW';
            titleLine.insertBefore(badge, title ? title.nextSibling : titleLine.firstChild);
            return true;
        """
        )
    )


def capture_submit_workflow(driver: webdriver.Chrome, base_url: str, out_dir: Path, viewport: str, width: int, height: int) -> list[dict]:
    results: list[dict] = []
    submit_url = urljoin(base_url.rstrip("/") + "/", "submit")

    driver.set_window_size(width, height)
    driver.get(submit_url)
    time.sleep(1.4)
    clear_submit_drafts(driver)
    driver.get(submit_url)
    time.sleep(1.8)
    results.append(
        capture_current(
            driver,
            out_dir,
            viewport,
            width,
            height,
            page_def("submit-empty", "/submit", auth_state="authenticated", workflow_state="empty_draft"),
            submit_url,
        )
    )

    set_text_inputs(
        driver,
        {
            "서울시": "서울시 청년 취업 데이터 분석",
            "핵심 메시지": "청년 취업 지표를 지역과 산업별로 비교합니다.",
            "공공데이터": "공공데이터, 취업, 시각화",
            "iframe": "https://app.powerbi.com/view?r=sample",
            "github.com": "https://github.com/example/youth-jobs",
            "https://...": "https://example.com/youth-jobs-dashboard",
        },
    )
    time.sleep(0.6)
    results.append(
        capture_current(
            driver,
            out_dir,
            viewport,
            width,
            height,
            page_def("submit-typed", "/submit", auth_state="authenticated", workflow_state="typed_required_fields"),
            submit_url,
        )
    )

    click_radio_value(driver, "manual_url")
    set_text_inputs(driver, {"썸네일": urljoin(base_url.rstrip("/") + "/", "hero-dashboard-lab.webp")})
    results.append(
        capture_current(
            driver,
            out_dir,
            viewport,
            width,
            height,
            page_def("submit-thumbnail-url", "/submit", auth_state="authenticated", workflow_state="thumbnail_manual_url"),
            submit_url,
        )
    )

    click_radio_value(driver, "capture")
    results.append(
        capture_current(
            driver,
            out_dir,
            viewport,
            width,
            height,
            page_def("submit-capture-selected", "/submit", auth_state="authenticated", workflow_state="thumbnail_capture_selected"),
            submit_url,
        )
    )

    click_radio_value(driver, "powerbi")
    results.append(
        capture_current(
            driver,
            out_dir,
            viewport,
            width,
            height,
            page_def("submit-powerbi-selected", "/submit", auth_state="authenticated", workflow_state="platform_powerbi_selected"),
            submit_url,
        )
    )

    pbix_path = resolve_test_pbix_path()
    if pbix_path:
        try:
            file_input = driver.find_element(By.CSS_SELECTOR, "input[type='file'][accept='.pbix']")
            file_input.send_keys(str(pbix_path))
            time.sleep(0.6)
            results.append(
                capture_current(
                    driver,
                    out_dir,
                    viewport,
                    width,
                    height,
                    page_def("submit-pbix-file-selected", "/submit", auth_state="authenticated", workflow_state="pbix_file_selected"),
                    submit_url,
                )
            )
        except Exception:
            pass

    driver.get(submit_url)
    time.sleep(1.3)
    clear_submit_drafts(driver)
    driver.get(submit_url)
    time.sleep(1.5)
    button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    button.click()
    time.sleep(1)
    results.append(
        capture_current(
            driver,
            out_dir,
            viewport,
            width,
            height,
            page_def("submit-validation-error", "/submit", auth_state="authenticated", workflow_state="validation_error_empty_required"),
            submit_url,
        )
    )
    return results


def capture_edit_pbix_workflow(driver: webdriver.Chrome, base_url: str, out_dir: Path, viewport: str, width: int, height: int) -> list[dict]:
    results: list[dict] = []
    my_url = urljoin(base_url.rstrip("/") + "/", "my")
    driver.set_window_size(width, height)
    driver.get(my_url)
    time.sleep(1.8)
    edit_links = [
        link.get_attribute("href") or ""
        for link in driver.find_elements(By.CSS_SELECTOR, ".portfolio-actions a[href*='/edit'], a.button-link[href*='/edit']")
    ]
    edit_links = [link for link in edit_links if link]
    if not edit_links:
        return results

    edit_url = edit_links[0]
    edit_path = current_path_from_url(edit_url)
    driver.set_window_size(width, height)
    driver.get(edit_url)
    time.sleep(2)
    click_radio_value(driver, "powerbi")
    results.append(
        capture_current(
            driver,
            out_dir,
            viewport,
            width,
            height,
            page_def("project-edit-powerbi-selected", edit_path, auth_state="authenticated", project_owner_state="owner", workflow_state="edit_platform_powerbi_selected"),
            edit_url,
        )
    )

    checkbox = next(
        (item for item in driver.find_elements(By.CSS_SELECTOR, ".delete-option-row input[type='checkbox']") if item.is_displayed()),
        None,
    )
    if checkbox and not checkbox.is_selected():
        checkbox.click()
        time.sleep(0.5)
        results.append(
            capture_current(
                driver,
                out_dir,
                viewport,
                width,
                height,
                page_def("project-edit-pbix-replace-enabled", edit_path, auth_state="authenticated", project_owner_state="owner", workflow_state="edit_pbix_replace_enabled"),
                edit_url,
            )
        )

    pbix_path = resolve_test_pbix_path()
    if pbix_path:
        try:
            file_input = driver.find_element(By.CSS_SELECTOR, "input[type='file'][accept='.pbix']")
            file_input.send_keys(str(pbix_path))
            time.sleep(0.6)
            results.append(
                capture_current(
                    driver,
                    out_dir,
                    viewport,
                    width,
                    height,
                    page_def("project-edit-pbix-file-selected", edit_path, auth_state="authenticated", project_owner_state="owner", workflow_state="edit_pbix_file_selected"),
                    edit_url,
                )
            )
        except Exception:
            pass
    return results
def capture_my_workflow(driver: webdriver.Chrome, base_url: str, out_dir: Path, viewport: str, width: int, height: int) -> list[dict]:
    results: list[dict] = []
    my_url = urljoin(base_url.rstrip("/") + "/", "my")
    driver.set_window_size(width, height)
    driver.get(my_url)
    time.sleep(2)
    try:
        profile_button = next((button for button in driver.find_elements(By.CSS_SELECTOR, "button") if "프로필 편집" in (button.text or "")), None)
        if profile_button:
            profile_button.click()
            time.sleep(0.7)
            results.append(
                capture_current(
                    driver,
                    out_dir,
                    viewport,
                    width,
                    height,
                    page_def("my-profile-edit-open", "/my", auth_state="authenticated", project_owner_state="owner_listing", workflow_state="profile_edit_open"),
                    my_url,
                )
            )
    except Exception:
        pass

    driver.set_window_size(width, height)
    driver.get(my_url)
    time.sleep(2)
    try:
        if inject_my_unread_badge(driver):
            time.sleep(0.3)
            results.append(
                capture_current(
                    driver,
                    out_dir,
                    viewport,
                    width,
                    height,
                    page_def("my-unread-badge-fixture", "/my", auth_state="authenticated", project_owner_state="owner_listing", workflow_state="visual_fixture_unread_comment_badge"),
                    my_url,
                )
            )
    except Exception:
        pass

    driver.set_window_size(width, height)
    driver.get(my_url)
    time.sleep(2)
    try:
        delete_button = next((button for button in driver.find_elements(By.CSS_SELECTOR, ".portfolio-actions button") if (button.text or "").strip() == "삭제"), None)
        if delete_button:
            delete_button.click()
            time.sleep(0.7)
            results.append(
                capture_current(
                    driver,
                    out_dir,
                    viewport,
                    width,
                    height,
                    page_def("my-delete-confirm", "/my", auth_state="authenticated", project_owner_state="owner_listing", workflow_state="delete_confirm_first_click"),
                    my_url,
                )
            )
    except Exception:
        pass
    return results


def find_owner_detail_path(driver: webdriver.Chrome, base_url: str) -> str | None:
    driver.set_window_size(1200, 900)
    driver.get(urljoin(base_url.rstrip("/") + "/", "my"))
    time.sleep(1.8)
    links = [
        link.get_attribute("href") or ""
        for link in driver.find_elements(By.CSS_SELECTOR, ".portfolio-actions a[href*='/projects/'], a.button-link[href*='/projects/']")
    ]
    links = [link for link in links if link and "/edit" not in link]
    return current_path_from_url(links[0]) if links else None


def inject_detail_loading_shell(driver: webdriver.Chrome) -> bool:
    return bool(
        driver.execute_script(
            r"""
            const main = document.querySelector('main') || document.body;
            if (!main) return false;
            main.innerHTML = `
              <section class="detail-hero project-detail-image-hero detail-loading-hero" aria-label="프로젝트 상세 로딩 중">
                <div class="detail-hero-copy">
                  <div class="detail-hero-eyebrow">프로젝트 상세</div>
                  <h1>프로젝트를 불러오고 있어요.</h1>
                  <p>곧 시각화와 프로젝트 설명이 이어서 표시됩니다.</p>
                </div>
                <div class="detail-loading-card" aria-hidden="true">
                  <span class="detail-loading-chip"></span>
                  <span class="detail-loading-title"></span>
                  <span class="detail-loading-line"></span>
                  <span class="detail-loading-line detail-loading-line-short"></span>
                  <div class="detail-loading-metrics"><span></span><span></span><span></span></div>
                </div>
              </section>
              <section class="detail-loading-content" aria-label="프로젝트 상세 본문 로딩 중">
                <div class="detail-loading-visual"></div>
                <div class="detail-loading-panel">
                  <span class="detail-loading-line detail-loading-line-wide"></span>
                  <span class="detail-loading-line"></span>
                  <span class="detail-loading-line detail-loading-line-short"></span>
                </div>
              </section>`;
            return true;
        """
        )
    )


def inject_comment_message(driver: webdriver.Chrome, kind: str) -> bool:
    return bool(
        driver.execute_script(
            r"""
            const kind = arguments[0];
            const panel = document.querySelector('.comments-panel');
            if (!panel) return false;
            const oldMessage = panel.querySelector('.auth-message.fixture-message');
            if (oldMessage) oldMessage.remove();
            const message = document.createElement('div');
            message.className = `auth-message fixture-message ${kind === 'error' ? 'error' : 'success'}`;
            message.textContent = kind === 'error' ? '댓글 내용을 입력하세요.' : '댓글이 등록되었습니다.';
            const heading = panel.querySelector('.comments-heading');
            panel.insertBefore(message, heading ? heading.nextSibling : panel.firstChild);
            const form = panel.querySelector('.comment-form');
            if (form && kind === 'error') form.classList.add('fixture-error');
            return true;
        """,
            kind,
        )
    )

def inject_liked_state(driver: webdriver.Chrome) -> bool:
    return bool(
        driver.execute_script(
            r"""
            const button = document.querySelector('.like-control button');
            if (!button) return false;
            button.classList.add('liked');
            const icon = button.querySelector('span');
            if (icon) icon.textContent = '♥';
            return true;
        """
        )
    )


def inject_detail_visual_state(driver: webdriver.Chrome, kind: str) -> bool:
    return bool(
        driver.execute_script(
            r"""
            const kind = arguments[0];
            const panel = document.querySelector('.visual-panel');
            if (!panel) return false;
            const frame = panel.querySelector('.dashboard-frame, .powerbi-shell');
            if (frame) frame.remove();
            panel.classList.toggle('external-only-output', kind === 'external');
            panel.classList.toggle('embed-failed-output', kind === 'failed');
            let message = panel.querySelector('.embed-empty');
            if (!message) {
              message = document.createElement('div');
              const heading = panel.querySelector('.visual-panel-head');
              if (heading && heading.nextSibling) {
                panel.insertBefore(message, heading.nextSibling);
              } else if (heading) {
                panel.appendChild(message);
              } else {
                panel.insertBefore(message, panel.firstChild);
              }
            }
            message.className = kind === 'failed'
              ? 'embed-empty embed-failed-state'
              : 'embed-empty embed-external-state';
            message.textContent = kind === 'failed'
              ? 'Power BI 보고서를 불러오지 못했습니다. 프로젝트 작성자는 마이페이지에서 상태를 확인하세요.'
              : '이 프로젝트는 외부 대시보드 링크로 확인할 수 있습니다.';
            const caption = panel.querySelector('.visual-caption');
            if (caption) caption.remove();
            return true;
        """,
            kind,
        )
    )

def focus_comment_form(driver: webdriver.Chrome) -> bool:
    return bool(
        driver.execute_script(
            r"""
            const textarea = document.querySelector('.comments-panel .comment-form textarea');
            if (!textarea) return false;
            textarea.focus();
            textarea.value = '상세페이지 댓글 입력 상태를 확인합니다.';
            textarea.dispatchEvent(new Event('input', { bubbles: true }));
            return true;
        """
        )
    )


def capture_detail_workflow(driver: webdriver.Chrome, base_url: str, out_dir: Path, viewport: str, width: int, height: int) -> list[dict]:
    results: list[dict] = []
    known_url = urljoin(base_url.rstrip("/") + "/", f"projects/{KNOWN_PROJECT_ID}")

    driver.set_window_size(width, height)
    driver.get(known_url)
    time.sleep(2)
    try:
        if inject_detail_loading_shell(driver):
            time.sleep(0.3)
            results.append(
                capture_current(
                    driver,
                    out_dir,
                    viewport,
                    width,
                    height,
                    page_def("project-detail-loading-fixture", f"/projects/{KNOWN_PROJECT_ID}", auth_state="authenticated", project_owner_state="unknown", workflow_state="visual_fixture_loading_shell", fixture_project_id=KNOWN_PROJECT_ID),
                    known_url,
                )
            )
    except Exception:
        pass

    for kind, name, workflow in [
        ("external", "project-detail-external-only-fixture", "visual_fixture_external_only_output"),
        ("failed", "project-detail-embed-failed-fixture", "visual_fixture_embed_failed_output"),
    ]:
        driver.set_window_size(width, height)
        driver.get(known_url)
        time.sleep(2)
        try:
            if inject_detail_visual_state(driver, kind):
                time.sleep(0.3)
                results.append(
                    capture_current(
                        driver,
                        out_dir,
                        viewport,
                        width,
                        height,
                        page_def(name, f"/projects/{KNOWN_PROJECT_ID}", auth_state="authenticated", project_owner_state="unknown", workflow_state=workflow, fixture_project_id=KNOWN_PROJECT_ID),
                        known_url,
                    )
                )
        except Exception:
            pass
    driver.set_window_size(width, height)
    driver.get(known_url)
    time.sleep(2)
    try:
        share_button = next((button for button in driver.find_elements(By.CSS_SELECTOR, "button") if "링크 복사" in (button.text or "")), None)
        if share_button:
            share_button.click()
            time.sleep(0.4)
            results.append(
                capture_current(
                    driver,
                    out_dir,
                    viewport,
                    width,
                    height,
                    page_def("project-detail-share-clicked", f"/projects/{KNOWN_PROJECT_ID}", auth_state="authenticated", project_owner_state="unknown", workflow_state="share_button_clicked", fixture_project_id=KNOWN_PROJECT_ID),
                    known_url,
                )
            )
    except Exception:
        pass

    driver.set_window_size(width, height)
    driver.get(known_url)
    time.sleep(2)
    try:
        report_button = next((button for button in driver.find_elements(By.CSS_SELECTOR, "button") if (button.text or "").strip() == "신고"), None)
        if report_button:
            report_button.click()
            time.sleep(0.7)
            results.append(
                capture_current(
                    driver,
                    out_dir,
                    viewport,
                    width,
                    height,
                    page_def("project-detail-report-modal", f"/projects/{KNOWN_PROJECT_ID}", auth_state="authenticated", project_owner_state="not_owner", workflow_state="report_modal_open", fixture_project_id=KNOWN_PROJECT_ID),
                    known_url,
                )
            )
    except Exception:
        pass

    driver.set_window_size(width, height)
    driver.get(known_url)
    time.sleep(2)
    try:
        if inject_liked_state(driver):
            time.sleep(0.3)
            results.append(
                capture_current(
                    driver,
                    out_dir,
                    viewport,
                    width,
                    height,
                    page_def("project-detail-liked-fixture", f"/projects/{KNOWN_PROJECT_ID}", auth_state="authenticated", project_owner_state="unknown", workflow_state="visual_fixture_liked_state", fixture_project_id=KNOWN_PROJECT_ID),
                    known_url,
                )
            )
    except Exception:
        pass

    driver.set_window_size(width, height)
    driver.get(known_url)
    time.sleep(2)
    try:
        if focus_comment_form(driver):
            time.sleep(0.3)
            results.append(
                capture_current(
                    driver,
                    out_dir,
                    viewport,
                    width,
                    height,
                    page_def("project-detail-comment-draft", f"/projects/{KNOWN_PROJECT_ID}", auth_state="authenticated", project_owner_state="unknown", workflow_state="comment_form_draft", fixture_project_id=KNOWN_PROJECT_ID),
                    known_url,
                )
            )
    except Exception:
        pass
    for kind, name, workflow in [
        ("success", "project-detail-comment-success-fixture", "visual_fixture_comment_success"),
        ("error", "project-detail-comment-error-fixture", "visual_fixture_comment_error"),
    ]:
        driver.set_window_size(width, height)
        driver.get(known_url)
        time.sleep(2)
        try:
            if inject_comment_message(driver, kind):
                time.sleep(0.3)
                results.append(
                    capture_current(
                        driver,
                        out_dir,
                        viewport,
                        width,
                        height,
                        page_def(name, f"/projects/{KNOWN_PROJECT_ID}", auth_state="authenticated", project_owner_state="unknown", workflow_state=workflow, fixture_project_id=KNOWN_PROJECT_ID),
                        known_url,
                    )
                )
        except Exception:
            pass

    try:
        owner_detail_path = find_owner_detail_path(driver, base_url)
        if owner_detail_path:
            owner_url = urljoin(base_url.rstrip("/") + "/", owner_detail_path.lstrip("/"))
            driver.set_window_size(width, height)
            driver.get(owner_url)
            time.sleep(2)
            delete_button = next((button for button in driver.find_elements(By.CSS_SELECTOR, ".detail-action-group button") if (button.text or "").strip() == "삭제"), None)
            if delete_button:
                delete_button.click()
                time.sleep(0.7)
                results.append(
                    capture_current(
                        driver,
                        out_dir,
                        viewport,
                        width,
                        height,
                        page_def("project-detail-delete-dialog", owner_detail_path, auth_state="authenticated", project_owner_state="owner", workflow_state="delete_dialog_open", fixture_project_id=extract_project_id(owner_detail_path + "/")),
                        owner_url,
                    )
                )
    except Exception:
        pass

    return results

def capture_notification_popover(driver: webdriver.Chrome, base_url: str, out_dir: Path, viewport: str, width: int, height: int) -> list[dict]:
    results: list[dict] = []
    url = urljoin(base_url.rstrip("/") + "/", "notifications")
    driver.set_window_size(width, height)
    driver.get(url)
    time.sleep(1.8)
    try:
        target = driver.find_element(By.CSS_SELECTOR, ".notification-link, a[href='/notifications']")
        target.click()
        time.sleep(0.8)
        results.append(
            capture_current(
                driver,
                out_dir,
                viewport,
                width,
                height,
                page_def("notifications-header-popover", "/notifications", auth_state="authenticated", workflow_state="header_notification_click"),
                url,
            )
        )
    except Exception:
        pass
    return results


def auth_login_result(base_url: str, viewport: str, driver: webdriver.Chrome, logged_in: bool) -> dict:
    return {
        "name": "auth-login-result",
        "url": urljoin(base_url.rstrip("/") + "/", "login"),
        "viewportName": viewport,
        "screenshot": "",
        "title": driver.title,
        "auth_state": "authenticated" if logged_in else "auth_required_but_login_failed",
        "project_owner_state": "n/a",
        "workflow_state": "login_session_setup",
        "fixture_project_id": "",
        "h1Text": [],
        "navText": [],
        "buttonText": [],
        "scroll": {"height": 0, "width": 0, "overflowX": 0},
        "counts": {},
        "selectors": {},
        "overflowElements": [],
        "warnings": [] if logged_in else ["login failed or test credentials missing"],
    }


def write_report(out_dir: Path, results: list[dict]) -> None:
    (out_dir / "report.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = ["# Current Svelte UIUX Capture", ""]
    lines.append("| viewport | name | state | owner | workflow | screenshot | url | height | warnings |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- | ---: | --- |")
    for item in results:
        warning_text = ", ".join(item.get("warnings", [])) if item.get("warnings") else "ok"
        state = item.get("auth_state", "")
        owner = item.get("project_owner_state", "")
        workflow = item.get("workflow_state", "")
        height = item.get("scroll", {}).get("height", 0)
        screenshot = item.get("screenshot") or "(no screenshot)"
        lines.append(
            f"| {item['viewportName']} | {item['name']} | {state} | {owner} | {workflow} | {screenshot} | {item['url']} | {height} | {warning_text} |"
        )
    (out_dir / "manifest.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    overflow_lines = ["# Horizontal Overflow Trace", ""]
    for item in results:
        nodes = item.get("overflowElements") or []
        if not nodes or item.get("scroll", {}).get("overflowX", 0) <= 3:
            continue
        overflow_lines.append(f"## {item['viewportName']} / {item['name']}")
        overflow_lines.append(f"- overflowX: {item.get('scroll', {}).get('overflowX', 0)}px")
        for node in nodes[:10]:
            rect = node.get("rect", {})
            overflow_lines.append(
                f"- `{node.get('tag')}` .`{node.get('className')}` right={rect.get('right')} width={rect.get('width')} text={node.get('text')!r}"
            )
        overflow_lines.append("")
    (out_dir / "overflow-trace.md").write_text("\n".join(overflow_lines) + "\n", encoding="utf-8")


def main() -> None:
    load_env()
    base_url = os.environ.get("SVELTE_CAPTURE_BASE", DEFAULT_BASE)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    out_dir = ROOT / "artifacts" / f"uiux-svelte-current-{stamp}"
    out_dir.mkdir(parents=True, exist_ok=True)
    results: list[dict] = []

    for viewport, width, height in VIEWPORTS:
        driver = make_driver(width, height)
        try:
            for page in PUBLIC_PAGES:
                results.append(capture_page(driver, base_url, out_dir, viewport, width, height, page))
        finally:
            driver.quit()

        driver = make_driver(width, height)
        try:
            logged_in = login_svelte(driver, base_url)
            results.append(auth_login_result(base_url, viewport, driver, logged_in))
            auth_pages = resolve_auth_pages(driver, base_url) if logged_in else AUTH_PAGES
            for page in auth_pages:
                page = dict(page)
                if not logged_in:
                    page["auth_state"] = "auth_required_but_login_failed"
                results.append(capture_page(driver, base_url, out_dir, viewport, width, height, page))
            if logged_in:
                results.extend(capture_submit_workflow(driver, base_url, out_dir, viewport, width, height))
                results.extend(capture_my_workflow(driver, base_url, out_dir, viewport, width, height))
                results.extend(capture_detail_workflow(driver, base_url, out_dir, viewport, width, height))
                results.extend(capture_notification_popover(driver, base_url, out_dir, viewport, width, height))
        finally:
            driver.quit()

    write_report(out_dir, results)
    print(out_dir.resolve())


if __name__ == "__main__":
    main()
