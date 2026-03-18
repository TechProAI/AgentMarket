import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import StepIndicator from "../../../components/StepIndicator/StepIndicator";
import { useResume } from "../../../context/ResumeContext";
import "../../../components/shared.css";
import "./skills.css";

const SUGGESTED = [
  "JavaScript", "Python", "React", "Node.js", "TypeScript",
  "FastAPI", "Machine Learning", "SQL", "Git", "Docker", "AWS", "Figma",
];

const ArrowLeft = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <line x1="19" y1="12" x2="5" y2="12" /><polyline points="12 19 5 12 12 5" />
  </svg>
);
const SparkleIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 2L9.5 9.5 2 12l7.5 2.5L12 22l2.5-7.5L22 12l-7.5-2.5z" />
  </svg>
);

const SkillsPage: React.FC = () => {
  const navigate = useNavigate();
  const { resumeData, setResumeData, setIsGenerating } = useResume();
  const [inputVal, setInputVal] = useState("");

  const addSkill = (skill: string) => {
    const trimmed = skill.trim();
    if (!trimmed || resumeData.skills.includes(trimmed)) return;
    setResumeData((prev) => ({ ...prev, skills: [...prev.skills, trimmed] }));
  };

  const removeSkill = (skill: string) => {
    setResumeData((prev) => ({
      ...prev,
      skills: prev.skills.filter((s) => s !== skill),
    }));
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      e.preventDefault();
      addSkill(inputVal);
      setInputVal("");
    }
  };

  const handleGenerate = () => {
    setIsGenerating(true);
    navigate("/resume-builder-agent/preview");
  };

  return (
    <div className="rb-page">
      <div className="rb-header">
        <h1>Resume Builder</h1>
        <p>Create your professional resume in minutes</p>
      </div>

      <StepIndicator currentStep={6} />

      <div className="rb-card">
        <h2 className="rb-card-title">Skills</h2>
        <p className="rb-card-subtitle">Add your technical and professional skills</p>

        {/* Input */}
        <p className="skills-hint">Type a skill and press Enter</p>
        <div className="skills-input-wrap">
          <input
            className="rb-input"
            placeholder="e.g., React, Python, Machine Learning..."
            value={inputVal}
            onChange={(e) => setInputVal(e.target.value)}
            onKeyDown={handleKeyDown}
          />
        </div>

        {/* Suggested */}
        <div className="suggested-label">
          <SparkleIcon /> Suggested Skills (Click to add)
        </div>
        <div className="suggested-skills">
          {SUGGESTED.map((s) => (
            <button
              key={s}
              className={`suggested-skill-btn ${resumeData.skills.includes(s) ? "already-added" : ""}`}
              onClick={() => addSkill(s)}
              disabled={resumeData.skills.includes(s)}
            >
              + {s}
            </button>
          ))}
        </div>

        {/* Added skills pool */}
        <div className="skills-pool">
          {resumeData.skills.length === 0 ? (
            <p className="skills-pool-empty">
              No skills added yet. Type a skill above and press Enter, or click on suggested skills.
            </p>
          ) : (
            resumeData.skills.map((skill) => (
              <div className="skill-tag" key={skill}>
                {skill}
                <button className="skill-tag-remove" onClick={() => removeSkill(skill)}>
                  ×
                </button>
              </div>
            ))
          )}
        </div>

        <div className="rb-nav">
          <button className="rb-btn-back" onClick={() => navigate("/resume-builder-agent/education")}>
            <ArrowLeft /> Back
          </button>
          <button
            className="generate-btn"
            onClick={handleGenerate}
            disabled={resumeData.skills.length === 0}
          >
            <SparkleIcon /> Generate Resume
          </button>
        </div>
      </div>
    </div>
  );
};

export default SkillsPage;