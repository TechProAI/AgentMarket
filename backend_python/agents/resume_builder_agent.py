"""
resume_builder_agent.py
=======================
Layout pixel-matched to a clean single-column professional resume with:

HEADER
  - Full name  (large, bold, centered)
  - Job title  (medium, centered, below name)
  - Contact bar: 📍 City, Country  |  ✉ email  |  phone  |  Portfolio  |  LinkedIn
    (all on one line, separated by  |  pipes, centered)
  - Thin horizontal rule beneath the header

SECTIONS  (each has an ALL-CAPS bold heading + full-width bottom rule)
  1. Professional Summary   — justified paragraph
  2. Technical Skills       — bullet list of  "Category: item1, item2, ..."  lines
  3. Experience             — entries: title (left) + date range (right)
                                        company, city (left)
                                        bullet list
  4. Projects & Certs       — same entry format, no date column
  5. Education              — degree (left) + years + CGPA (right)
                              institution, city below
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


# ── tiny helpers ─────────────────────────────────────────────────────────────

def _e(v) -> str:
    return html_module.escape(str(v or ""))


def _fmt_date(raw: str) -> str:
    if not raw:
        return ""
    m = re.match(r"^(\d{4})-(\d{2})", raw)
    if m:
        months = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        return f"{months[int(m.group(2))]} {m.group(1)}"
    return raw


def _is_placeholder(v: str) -> bool:
    return not v or v.strip().upper() in ("NA", "N/A", "-", "NONE", "")


# ════════════════════════════════════════════════════════════════════════════
#  LLM POLISH
# ════════════════════════════════════════════════════════════════════════════

_POLISH_SYSTEM = """\
You are an elite resume writer with 15+ years of experience helping candidates
land roles at top companies. Your rewrites consistently pass ATS filters and
impress senior recruiters.

Return ONLY a valid JSON object — no markdown fences, no code blocks, no preamble.
Begin your response with '{' and end with '}'.

━━━━━━━━━━━━━━━━  SUMMARY RULES  ━━━━━━━━━━━━━━━━
Write 3–4 sentences following this exact structure:

  S1 – Identity: experience level + domain + primary tech stack
       e.g. "Results-driven Frontend Developer with 4 years of experience designing
       scalable web applications using React.js, TypeScript, and JavaScript (ES6+)."

  S2 – Core competencies: 4–5 specific technical strengths
       e.g. "Proficient in responsive UI/UX design, API integration, Redux Toolkit
       state management, and performance optimization."

  S3 – Work style / methodology
       e.g. "Experienced in Agile/Scrum environments, collaborating with
       cross-functional teams to deliver high-quality software solutions."

  S4 (optional) – Additional value or specialisation
       e.g. "Adept at React Hooks, unit testing with Jest, and ensuring
       cross-browser compatibility and accessibility standards."

NEVER use: first-person pronouns · "passionate" · "hardworking" · "team player"
           "detail-oriented" · "Seeking a role" · "Motivated professional"

━━━━━━━━━━━━━━━━  EXPERIENCE BULLET RULES  ━━━━━━━━━━━━━━━━
Write 3–6 bullets per entry (scale to tenure and seniority).

Every bullet MUST:
  • Start with a strong past-tense action verb (from the list below)
  • Follow CAR formula  ➜  Context → Action → Result
  • Include a quantified result where the input data allows
    (If no number is given use relative impact: "by ~40%", "significantly",
     "for 1,000+ users")
  • Stay under 140 characters
  • Never repeat the opening verb back-to-back

Approved verbs (vary them — never reuse within one entry):
  Developed · Designed · Built · Engineered · Architected · Implemented ·
  Integrated · Delivered · Optimised · Reduced · Increased · Automated ·
  Migrated · Launched · Deployed · Improved · Refactored · Collaborated ·
  Mentored · Led · Spearheaded · Managed · Streamlined · Contributed ·
  Utilised · Conducted · Performed · Translated · Ensured · Coordinated

BAD:  "Worked on backend APIs and helped fix some bugs"
GOOD: "Engineered 12 REST APIs in Node.js, cutting avg response time by 35%
       and supporting 50 K daily active users"

━━━━━━━━━━━━━━━━  PROJECT DESCRIPTION RULES  ━━━━━━━━━━━━━━━━
Exactly 2 sentences:
  S1 – What it is + core tech stack
  S2 – Scale, outcome, or the most impressive technical achievement

Never use: "a useful tool" · "helped users" · "various features" · vague adjectives

