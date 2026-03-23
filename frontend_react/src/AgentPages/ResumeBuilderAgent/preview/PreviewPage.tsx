import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import StepIndicator from "../../../components/StepIndicator/StepIndicator";
import { useResume } from "../../../context/ResumeContext";
import { useAuth } from "../../../context/AuthContext";
import { useAPI } from "../../../context/APIContext";
import "../../../components/shared.css";
import "./preview.css";

const EditIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
    <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
  </svg>
);

const DownloadIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
    <polyline points="7 10 12 15 17 10" />
    <line x1="12" y1="15" x2="12" y2="3" />
  </svg>
);


// ─────────────────────────────────────────────────────────────────────────────

const PreviewPage: React.FC = () => {
  const navigate = useNavigate();
  const { resumeData, generatedHtml, setGeneratedHtml, isGenerating, setIsGenerating } = useResume();
  const [isDownloading, setIsDownloading] = useState(false);

  const {user, token} = useAuth()
  const {url} = useAPI()

  // Fetch the AI-generated resume HTML from the backend on mount
  useEffect(() => {
    if (generatedHtml) return; // already generated — don't re-fetch

    const generate = async () => {
      setIsGenerating(true);
      try {
        const res = await fetch(`${url}api/resume-builder-agent/generate`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`
          },
          body: JSON.stringify({ resume_data: resumeData }),
        });
        if (!res.ok) {
          const err = await res.json().catch(() => ({}));
          throw new Error(err.detail ?? `HTTP ${res.status}`);
        }
        const data = await res.json();
        setGeneratedHtml(data.html);
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : String(err);
        setGeneratedHtml(
          `<div style="padding:2rem;color:#dc2626;font-family:sans-serif;">
            <strong>Failed to generate resume:</strong><br/>${msg}
           </div>`
        );
      } finally {
        setIsGenerating(false);
      }
    };

    generate();
  }, []);

  const handleDownload = async () => {
    if (!generatedHtml) return;
    setIsDownloading(true);
    try {
      const res = await fetch(`${url}api/resume-builder-agent/download`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`
          },
        body: JSON.stringify({ html_content: generatedHtml }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const blob = await res.blob();
      const contentType = res.headers.get("Content-Type") ?? "";
      const isPdf = contentType.includes("pdf");
      const filename = isPdf ? "resume.pdf" : "resume.html";
      const urls = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = urls;
      a.download = filename;
      a.click();
      URL.revokeObjectURL(urls);
    } catch (err: unknown) {
      alert(`Download failed: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setIsDownloading(false);
    }
  };

  const handleEdit = () => {
    setGeneratedHtml("");
    navigate("/resume-builder-agent/skills");
  };

  return (
    <div className="rb-page">
      <div className="rb-header">
        <h1>Resume Builder</h1>
        <p>Create your professional resume in minutes</p>
      </div>

      <StepIndicator currentStep={7} />

      <div className="rb-card preview-card">
        <h2 className="preview-title">Your Resume is Ready!</h2>
        <p className="preview-subtitle">Preview and download your professional resume</p>

        <div className="preview-frame-wrap">
          {isGenerating ? (
            <div className="preview-generating">
              <div className="preview-spinner" />
              <p>Designing your resume...</p>
              <span>Our AI is crafting a beautiful layout just for you.</span>
            </div>
          ) : (
            <iframe
              className="preview-iframe"
              srcDoc={generatedHtml}
              title="Resume Preview"
              sandbox="allow-same-origin"
            />
          )}
        </div>

        <div className="preview-actions">
          <button className="preview-btn-edit" onClick={handleEdit}>
            <EditIcon /> Edit Details
          </button>
          <button
            className="preview-btn-download"
            onClick={handleDownload}
            disabled={!generatedHtml || isDownloading}
          >
            <DownloadIcon />
            {isDownloading ? "Preparing..." : "Download PDF"}
          </button>
        </div>
      </div>
    </div>
  );
};

export default PreviewPage;