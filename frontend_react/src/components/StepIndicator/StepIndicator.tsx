import React from "react";
import "./StepIndicator.css";

const STEPS = [
  { label: "Photo" },
  { label: "Personal" },
  { label: "Experience" },
  { label: "Projects" },
  { label: "Education" },
  { label: "Skills" },
  { label: "Preview" },
];

interface StepIndicatorProps {
  currentStep: number; // 1-indexed
}

const CheckIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="20 6 9 17 4 12" />
  </svg>
);

const StepIndicator: React.FC<StepIndicatorProps> = ({ currentStep }) => {
  return (
    <div className="step-indicator">
      {STEPS.map((step, idx) => {
        const stepNum = idx + 1;
        const isCompleted = stepNum < currentStep;
        const isActive = stepNum === currentStep;

        return (
          <div className="step-item" key={step.label}>
            {/* Connector line (not for last item) */}
            {idx < STEPS.length - 1 && (
              <div className={`step-connector ${isCompleted ? "completed" : ""}`} />
            )}

            <div
              className={`step-circle ${isActive ? "active" : ""} ${isCompleted ? "completed" : ""}`}
            >
              {isCompleted ? <CheckIcon /> : stepNum}
            </div>

            <span
              className={`step-label ${isActive ? "active" : ""} ${isCompleted ? "completed" : ""}`}
            >
              {step.label}
            </span>
          </div>
        );
      })}
    </div>
  );
};

export default StepIndicator;