━━━━━━━━━━━━━━━━  HARD CONSTRAINTS  ━━━━━━━━━━━━━━━━
  ✗ Never invent companies, dates, names, titles, or technologies
  ✗ Never reorder experiences or projects
  ✗ Never add or remove JSON keys
  ✗ Never produce empty strings — preserve raw input if truly empty
  ✗ Output arrays must match input arrays exactly in length and order

━━━━━━━━━━━━━━━━  OUTPUT SCHEMA  ━━━━━━━━━━━━━━━━
{
  "summary": "string",
  "experiences": [ { "bullets": ["string", "string", "string"] } ],
  "projects":    [ { "description": "string" } ]
}"""


def _polish_content(resume_data: dict) -> dict:
    llm   = get_llm()
    p     = resume_data.get("personal", {})
    exps  = resume_data.get("experiences", [])
    projs = resume_data.get("projects", [])

    exp_input = [
        {
            "jobTitle":    e.get("jobTitle", ""),
            "companyName": e.get("companyName", ""),
            "startDate":   e.get("startDate", ""),
            "endDate":     e.get("endDate", ""),
            "description": e.get("description", ""),
        }
        for e in exps if e.get("jobTitle") or e.get("companyName")
    ]
    proj_input = [
        {"title": pr.get("title", ""), "description": pr.get("description", "")}
        for pr in projs
        if pr.get("title") and not _is_placeholder(pr.get("title", ""))
    ]

    user_prompt = (
        "Polish the resume content below following your system rules exactly.\n\n"
        "=== RAW SUMMARY ===\n"
        + (p.get("summary") or "(none provided)") + "\n\n"
        "=== RAW EXPERIENCE ===\n"
        + json.dumps(exp_input, indent=2) + "\n\n"
        "=== RAW PROJECTS ===\n"
        + json.dumps(proj_input, indent=2) + "\n\n"
        "Instructions:\n"
        "1. Extract any implied metrics from descriptions and make them explicit.\n"
        "2. If a description is vague, infer measurable impact from the title/company context.\n"
        "3. Every bullet must read like a senior professional with proven results wrote it.\n"
        "4. Preserve ALL facts: company names, dates, product names, technologies.\n"
        "5. Return ONLY the JSON object. First character must be '{'.\n"
    )

    try:
        resp = llm.invoke([
            SystemMessage(content=_POLISH_SYSTEM),
            HumanMessage(content=user_prompt),
        ])
        raw = resp.content.strip()
        raw = re.sub(r"^```json\s*", "", raw, flags=re.IGNORECASE)
        raw = re.sub(r"^```\s*",     "", raw)
        raw = re.sub(r"\s*```$",     "", raw)
        return json.loads(raw)
    except Exception as exc:
        log.warning("LLM polish failed (%s) — using raw content", exc)
        return {
            "summary": p.get("summary", ""),
            "experiences": [{"bullets": [e.get("description", "")]} for e in exp_input],
            "projects":    [{"description": pr.get("description", "")} for pr in proj_input],
        }


# ════════════════════════════════════════════════════════════════════════════
#  CSS  —  matched pixel-for-pixel to the reference PDF
# ════════════════════════════════════════════════════════════════════════════

_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Calibri:wght@400;700&display=swap');

/* ── Reset ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body              { background: #fff; }

/* ── Page ── */
body {
    font-family: Calibri, 'Segoe UI', Arial, sans-serif;
    font-size: 10.5pt;
    color: #000;
    background: #fff;
}
.page {
    width: 794px;
    min-height: 1122px;
    margin: 0 auto;
    padding: 36px 52px 48px 52px;
    background: #fff;
}

/* ── Header ── */
.hdr            { text-align: center; margin-bottom: 0; }
.hdr-name       {
    font-size: 22pt;
    font-weight: 700;
    letter-spacing: 0.02em;
    line-height: 1.15;
    color: #000;
    margin-bottom: 3px;
}
.hdr-title      {
    font-size: 11pt;
    font-weight: 400;
    color: #222;
    margin-bottom: 5px;
}
.hdr-contacts   {
    font-size: 9.5pt;
    color: #111;
    margin-bottom: 0;
    line-height: 1.7;
}
.hdr-sep        { color: #555; margin: 0 7px; }
.hdr-rule       {
    border: none;
    border-top: 1.5px solid #000;
    margin-top: 7px;
    margin-bottom: 14px;
}

/* ── Section ── */
.sec            { margin-bottom: 14px; }
.sec-heading    {
    font-size: 11pt;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.03em;
    color: #000;
    padding-bottom: 2px;
    border-bottom: 1.2px solid #000;
    margin-bottom: 8px;
}

/* ── Entry (experience / education / project) ── */
.entry          { margin-bottom: 10px; }
.entry-row      {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
}
.entry-title    { font-weight: 700; font-size: 10.5pt; color: #000; }
.entry-date     {
    font-size: 9.5pt;
    color: #111;
    white-space: nowrap;
    padding-left: 14px;
    flex-shrink: 0;
}
.entry-company  {
    font-size: 10pt;
    color: #111;
    margin-bottom: 4px;
}

/* ── Bullet list ── */
.blist          { padding-left: 20px; margin: 3px 0 0 0; list-style-type: disc; }
.blist li       {
    font-size: 10pt;
    color: #000;
    line-height: 1.6;
    margin-bottom: 2px;
}

/* ── Summary text ── */
.summary-p      {
    font-size: 10pt;
    color: #000;
    line-height: 1.7;
    text-align: justify;
}

/* ── Skills ── */
.skills-row     {
    font-size: 10pt;
    color: #000;
    line-height: 1.65;
    padding-left: 20px;
    position: relative;
}
.skills-row::before {
    content: "●";
    position: absolute;
    left: 4px;
    color: #000;
    font-size: 9pt;
}

/* ── Education ── */
.edu-degree     { font-weight: 700; font-size: 10.5pt; color: #000; }
.edu-sub        { font-size: 10pt; color: #111; margin-top: 1px; }

/* ── Print ── */
@media print {
    @page      { size: A4; margin: 0; }
    html, body { width: 210mm; }
    body       { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    .page      { padding: 32px 48px 44px 48px; }
}
"""


