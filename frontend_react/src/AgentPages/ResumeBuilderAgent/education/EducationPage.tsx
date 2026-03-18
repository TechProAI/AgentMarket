import React from "react";
import { useNavigate } from "react-router-dom";
import StepIndicator from "../../../components/StepIndicator/StepIndicator";
import { useResume } from "../../../context/ResumeContext";
import type { Education } from "../../../types/resume";
import "../../../components/shared.css";
import "./education.css";

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
const GradIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M22 10v6M2 10l10-5 10 5-10 5z" /><path d="M6 12v5c3 3 9 3 12 0v-5" />
  </svg>
);

const EducationPage: React.FC = () => {
  const navigate = useNavigate();
  const { resumeData, setResumeData } = useResume();

  const updateEdu = (id: string, field: keyof Education, value: string) => {
    setResumeData((prev) => ({
      ...prev,
      educations: prev.educations.map((e) =>
        e.id === id ? { ...e, [field]: value } : e
      ),
    }));
  };

  const addEdu = () => {
    setResumeData((prev) => ({
      ...prev,
      educations: [
        ...prev.educations,
        { id: `edu-${Date.now()}`, degree: "", institution: "", startYear: "", endYear: "", gpa: "" },
      ],
    }));
  };

  const removeEdu = (id: string) => {
    setResumeData((prev) => ({
      ...prev,
      educations: prev.educations.filter((e) => e.id !== id),
    }));
  };

  return (
    <div className="rb-page">
      <div className="rb-header">
        <h1>Resume Builder</h1>
        <p>Create your professional resume in minutes</p>
      </div>

      <StepIndicator currentStep={5} />

      <div className="rb-card">
        <h2 className="rb-card-title">Education Details</h2>
        <p className="rb-card-subtitle">Add your educational background</p>

        {resumeData.educations.map((edu, idx) => (
          <div className="rb-entry-card" key={edu.id}>
            <div className="rb-entry-card-header">
              <GradIcon />
              Education {idx + 1}
              {resumeData.educations.length > 1 && (
                <button className="rb-remove-btn" onClick={() => removeEdu(edu.id)}>
                  Remove
                </button>
              )}
            </div>

            <div className="rb-row">
              <div className="rb-field">
                <label>Degree <span className="required">*</span></label>
                <input
                  className="rb-input"
                  placeholder="Bachelor of Science in Computer Science"
                  value={edu.degree}
                  onChange={(e) => updateEdu(edu.id, "degree", e.target.value)}
                />
              </div>
              <div className="rb-field">
                <label>Institution Name <span className="required">*</span></label>
                <input
                  className="rb-input"
                  placeholder="University of Technology"
                  value={edu.institution}
                  onChange={(e) => updateEdu(edu.id, "institution", e.target.value)}
                />
              </div>
            </div>

            <div className="rb-row-3">
              <div className="rb-field">
                <label>Start Year <span className="required">*</span></label>
                <input
                  className="rb-input"
                  placeholder="2018"
                  value={edu.startYear}
                  onChange={(e) => updateEdu(edu.id, "startYear", e.target.value)}
                />
              </div>
              <div className="rb-field">
                <label>End Year <span className="required">*</span></label>
                <input
                  className="rb-input"
                  placeholder="2022"
                  value={edu.endYear}
                  onChange={(e) => updateEdu(edu.id, "endYear", e.target.value)}
                />
              </div>
              <div className="rb-field">
                <label>GPA / Percentage (Optional)</label>
                <input
                  className="rb-input"
                  placeholder="3.8 / 85%"
                  value={edu.gpa}
                  onChange={(e) => updateEdu(edu.id, "gpa", e.target.value)}
                />
              </div>
            </div>
          </div>
        ))}

        <button className="rb-add-btn" onClick={addEdu}>
          + Add Another Education
        </button>

        <div className="rb-nav">
          <button className="rb-btn-back" onClick={() => navigate("/resume-builder-agent/projects")}>
            <ArrowLeft /> Back
          </button>
          <button
            className="rb-btn-next"
            onClick={() => navigate("/resume-builder-agent/skills")}
          >
            Next <ArrowRight />
          </button>
        </div>
      </div>
    </div>
  );
};

export default EducationPage;