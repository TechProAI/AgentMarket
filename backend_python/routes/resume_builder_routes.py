"""
resume_builder_routes.py
────────────────────────────────────────────────────────────────────────────
All routes are under /api/resume-builder-agent

POST /generate      — accepts the full ResumeData from the frontend form,
                      polishes content via LLM, returns styled HTML
POST /download      — accepts HTML, returns PDF (or HTML fallback)
POST /upload-photo  — accepts multipart image, returns base64
GET  /health        — sanity check
────────────────────────────────────────────────────────────────────────────
"""

import io
import logging
import traceback
from typing import Optional, List

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from auth.security import verify_token

from agents.resume_builder_agent import (
    generate_resume_html,
    create_pdf,
    encode_photo,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/resume-builder-agent", tags=["Resume Builder"])


# ─────────────────────────────────────────────────────────────────────────────
#  Pydantic models — mirror the TypeScript interfaces in resume.ts exactly
# ─────────────────────────────────────────────────────────────────────────────

class Personal(BaseModel):
    fullName: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    linkedin: str = ""
    portfolio: str = ""
    summary: str = ""

class Experience(BaseModel):
    id: str = ""
    jobTitle: str = ""
    companyName: str = ""
    startDate: str = ""
    endDate: str = ""
    description: str = ""

class Project(BaseModel):
    id: str = ""
    title: str = ""
    organization: str = ""
    description: str = ""
    link: str = ""

class Education(BaseModel):
    id: str = ""
    degree: str = ""
    institution: str = ""
    startYear: str = ""
    endYear: str = ""
    gpa: str = ""

class ResumeData(BaseModel):
    """Exact mirror of the frontend ResumeData TypeScript interface."""
    photo: Optional[str] = None          # data URI or base64 string
    personal: Personal = Personal()
    experiences: List[Experience] = []
    projects: List[Project] = []
    educations: List[Education] = []
    skills: List[str] = []

class GenerateRequest(BaseModel):
    resume_data: ResumeData

class DownloadRequest(BaseModel):
    html_content: str


# ─────────────────────────────────────────────────────────────────────────────
#  Routes
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/health")
def health():
    return {"status": "ok"}


@router.post("/generate")
async def generate_resume(request: GenerateRequest, user=Depends(verify_token)):
    """
    Accepts the full structured ResumeData from the frontend form.
    1. LLM polishes the text content.
    2. Python template renders a beautiful two-column HTML resume.
    Returns { html: string }.
    """
    try:
        # Convert Pydantic model → plain dict for the agent
        data = request.resume_data.model_dump()

        # Extract photo from the data dict (it's nested under resume_data.photo)
        photo_b64: Optional[str] = data.pop("photo", None)
        if photo_b64:
            # Strip data URI prefix if the frontend sends a full data: URI
            photo_b64 = photo_b64.split(",")[-1]

        html = generate_resume_html(data, photo_b64)
        return {"html": html}

    except Exception as e:
        logger.error("Resume /generate error:\n%s", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {str(e)}")


@router.post("/download")
async def download_resume(request: DownloadRequest, user=Depends(verify_token)):
    """
    Converts the HTML resume to a PDF and returns it as a downloadable file.
    Falls back to HTML download if WeasyPrint is not installed.
    """
    try:
        pdf_bytes = create_pdf(request.html_content)
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=resume.pdf",
                "Access-Control-Expose-Headers": "Content-Disposition",
            },
        )

    except ImportError:
        logger.warning("WeasyPrint not installed — returning HTML fallback")
        return StreamingResponse(
            io.BytesIO(request.html_content.encode("utf-8")),
            media_type="text/html",
            headers={"Content-Disposition": "attachment; filename=resume.html"},
        )

    except Exception as e:
        logger.error("Resume /download error:\n%s", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {str(e)}")


@router.post("/upload-photo")
async def upload_photo(file: UploadFile = File(...)):
    """
    Accepts a multipart image upload.
    Returns { base64: string, media_type: string }.
    """
    try:
        contents = await file.read()
        encoded = encode_photo(contents)
        media_type = file.content_type or "image/jpeg"
        return {"base64": encoded, "media_type": media_type}

    except Exception as e:
        logger.error("Resume /upload-photo error:\n%s", traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))