# ════════════════════════════════════════════════════════════════════════════
#  HTML BUILDERS
# ════════════════════════════════════════════════════════════════════════════

def _contact_bar(p: dict) -> str:
    """
    Produces:  📍 Bangalore, India  |  ✉ email@x.com  |  +91 9999  |  Portfolio  |  LinkedIn
    Matches the reference PDF header exactly.
    """
    parts = []

    loc = p.get("location", "").strip()
    if loc:
        parts.append("📍 " + _e(loc))

    email = p.get("email", "").strip()
    if email:
        parts.append("✉&thinsp;" + _e(email))

    phone = p.get("phone", "").strip()
    if phone:
        parts.append(_e(phone))

    portfolio = p.get("portfolio", "").strip()
    if portfolio:
        # show as hyperlink label "Portfolio"
        parts.append("<a href='" + _e(portfolio) + "' style='color:#000;text-decoration:underline;'>Portfolio</a>")

    linkedin = p.get("linkedin", "").strip()
    if linkedin:
        parts.append("<a href='" + _e(linkedin) + "' style='color:#000;text-decoration:underline;'>LinkedIn</a>")

    sep = "<span class='hdr-sep'>|</span>"
    return (
        "<div class='hdr-contacts'>"
        + sep.join(parts)
        + "</div>"
    )


def _section(title: str, body: str) -> str:
    if not body.strip():
        return ""
    return (
        "<div class='sec'>"
        "<div class='sec-heading'>" + _e(title) + "</div>"
        + body
        + "</div>"
    )


# ── Summary ──────────────────────────────────────────────────────────────────

def _render_summary(text: str) -> str:
    return "<p class='summary-p'>" + _e(text) + "</p>" if text else ""


# ── Skills ───────────────────────────────────────────────────────────────────

def _render_skills(skills: list) -> str:
    """
    Each skill string is rendered as a bullet row.
    Supports both:
      • Flat:       "React.js, TypeScript, HTML5"
      • Categorised: "Frontend Technologies: React.js, TypeScript, HTML5"
    """
    if not skills:
        return ""
    rows = ""
    for s in skills:
        if s.strip():
            rows += "<div class='skills-row'>" + _e(s.strip()) + "</div>"
    return rows


# ── Experience ───────────────────────────────────────────────────────────────

