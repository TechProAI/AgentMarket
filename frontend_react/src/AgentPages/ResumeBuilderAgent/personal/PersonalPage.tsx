import React from "react";
import { useNavigate } from "react-router-dom";
import StepIndicator from "../../../components/StepIndicator/StepIndicator";
import { useResume } from "../../../context/ResumeContext";
import "../../../components/shared.css";
import "./personal.css";

const ArrowLeft = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <line x1="19" y1="12" x2="5" y2="12" /><polyline points="12 19 5 12 12 5" />
  </svg>
);
const ArrowRight = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <line x1="5" y1="12" x2="19" y2="12" /><polyline points="12 5 19 12 12 19" />
  </svg>
);

const PersonalPage: React.FC = () => {
  const navigate = useNavigate();
  const { resumeData, setResumeData } = useResume();
  const p = resumeData.personal;

  const update = (field: keyof typeof p, value: string) => {
    setResumeData((prev) => ({
      ...prev,
      personal: { ...prev.personal, [field]: value },
    }));
  };

  const isValid = p.fullName.trim() && p.email.trim() && p.phone.trim() && p.location.trim() && p.summary.trim();

  return (
    <div className="rb-page">
      <div className="rb-header">
        <h1>Resume Builder</h1>
        <p>Create your professional resume in minutes</p>
      </div>

      <StepIndicator currentStep={2} />

      <div className="rb-card">
        <h2 className="rb-card-title">Personal Information</h2>
        <p className="rb-card-subtitle">Tell us about yourself</p>

        <div className="personal-form">
          {/* Full Name */}
          <div className="rb-field">
            <label>Full Name <span className="required">*</span></label>
            <input
              className="rb-input"
              type="text"
              placeholder="John Doe"
              value={p.fullName}
              onChange={(e) => update("fullName", e.target.value)}
            />
          </div>

          {/* Email + Phone */}
          <div className="rb-row">
            <div className="rb-field">
              <label>Email Address <span className="required">*</span></label>
              <input
                className="rb-input"
                type="email"
                placeholder="john.doe@example.com"
                value={p.email}
                onChange={(e) => update("email", e.target.value)}
              />
            </div>
            <div className="rb-field">
              <label>Phone Number <span className="required">*</span></label>
              <input
                className="rb-input"
                type="tel"
                placeholder="+1 (555) 123-4567"
                value={p.phone}
                onChange={(e) => update("phone", e.target.value)}
              />
            </div>
          </div>

          {/* Location */}
          <div className="rb-field">
            <label>Location <span className="required">*</span></label>
            <input
              className="rb-input"
              type="text"
              placeholder="San Francisco, USA"
              value={p.location}
              onChange={(e) => update("location", e.target.value)}
            />
          </div>

          {/* LinkedIn + Portfolio */}
          <div className="rb-row">
            <div className="rb-field">
              <label>LinkedIn Profile URL</label>
              <input
                className="rb-input"
                type="url"
                placeholder="linkedin.com/in/johndoe"
                value={p.linkedin}
                onChange={(e) => update("linkedin", e.target.value)}
              />
            </div>
            <div className="rb-field">
              <label>Portfolio / Website URL</label>
              <input
                className="rb-input"
                type="url"
                placeholder="johndoe.com"
                value={p.portfolio}
                onChange={(e) => update("portfolio", e.target.value)}
              />
            </div>
          </div>

          {/* Summary */}
          <div className="rb-field">
            <label>Professional Summary <span className="required">*</span></label>
            <textarea
              className="rb-textarea"
              placeholder="A brief overview of your professional background and career objectives..."
              value={p.summary}
              onChange={(e) => update("summary", e.target.value)}
            />
          </div>
        </div>

        <div className="rb-nav">
          <button className="rb-btn-back" onClick={() => navigate("/resume-builder-agent/photo")}>
            <ArrowLeft /> Back
          </button>
          <button
            className="rb-btn-next"
            onClick={() => navigate("/resume-builder-agent/experience")}
            disabled={!isValid}
          >
            Next <ArrowRight />
          </button>
        </div>
      </div>
    </div>
  );
};

export default PersonalPage;