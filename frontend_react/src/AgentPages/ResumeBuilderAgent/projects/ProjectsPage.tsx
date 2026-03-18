import React from "react";
import { useNavigate } from "react-router-dom";
import StepIndicator from "../../../components/StepIndicator/StepIndicator";
import { useResume } from "../../../context/ResumeContext";
import type { Project } from "../../../types/resume";
import "../../../components/shared.css";
import "./projects.css";

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
const CertIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="8" r="6" /><path d="M15.477 12.89 17 22l-5-3-5 3 1.523-9.11" />
  </svg>
);

const ProjectsPage: React.FC = () => {
  const navigate = useNavigate();
  const { resumeData, setResumeData } = useResume();

  const updateProject = (id: string, field: keyof Project, value: string) => {
    setResumeData((prev) => ({
      ...prev,
      projects: prev.projects.map((p) =>
        p.id === id ? { ...p, [field]: value } : p
      ),
    }));
  };

  const addProject = () => {
    setResumeData((prev) => ({
      ...prev,
      projects: [
        ...prev.projects,
        { id: `proj-${Date.now()}`, title: "", organization: "", description: "", link: "" },
      ],
    }));
  };

  const removeProject = (id: string) => {
    setResumeData((prev) => ({
      ...prev,
      projects: prev.projects.filter((p) => p.id !== id),
    }));
  };

  return (
    <div className="rb-page">
      <div className="rb-header">
        <h1>Resume Builder</h1>
        <p>Create your professional resume in minutes</p>
      </div>

      <StepIndicator currentStep={4} />

      <div className="rb-card">
        <h2 className="rb-card-title">Projects &amp; Certifications</h2>
        <p className="rb-card-subtitle">Showcase your work and achievements</p>

        {resumeData.projects.map((proj, idx) => (
          <div className="rb-entry-card" key={proj.id}>
            <div className="rb-entry-card-header">
              <CertIcon />
              Project / Certification {idx + 1}
              {resumeData.projects.length > 1 && (
                <button className="rb-remove-btn" onClick={() => removeProject(proj.id)}>
                  Remove
                </button>
              )}
            </div>

            <div className="rb-row">
              <div className="rb-field">
                <label>Project / Certification Title <span className="required">*</span></label>
                <input
                  className="rb-input"
                  placeholder="E-commerce Platform"
                  value={proj.title}
                  onChange={(e) => updateProject(proj.id, "title", e.target.value)}
                />
              </div>
              <div className="rb-field">
                <label>Organization / Platform <span className="required">*</span></label>
                <input
                  className="rb-input"
                  placeholder="Coursera, Udemy, Personal"
                  value={proj.organization}
                  onChange={(e) => updateProject(proj.id, "organization", e.target.value)}
                />
              </div>
            </div>

            <div className="rb-field">
              <label>Description <span className="required">*</span></label>
              <textarea
                className="rb-textarea"
                placeholder="Describe the project or certification details..."
                value={proj.description}
                onChange={(e) => updateProject(proj.id, "description", e.target.value)}
              />
            </div>

            <div className="rb-field">
              <label>Project Link (Optional)</label>
              <input
                className="rb-input"
                type="url"
                placeholder="https://github.com/username/project"
                value={proj.link}
                onChange={(e) => updateProject(proj.id, "link", e.target.value)}
              />
            </div>
          </div>
        ))}

        <button className="rb-add-btn" onClick={addProject}>
          + Add Another Project / Certification
        </button>

        <div className="rb-nav">
          <button className="rb-btn-back" onClick={() => navigate("/resume-builder-agent/experience")}>
            <ArrowLeft /> Back
          </button>
          <button
            className="rb-btn-next"
            onClick={() => navigate("/resume-builder-agent/education")}
          >
            Next <ArrowRight />
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProjectsPage;