import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import "./App.css";
import Auth from "./pages/Auth";
import ProtectedRoute from "./components/ProtectedRoute";
import Profile from "./pages/Profile";
import Skills from "./pages/Skills";
import SkillGap from "./pages/SkillGap";
import Careers from "./pages/Careers";
import Roadmap from "./pages/Roadmap";
import Projects from "./pages/Projects";
import Opportunities from "./pages/Opportunities";
import Notifications from "./pages/Notifications";
import Feedback from "./pages/Feedback";
import WhatIf from "./pages/WhatIf";
import CareerGraph from "./pages/CareerGraph";
import Admin from "./pages/Admin";

function Placeholder({ title }) {
  return (
    <div className="placeholder-page">
      <h1>{title}</h1>
      <p>This module will be implemented in the next steps.</p>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      
<Routes>
  <Route path="/login" element={<Auth mode="login" />} />
  <Route path="/register" element={<Auth mode="register" />} />

  <Route element={<ProtectedRoute />}>
    <Route element={<Layout />}>
      <Route path="/" element={<Dashboard />} />
      <Route path="profile" element={<Profile />} />
      <Route path="skills" element={<Skills />} />
      <Route path="skill-gap" element={<SkillGap />} />
      <Route path="careers" element={<Careers />} />
      <Route path="roadmap" element={<Roadmap />} />
      <Route path="projects" element={<Projects />} />
      <Route path="opportunities" element={<Opportunities />} />
      <Route path="notifications" element={<Notifications />} />
      <Route path="what-if" element={<WhatIf />} />
      <Route path="graph" element={<CareerGraph />} />
      <Route path="admin" element={<Admin />} />
      <Route path="feedback" element={<Feedback />} />
    </Route>
  </Route>
</Routes>

    </BrowserRouter>
  );
}