def _render_exp(exp: dict, pol: dict) -> str:
    raw = pol.get("bullets") or []
    bullets = [b for b in raw if b.strip()] or [exp.get("description", "")]

    start = _fmt_date(exp.get("startDate", ""))
    end   = _fmt_date(exp.get("endDate",   "")) or "Present"
    date  = (start + " – " + end) if start else end

    company  = exp.get("companyName", "").strip()
    location = exp.get("location",    "").strip()
    co_line  = ", ".join(filter(None, [company, location]))

    lis = "".join(
        "<li>" + _e(b.lstrip("-*•· ")) + "</li>"
        for b in bullets if b.strip()
    )

    return (
        "<div class='entry'>"

        # Row 1 — Job title | Date
        "<div class='entry-row'>"
        "<span class='entry-title'>" + _e(exp.get("jobTitle", "")) + "</span>"
        + ("<span class='entry-date'>" + _e(date) + "</span>" if date else "")
        + "</div>"

        # Row 2 — Company, Location
        + ("<div class='entry-company'>" + _e(co_line) + "</div>" if co_line else "")

        # Bullet list
        + "<ul class='blist'>" + lis + "</ul>"

        "</div>"
    )


# ── Projects / Certs ─────────────────────────────────────────────────────────

def _render_proj(proj: dict, pol: dict) -> str:
    desc  = (pol.get("description") or proj.get("description", "")).strip()
    title = proj.get("title",        "").strip()
    org   = proj.get("organization", "").strip()
    link  = proj.get("link",         "").strip()

    link_html = ""
    if link:
        link_html = (
            "<div style='font-size:9.5pt;color:#333;margin-top:2px;"
            "word-break:break-all;'>" + _e(link) + "</div>"
        )

    return (
        "<div class='entry'>"
        "<div class='entry-row'>"
        "<span class='entry-title'>" + _e(title) + "</span>"
        "</div>"
        + ("<div class='entry-company'>" + _e(org) + "</div>" if org else "")
        + ("<p style='font-size:10pt;color:#000;line-height:1.6;margin-top:3px;'>"
           + _e(desc) + "</p>" if desc else "")
        + link_html
        + "</div>"
    )


# ── Education ────────────────────────────────────────────────────────────────

def _render_edu(edu: dict) -> str:
    sy   = edu.get("startYear", "").strip()
    ey   = edu.get("endYear",   "").strip()
    date = (sy + "–" + ey) if (sy and ey) else (sy or ey)

    gpa  = edu.get("gpa", "").strip()
    gpa_html = (" | CGPA: " + _e(gpa) + " / 10") if gpa else ""

    degree  = edu.get("degree",      "").strip()
    inst    = edu.get("institution", "").strip()
    field   = edu.get("fieldOfStudy","").strip()
    city    = edu.get("city",        "").strip()

    # institution sub-line: e.g. "Madras Institute of Technology, Anna University, Chennai"
    sub_parts = [x for x in [inst, city] if x]
    sub_line  = ", ".join(sub_parts)

    # degree line might include field of study
    degree_display = degree
    if field and field.lower() not in degree.lower():
        degree_display = degree + " – " + field

    return (
        "<div class='entry'>"

        # Row 1 — Degree | Years + CGPA
        "<div class='entry-row'>"
        "<span class='edu-degree'>" + _e(degree_display) + "</span>"
        + (
            "<span class='entry-date'>" + _e(date) + _e(gpa_html) + "</span>"
            if (date or gpa) else ""
        )
        + "</div>"

        # Row 2 — Institution
        + ("<div class='edu-sub'>" + _e(sub_line) + "</div>" if sub_line else "")

        + "</div>"
    )


# ════════════════════════════════════════════════════════════════════════════
#  MAIN GENERATOR
# ════════════════════════════════════════════════════════════════════════════

