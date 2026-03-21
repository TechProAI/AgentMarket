import React, { useEffect } from "react";
import { Route, Routes, Navigate } from "react-router-dom";

import TravelAgentPage from "./AgentPages/TravelAgent/TravelAgentPage";
import Login from "./auth/LoginPage/Login";
import Signup from "./auth/SignupPage/Signup";
import { useAuth } from "./context/AuthContext";
import WebSearchAgentPage from "./AgentPages/WebSearchAgent/WebSearchAgentPage";
import Header from "./components/Header/Header";
import HomePage from "./components/Home/HomePage";

// Resume Builder pages
import PhotoPage from "./AgentPages/ResumeBuilderAgent/photo/PhotoPage";
import PersonalPage from "./AgentPages/ResumeBuilderAgent/personal/PersonalPage";
import ExperiencePage from "./AgentPages/ResumeBuilderAgent/experience/ExperiencePage";
import ProjectsPage from "./AgentPages/ResumeBuilderAgent/projects/ProjectsPage";
import EducationPage from "./AgentPages/ResumeBuilderAgent/education/EducationPage";
import SkillsPage from "./AgentPages/ResumeBuilderAgent/skills/SkillsPage";
import PreviewPage from "./AgentPages/ResumeBuilderAgent/preview/PreviewPage";


import { ResumeProvider } from "./context/ResumeContext";

// ─── Protected Route wrapper ──────────────────────────────────────────────────
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { authLoading, token } = useAuth();

  if (authLoading) {
    return <div>Loading...</div>;
  }

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

// ─── App ──────────────────────────────────────────────────────────────────────
function App() {

  useEffect(() => {
    localStorage.removeItem("token")
  },[])

  return (
    <>
      <Header />
      <Routes>

        {/* ── Public Routes ───────────────────────────────────────────────── */}
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/" element={<HomePage />} />

        {/* ── Protected: Travel & Web Search ──────────────────────────────── */}
        <Route
          path="/travel-agent"
          element={<ProtectedRoute><TravelAgentPage /></ProtectedRoute>}
        />
        <Route
          path="/web-search-agent"
          element={<ProtectedRoute><WebSearchAgentPage /></ProtectedRoute>}
        />

        {/* ── Protected: Resume Builder steps (all wrapped in ResumeProvider) */}
        {/* ResumeProvider is placed at the layout level via a wrapper element  */}
        <Route
          path="/resume-builder-agent"
          element={
            <ProtectedRoute>
              <ResumeProvider>
                <Navigate to="/resume-builder-agent/photo" replace />
              </ResumeProvider>
            </ProtectedRoute>
          }
        />
        <Route
          path="/resume-builder-agent/photo"
          element={
            <ProtectedRoute>
              <ResumeProvider>
                <PhotoPage />
              </ResumeProvider>
            </ProtectedRoute>
          }
        />
        <Route
          path="/resume-builder-agent/personal"
          element={
            <ProtectedRoute>
              <ResumeProvider>
                <PersonalPage />
              </ResumeProvider>
            </ProtectedRoute>
          }
        />
        <Route
          path="/resume-builder-agent/experience"
          element={
            <ProtectedRoute>
              <ResumeProvider>
                <ExperiencePage />
              </ResumeProvider>
            </ProtectedRoute>
          }
        />
        <Route
          path="/resume-builder-agent/projects"
          element={
            <ProtectedRoute>
              <ResumeProvider>
                <ProjectsPage />
              </ResumeProvider>
            </ProtectedRoute>
          }
        />
        <Route
          path="/resume-builder-agent/education"
          element={
            <ProtectedRoute>
              <ResumeProvider>
                <EducationPage />
              </ResumeProvider>
            </ProtectedRoute>
          }
        />
        <Route
          path="/resume-builder-agent/skills"
          element={
            <ProtectedRoute>
              <ResumeProvider>
                <SkillsPage />
              </ResumeProvider>
            </ProtectedRoute>
          }
        />
        <Route
          path="/resume-builder-agent/preview"
          element={
            <ProtectedRoute>
              <ResumeProvider>
                <PreviewPage />
              </ResumeProvider>
            </ProtectedRoute>
          }
        />

      </Routes>
    </>
  );
}

export default App;