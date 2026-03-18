import React from "react";
import { useNavigate } from "react-router-dom";
import StepIndicator from "../../../components/StepIndicator/StepIndicator";
import { useResume } from "../../../context/ResumeContext";
import type { Experience } from "../../../types/resume";
import "../../../components/shared.css";
import "./experience.css";

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
const BriefcaseIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="2" y="7" width="20" height="14" rx="2" /><path d="M16 7V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v2" />
    <line x1="12" y1="12" x2="12" y2="12" />
  </svg>
);

const ExperiencePage: React.FC = () => {
  const navigate = useNavigate();
  const { resumeData, setResumeData } = useResume();

  const updateExp = (id: string, field: keyof Experience, value: string) => {
    setResumeData((prev) => ({
      ...prev,
      experiences: prev.experiences.map((e) =>
        e.id === id ? { ...e, [field]: value } : e
      ),
    }));
    console.log("RESUME DATA", resumeData)
  };

  const addExp = () => {
    setResumeData((prev) => ({
      ...prev,
      experiences: [
        ...prev.experiences,
        {
          id: `exp-${Date.now()}`,
          jobTitle: "", companyName: "", startDate: "", endDate: "", description: "",
        },
      ],
    }));
  };

  const removeExp = (id: string) => {
    setResumeData((prev) => ({
      ...prev,
      experiences: prev.experiences.filter((e) => e.id !== id),
    }));
  };

  return (
    <div className="rb-page">
      <div className="rb-header">
        <h1>Resume Builder</h1>
        <p>Create your professional resume in minutes</p>
      </div>

      <StepIndicator currentStep={3} />

      <div className="rb-card">
        <h2 className="rb-card-title">Work Experience</h2>
        <p className="rb-card-subtitle">Add your professional experience</p>

        {resumeData.experiences.map((exp, idx) => (
          <div className="rb-entry-card" key={exp.id}>
            <div className="rb-entry-card-header">
              <BriefcaseIcon />
              Experience {idx + 1}
              {resumeData.experiences.length > 1 && (
                <button className="rb-remove-btn" onClick={() => removeExp(exp.id)}>
                  Remove
                </button>
              )}
            </div>

            <div className="rb-row">
              <div className="rb-field">
                <label>Job Title <span className="required">*</span></label>
                <input
                  className="rb-input"
                  placeholder="Software Engineer"
                  value={exp.jobTitle}
                  onChange={(e) => updateExp(exp.id, "jobTitle", e.target.value)}
                />
              </div>
              <div className="rb-field">
                <label>Company Name <span className="required">*</span></label>
                <input
                  className="rb-input"
                  placeholder="Tech Corp"
                  value={exp.companyName}
                  onChange={(e) => updateExp(exp.id, "companyName", e.target.value)}
                />
              </div>
            </div>

            <div className="rb-row">
              <div className="rb-field">
                <label>Start Date <span className="required">*</span></label>
                <input
                  className="rb-input"
                  type="date"
                  value={exp.startDate}
                  onChange={(e) => updateExp(exp.id, "startDate", e.target.value)}
                />
              </div>
              <div className="rb-field">
                <label>End Date <span className="required">*</span></label>
                <input
                  className="rb-input"
                  type="date"
                  value={exp.endDate}
                  onChange={(e) => updateExp(exp.id, "endDate", e.target.value)}
                />
              </div>
            </div>

            <div className="rb-field">
              <label>Job Description <span className="required">*</span></label>
              <textarea
                className="rb-textarea"
                placeholder="Describe your responsibilities and achievements..."
                value={exp.description}
                onChange={(e) => updateExp(exp.id, "description", e.target.value)}
              />
            </div>
          </div>
        ))}

        <button className="rb-add-btn" onClick={addExp}>
          + Add Another Experience
        </button>

        <div className="rb-nav">
          <button className="rb-btn-back" onClick={() => navigate("/resume-builder-agent/personal")}>
            <ArrowLeft /> Back
          </button>
          <button
            className="rb-btn-next"
            onClick={() => navigate("/resume-builder-agent/projects")}
          >
            Next <ArrowRight />
          </button>
        </div>
      </div>
    </div>
  );
};

export default ExperiencePage;