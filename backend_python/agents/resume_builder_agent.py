"""
resume_builder_agent.py
"""

import base64
import json
import re
import html as html_module
import os
import logging
from typing import Optional

from langchain_core.messages import HumanMessage, SystemMessage
from services.llm_service import get_llm

log = logging.getLogger(__name__)


def _e(text: str) -> str:
    return html_module.escape(str(text or ""))


def _fmt_date(raw: str) -> str:
    if not raw:
        return ""
    m = re.match(r"^(\d{4})-(\d{2})", raw)
    if m:
        months = ["","Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        return "%s %s" % (months[int(m.group(2))], m.group(1))
    return raw


def _is_placeholder(val: str) -> bool:
    return not val or val.strip().upper() in ("NA", "N/A", "-", "NONE", "")


# ── LLM polish ───────────────────────────────────────────────────────────────

_POLISH_SYSTEM = """You are a professional resume writer.
Polish the raw resume content and return ONLY a valid JSON object.
No markdown, no code fences, no explanation.

Rules:
- summary     : 2-3 punchy sentences.
- experiences : 2-4 bullet strings per entry, starting with action verbs.
- projects    : 1-2 clean sentences per entry.
- Never invent facts or change names, dates, companies, or skills.

Schema (arrays must match input order):
{
  "summary": "...",
  "experiences": [{"bullets": ["...", "..."]}],
  "projects":    [{"description": "..."}]
}"""


def _polish_content(resume_data: dict) -> dict:
    llm   = get_llm()
    p     = resume_data.get("personal", {})
    exps  = resume_data.get("experiences", [])
    projs = resume_data.get("projects", [])

    exp_input = [
        {"jobTitle": e.get("jobTitle",""), "companyName": e.get("companyName",""), "description": e.get("description","")}
        for e in exps if e.get("jobTitle") or e.get("companyName")
    ]
    proj_input = [
        {"title": pr.get("title",""), "description": pr.get("description","")}
        for pr in projs if pr.get("title") and not _is_placeholder(pr.get("title",""))
    ]

    prompt = (
        "SUMMARY:\n" + p.get("summary","") + "\n\n"
        "EXPERIENCES:\n" + json.dumps(exp_input, indent=2) + "\n\n"
        "PROJECTS:\n" + json.dumps(proj_input, indent=2) + "\n\nReturn JSON now."
    )

    try:
        resp = llm.invoke([SystemMessage(content=_POLISH_SYSTEM), HumanMessage(content=prompt)])
        raw = resp.content.strip()
        raw = re.sub(r"^```json\s*", "", raw, flags=re.IGNORECASE)
        raw = re.sub(r"^```\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
        return json.loads(raw)
    except Exception:
        return {
            "summary": p.get("summary",""),
            "experiences": [{"bullets": [e.get("description","")]} for e in exp_input],
            "projects":    [{"description": pr.get("description","")} for pr in proj_input],
        }


# ── HTML building blocks (plain string concat — zero f-string nesting) ────────

def _sidebar_label(text):
    return (
        "<div style='font-family:Arial,sans-serif;font-weight:bold;"
        "font-size:8px;letter-spacing:2px;text-transform:uppercase;"
        "color:rgba(255,255,255,0.4);margin-bottom:8px;'>"
        + text + "</div>"
    )

def _sidebar_divider():
    return "<div style='height:1px;background:rgba(255,255,255,0.12);margin:14px 0;'></div>"

def _contact_row(label, val):
    if not val:
        return ""
    return (
        "<tr>"
        "<td valign='top' style='font-size:9px;color:rgba(255,255,255,0.45);"
        "padding-right:6px;padding-bottom:6px;white-space:nowrap;"
        "font-family:Arial,sans-serif;'>" + label + "</td>"
        "<td valign='top' style='font-size:10.5px;color:rgba(255,255,255,0.85);"
        "padding-bottom:6px;word-break:break-all;"
        "font-family:Arial,sans-serif;line-height:1.4;'>" + _e(val) + "</td>"
        "</tr>"
    )

def _skill_pill(text):
    return (
        "<span style='display:inline-block;"
        "background:rgba(255,255,255,0.13);color:#fff;"
        "border:1px solid rgba(255,255,255,0.2);border-radius:99px;"
        "padding:3px 9px;font-size:9.5px;font-family:Arial,sans-serif;"
        "margin:2px 2px;'>" + _e(text) + "</span>"
    )

def _section_wrap(title, body):
    if not body.strip():
        return ""
    return (
        "<div style='margin-bottom:20px;'>"
        "<div style='font-family:Georgia,serif;font-weight:bold;font-size:13px;"
        "color:#1e1b4b;padding-left:8px;border-left:3px solid #7c3aed;"
        "margin-bottom:5px;'>" + title + "</div>"
        "<div style='height:1px;background:#e5e7eb;margin-bottom:11px;'></div>"
        + body + "</div>"
    )

def _entry_card(title, sub, date, body):
    date_cell = ""
    if date:
        date_cell = (
            "<td align='right' valign='top' style='font-size:10px;color:#6b7280;"
            "white-space:nowrap;padding-left:8px;padding-top:1px;"
            "font-family:Arial,sans-serif;'>" + _e(date) + "</td>"
        )
    return (
        "<div style='margin-bottom:13px;padding-left:10px;"
        "border-left:2px solid #c4b5fd;'>"
        "<table width='100%' style='border-collapse:collapse;'>"
        "<tr>"
        "<td valign='top' style='font-family:Georgia,serif;font-weight:bold;"
        "font-size:12.5px;color:#1e1b4b;'>" + _e(title) + "</td>"
        + date_cell +
        "</tr>"
        "<tr><td colspan='2' style='font-size:11px;color:#7c3aed;font-weight:bold;"
        "padding-top:2px;font-family:Arial,sans-serif;'>" + _e(sub) + "</td></tr>"
        "</table>"
        + body +
        "</div>"
    )

def _render_exp(exp, pol):
    bullets = pol.get("bullets", [exp.get("description","")])
    lis = "".join(
        "<li style='font-size:11px;color:#374151;line-height:1.65;"
        "margin-bottom:3px;font-family:Arial,sans-serif;'>"
        + _e(b.lstrip("-* ")) + "</li>"
        for b in bullets if b.strip()
    )
    start = _fmt_date(exp.get("startDate",""))
    end   = _fmt_date(exp.get("endDate","")) or "Present"
    date  = (start + " - " + end) if start else end
    body  = "<ul style='padding-left:14px;margin-top:5px;'>" + lis + "</ul>"
    return _entry_card(exp.get("jobTitle",""), exp.get("companyName",""), date, body)

def _render_proj(proj, pol):
    desc = pol.get("description", proj.get("description",""))
    link = proj.get("link","")
    link_html = ""
    if link:
        link_html = (
            "<div style='font-size:10px;color:#7c3aed;margin-top:3px;"
            "word-break:break-all;font-family:Arial,sans-serif;'>"
            + _e(link) + "</div>"
        )
    body = (
        "<p style='font-size:11px;color:#374151;line-height:1.65;"
        "margin-top:5px;font-family:Arial,sans-serif;'>"
        + _e(desc) + "</p>" + link_html
    )
    return _entry_card(proj.get("title",""), proj.get("organization",""), "", body)

def _render_edu(edu):
    sy = edu.get("startYear","")
    ey = edu.get("endYear","")
    date = ((sy + " - " + ey).strip(" -")) if (sy or ey) else ""
    if edu.get("gpa"):
        date += " | GPA: " + _e(edu["gpa"])
    return _entry_card(edu.get("degree",""), edu.get("institution",""), date, "")


# ── Main HTML generator ───────────────────────────────────────────────────────

def generate_resume_html(resume_data: dict, photo_base64: Optional[str] = None) -> str:
    polished  = _polish_content(resume_data)
    p         = resume_data.get("personal", {})
    exps      = [e  for e  in resume_data.get("experiences",[]) if e.get("jobTitle") or e.get("companyName")]
    projs     = [pr for pr in resume_data.get("projects",[])    if pr.get("title") and not _is_placeholder(pr.get("title",""))]
    edus      = [ed for ed in resume_data.get("educations",[])  if ed.get("degree") or ed.get("institution")]
    skills    = [s  for s  in resume_data.get("skills",[])      if s and s.strip()]
    pol_exps  = polished.get("experiences",[])
    pol_projs = polished.get("projects",[])
    pol_sum   = polished.get("summary", p.get("summary",""))

    # Photo
    photo_html = ""
    if photo_base64:
        b64 = photo_base64.split(",")[-1]
        photo_html = (
            "<div style='text-align:center;margin-bottom:16px;'>"
            "<img src='data:image/jpeg;base64," + b64 + "' "
            "style='width:86px;height:86px;border-radius:50%;object-fit:cover;"
            "border:3px solid rgba(255,255,255,0.85);display:inline-block;'/>"
            "</div>"
        )

    # Contact table
    contact_rows = (
        _contact_row("Email",    p.get("email",""))
        + _contact_row("Phone",  p.get("phone",""))
        + _contact_row("City",   p.get("location",""))
        + _contact_row("in",     p.get("linkedin",""))
        + _contact_row("Web",    p.get("portfolio",""))
    )
    contact_html = (
        "<table style='border-collapse:collapse;width:100%;'>"
        + contact_rows +
        "</table>"
    )

    # Skills
    skills_html = ""
    if skills:
        pills = "".join(_skill_pill(s) for s in skills)
        skills_html = (
            _sidebar_divider()
            + _sidebar_label("SKILLS")
            + "<div style='line-height:2;'>" + pills + "</div>"
        )

    # Right column sections
    summary_sec = _section_wrap(
        "Professional Summary",
        "<p style='font-size:11.5px;color:#374151;line-height:1.75;"
        "font-family:Arial,sans-serif;'>" + _e(pol_sum) + "</p>"
        if pol_sum else ""
    )
    exp_sec  = _section_wrap("Work Experience",
        "".join(_render_exp(e, pol_exps[i] if i < len(pol_exps) else {}) for i, e in enumerate(exps)))
    proj_sec = _section_wrap("Projects &amp; Certifications",
        "".join(_render_proj(pr, pol_projs[i] if i < len(pol_projs) else {}) for i, pr in enumerate(projs)))
    edu_sec  = _section_wrap("Education",
        "".join(_render_edu(ed) for ed in edus))

    # ── CSS: same rules for both browser preview and Playwright PDF ──────────
    # Key decisions:
    #  - No width/height constraints on html/body (Playwright sets page width)
    #  - Table layout with pixel widths only (no percentages in sidebar)
    #  - All colours use hex, not rgba() — more reliable across renderers
    #  - Google Fonts loaded via @import — Playwright waits for networkidle
    css = (
        "@import url('https://fonts.googleapis.com/css2?"
        "family=Outfit:wght@400;600;700;800"
        "&family=DM+Sans:wght@400;500&display=swap');\n"
        "*, *::before, *::after { box-sizing:border-box; margin:0; padding:0; }\n"
        "html { background:#fff; }\n"
        "body { font-family:Arial,sans-serif; background:#fff; margin:0; padding:0; }\n"
        "ul { list-style-type:disc; }\n"
        "table { border-collapse:collapse; }\n"
        "@media print {\n"
        "  @page { size:A4; margin:0; }\n"
        "  html, body { width:210mm; }\n"
        "  body { -webkit-print-color-adjust:exact; print-color-adjust:exact; }\n"
        "}\n"
    )

    sidebar_td = (
        "<td style='"
        "width:195px;"
        "background-color:#1e1b4b;"
        "padding:26px 16px;"
        "vertical-align:top;"
        "'>\n"
        + photo_html
        + "<div style='text-align:center;margin-bottom:16px;'>"
          "<div style='font-family:Georgia,serif;font-weight:bold;font-size:17px;"
          "color:#ffffff;letter-spacing:-0.02em;line-height:1.25;'>"
        + _e(p.get("fullName", "Your Name"))
        + "</div></div>\n"
        + _sidebar_divider()
        + _sidebar_label("CONTACT")
        + contact_html
        + skills_html
        + "</td>\n"
    )

    main_td = (
        "<td style='"
        "padding:26px 24px;"
        "vertical-align:top;"
        "background-color:#ffffff;"
        "'>\n"
        + summary_sec + exp_sec + proj_sec + edu_sec
        + "</td>\n"
    )

    html = (
        "<!DOCTYPE html>\n"
        "<html lang='en'>\n"
        "<head>\n"
        "<meta charset='UTF-8'/>\n"
        "<meta name='viewport' content='width=device-width,initial-scale=1'/>\n"
        "<title>" + _e(p.get("fullName", "Resume")) + "</title>\n"
        "<style>\n" + css + "</style>\n"
        "</head>\n"
        "<body>\n"
        "<table style='width:794px;border-collapse:collapse;table-layout:fixed;'>\n"
        "<colgroup><col style='width:195px;'/><col style='width:599px;'/></colgroup>\n"
        "<tr valign='top'>\n"
        + sidebar_td
        + main_td
        + "</tr>\n"
        "</table>\n"
        "</body>\n"
        "</html>"
    )

    return html



# ── PDF conversion ────────────────────────────────────────────────────────────

def _find_wkhtmltopdf() -> Optional[str]:
    import shutil
    env_path = os.environ.get("WKHTMLTOPDF_PATH","").strip()
    if env_path and os.path.isfile(env_path):
        return env_path
    found = shutil.which("wkhtmltopdf")
    if found:
        return found
    if os.name == "nt":
        for c in [
            r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe",
            r"C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe",
            r"C:\wkhtmltopdf\bin\wkhtmltopdf.exe",
        ]:
            if os.path.isfile(c):
                return c
    return None


def create_pdf(html_content: str) -> bytes:
    # Option 1: Playwright
    try:
        from playwright.sync_api import sync_playwright  # type: ignore
        log.info("PDF: Playwright/Chromium")
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            # Viewport exactly 794px = A4 width at 96dpi
            # Height is large so nothing gets clipped before PDF export
            page = browser.new_page(viewport={"width": 794, "height": 1600})
            page.set_content(html_content, wait_until="networkidle")
            # Wait for Google Fonts to finish rendering
            page.wait_for_timeout(1200)
            # Get the actual rendered content height
            content_height = page.evaluate(
                "document.body.scrollHeight"
            )
            pdf_bytes = page.pdf(
                # Use exact pixel dimensions — matches what the browser renders
                width="794px",
                height=str(content_height) + "px",
                margin={"top":"0","right":"0","bottom":"0","left":"0"},
                print_background=True,
            )
            browser.close()
        return pdf_bytes
    except ImportError:
        log.warning("Playwright not installed, trying pdfkit")
    except Exception as exc:
        log.warning("Playwright failed (%s), trying pdfkit", exc)

    # Option 2: pdfkit
    try:
        import pdfkit  # type: ignore
        wk = _find_wkhtmltopdf()
        if not wk:
            raise FileNotFoundError("wkhtmltopdf not found")
        log.info("PDF: wkhtmltopdf at %s", wk)
        cfg  = pdfkit.configuration(wkhtmltopdf=wk)
        opts = {
            "page-size":"A4","margin-top":"0mm","margin-right":"0mm",
            "margin-bottom":"0mm","margin-left":"0mm","encoding":"UTF-8",
            "enable-local-file-access":"","background":"",
            "print-media-type":"","javascript-delay":"500","quiet":"",
        }
        return pdfkit.from_string(html_content, False, options=opts, configuration=cfg)
    except ImportError:
        pass
    except Exception as exc:
        log.error("pdfkit failed: %s", exc)

    raise RuntimeError(
        "No PDF engine available. "
        "Run: pip install playwright && playwright install chromium"
    )


def encode_photo(file_bytes: bytes) -> str:
    return base64.b64encode(file_bytes).decode("utf-8")