def generate_resume_html(resume_data: dict, photo_base64: Optional[str] = None) -> str:
    """
    photo_base64 is accepted for API compatibility but not rendered
    (single-column layout does not include a photo).
    """
    polished = _polish_content(resume_data)
    p        = resume_data.get("personal", {})

    exps   = [e  for e  in resume_data.get("experiences", [])
              if  e.get("jobTitle") or e.get("companyName")]
    projs  = [pr for pr in resume_data.get("projects",    [])
              if  pr.get("title") and not _is_placeholder(pr.get("title", ""))]
    edus   = [ed for ed in resume_data.get("educations",  [])
              if  ed.get("degree") or ed.get("institution")]
    skills = [s  for s  in resume_data.get("skills",      []) if s and s.strip()]

    pol_exps  = polished.get("experiences", [])
    pol_projs = polished.get("projects",    [])
    pol_sum   = polished.get("summary",     p.get("summary", ""))

    # Derive job-title subtitle from most recent role
    header_subtitle = exps[0].get("jobTitle", "") if exps else ""

    # ── Header ───────────────────────────────────────────────────────────────
    header_html = (
        "<div class='hdr'>"
        "<div class='hdr-name'>" + _e(p.get("fullName", "Your Name")) + "</div>"
        + ("<div class='hdr-title'>" + _e(header_subtitle) + "</div>"
           if header_subtitle else "")
        + _contact_bar(p)
        + "</div>"
        "<hr class='hdr-rule'/>"
    )

    # ── Body sections ────────────────────────────────────────────────────────
    summary_sec = _section(
        "Professional Summary",
        _render_summary(pol_sum),
    )

    skills_sec = _section(
        "Technical Skills",
        _render_skills(skills),
    )

    exp_sec = _section(
        "Experience",
        "".join(
            _render_exp(e, pol_exps[i] if i < len(pol_exps) else {})
            for i, e in enumerate(exps)
        ),
    )

    proj_sec = _section(
        "Projects & Certifications",
        "".join(
            _render_proj(pr, pol_projs[i] if i < len(pol_projs) else {})
            for i, pr in enumerate(projs)
        ),
    )

    edu_sec = _section(
        "Education",
        "".join(_render_edu(ed) for ed in edus),
    )

    # ── Full HTML ─────────────────────────────────────────────────────────────
    return (
        "<!DOCTYPE html>\n"
        "<html lang='en'>\n"
        "<head>\n"
        "  <meta charset='UTF-8'/>\n"
        "  <meta name='viewport' content='width=device-width,initial-scale=1'/>\n"
        "  <title>" + _e(p.get("fullName", "Resume")) + "</title>\n"
        "  <style>" + _CSS + "</style>\n"
        "</head>\n"
        "<body>\n"
        "  <div class='page'>\n"
        + header_html
        + summary_sec
        + skills_sec
        + exp_sec
        + proj_sec
        + edu_sec
        + "  </div>\n"
        "</body>\n"
        "</html>"
    )


# ════════════════════════════════════════════════════════════════════════════
#  PDF CONVERSION
# ════════════════════════════════════════════════════════════════════════════

def _find_wkhtmltopdf() -> Optional[str]:
    import shutil
    env_path = os.environ.get("WKHTMLTOPDF_PATH", "").strip()
    if env_path and os.path.isfile(env_path):
        return env_path
    found = shutil.which("wkhtmltopdf")
    if found:
        return found
    if os.name == "nt":
        for c in [
            r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe",
            r"C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe",
        ]:
            if os.path.isfile(c):
                return c
    return None


def create_pdf(html_content: str) -> bytes:
    # ── Option 1: Playwright / Chromium  (preferred — renders fonts perfectly) ──
    try:
        from playwright.sync_api import sync_playwright  # type: ignore
        log.info("PDF: Playwright/Chromium")
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            page    = browser.new_page(viewport={"width": 794, "height": 1122})
            page.set_content(html_content, wait_until="networkidle")
            page.wait_for_timeout(1500)          # let Google Fonts settle
            h = page.evaluate("document.body.scrollHeight")
            pdf = page.pdf(
                width="794px",
                height=str(h) + "px",
                margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
                print_background=True,
            )
            browser.close()
        return pdf
    except ImportError:
        log.warning("Playwright not installed — trying pdfkit")
    except Exception as exc:
        log.warning("Playwright failed (%s) — trying pdfkit", exc)

    # ── Option 2: pdfkit / wkhtmltopdf ──────────────────────────────────────
    try:
        import pdfkit  # type: ignore
        wk = _find_wkhtmltopdf()
        if not wk:
            raise FileNotFoundError("wkhtmltopdf not found")
        log.info("PDF: wkhtmltopdf at %s", wk)
        opts = {
            "page-size":                "A4",
            "margin-top":               "0mm",
            "margin-right":             "0mm",
            "margin-bottom":            "0mm",
            "margin-left":              "0mm",
            "encoding":                 "UTF-8",
            "enable-local-file-access": "",
            "print-media-type":         "",
            "javascript-delay":         "600",
            "quiet":                    "",
        }
        return pdfkit.from_string(
            html_content, False,
            options=opts,
            configuration=pdfkit.configuration(wkhtmltopdf=wk),
        )
    except ImportError:
        pass
    except Exception as exc:
        log.error("pdfkit failed: %s", exc)

    raise RuntimeError(
        "No PDF engine available.\n"
        "Fix: pip install playwright && playwright install chromium"
    )


def encode_photo(file_bytes: bytes) -> str:
    return base64.b64encode(file_bytes).decode("utf-8")