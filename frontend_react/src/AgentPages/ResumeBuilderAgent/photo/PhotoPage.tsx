import React, { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import StepIndicator from "../../../components/StepIndicator/StepIndicator";
import { useResume } from "../../../context/ResumeContext";
import "../../../components/shared.css";
import "./photo.css";

const UploadIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
    <polyline points="17 8 12 3 7 8" />
    <line x1="12" y1="3" x2="12" y2="15" />
  </svg>
);

const AvatarIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
    <circle cx="12" cy="7" r="4" />
  </svg>
);

const PhotoPage: React.FC = () => {
  const navigate = useNavigate();
  const { resumeData, setResumeData } = useResume();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isDragOver, setIsDragOver] = useState(false);

  const handleFile = (file: File) => {
    if (!file.type.startsWith("image/")) return;
    const reader = new FileReader();
    reader.onload = (e) => {
      const result = e.target?.result as string;
      setResumeData((prev) => ({ ...prev, photo: result }));
    };
    reader.readAsDataURL(file);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
  };

  const handleConfirm = () => navigate("/resume-builder-agent/personal");
  const handleSkip = () => {
    setResumeData((prev) => ({ ...prev, photo: null }));
    navigate("/resume-builder-agent/personal");
  };

  return (
    <div className="rb-page">
      <div className="rb-header">
        <h1>Resume Builder</h1>
        <p>Create your professional resume in minutes</p>
      </div>

      <StepIndicator currentStep={1} />

      <div className="rb-card">
        <h2 className="rb-card-title">Upload Your Profile Photo</h2>
        <p className="rb-card-subtitle">Add a professional photo to your resume (optional)</p>

        {/* Avatar preview */}
        <div className="photo-avatar-wrap">
          <div className="photo-avatar">
            {resumeData.photo ? (
              <img src={resumeData.photo} alt="Profile" />
            ) : (
              <AvatarIcon />
            )}
          </div>
        </div>

        {/* Dropzone */}
        <div
          className={`photo-dropzone ${isDragOver ? "drag-over" : ""}`}
          onClick={() => fileInputRef.current?.click()}
          onDragOver={(e) => { e.preventDefault(); setIsDragOver(true); }}
          onDragLeave={() => setIsDragOver(false)}
          onDrop={handleDrop}
        >
          <div className="photo-dropzone-icon">
            <UploadIcon />
          </div>
          <p>Drag &amp; drop your photo here</p>
          <span>or click to browse</span>
        </div>

        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          style={{ display: "none" }}
          onChange={handleChange}
        />

        {/* Navigation */}
        <div className="photo-nav">
          <button className="rb-btn-skip" onClick={handleSkip}>
            Skip for Now
          </button>
          <button
            className="rb-btn-next"
            onClick={handleConfirm}
            disabled={!resumeData.photo}
          >
            Confirm Photo
          </button>
        </div>
      </div>
    </div>
  );
};

export default PhotoPage;