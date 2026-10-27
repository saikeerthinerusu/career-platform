
import { useState } from "react";

const careerRequirements = {
  "AI Engineer": ["Python", "Machine Learning", "Statistics", "Deep Learning"],
  "Frontend Developer": ["HTML", "CSS", "JavaScript", "React"],
  "Backend Developer": ["Java", "SQL", "REST APIs", "Data Structures"],
  "Data Analyst": ["Python", "SQL", "Statistics", "Excel"],
  "Full Stack Developer": ["HTML", "CSS", "JavaScript", "React", "Node.js", "SQL"],
};

export default function WhatIf() {
  const [career, setCareer] = useState("AI Engineer");

  const skills = (() => {
    try {
      return JSON.parse(localStorage.getItem("careerSkills") || "[]");
    } catch {
      return [];
    }
  })();

  const userSkills = skills.map((skill) => skill.name.toLowerCase());
  const requiredSkills = careerRequirements[career];

  const matched = requiredSkills.filter((skill) =>
    userSkills.includes(skill.toLowerCase())
  );

  const missing = requiredSkills.filter(
    (skill) => !userSkills.includes(skill.toLowerCase())
  );

  const readiness = Math.round(
    (matched.length / requiredSkills.length) * 100
  );

  return (
    <div className="page-content">
      <h1>What-if Career Analysis</h1>
      <p>Compare your current skills with a different career goal.</p>

      <section className="whatif-card">
        <label htmlFor="whatif-career">What if you choose this career?</label>

        <select
          id="whatif-career"
          value={career}
          onChange={(event) => setCareer(event.target.value)}
        >
          {Object.keys(careerRequirements).map((name) => (
            <option key={name} value={name}>{name}</option>
          ))}
        </select>

        <div className="whatif-score">
          <span>Skill Match</span>
          <h2>{readiness}%</h2>
          <div className="readiness-track">
            <div
              className="readiness-fill"
              style={{ width: `${readiness}%` }}
            />
          </div>
          <p>{matched.length} of {requiredSkills.length} required skills matched</p>
        </div>

        <h3>Skills You Already Have</h3>
        {matched.length ? (
          <div className="project-tags">
            {matched.map((skill) => <span key={skill}>{skill}</span>)}
          </div>
        ) : <p>No matching skills yet. Add your skills in My Skills.</p>}

        <h3>Skills to Learn</h3>
        {missing.length ? (
          <div className="project-tags">
            {missing.map((skill) => (
              <span className="whatif-missing" key={skill}>{skill}</span>
            ))}
          </div>
        ) : <p>Great! All listed skills match your current skill names.</p>}
      </section>

      <p className="whatif-note">
        This is a sample rule-based comparison, not a prediction of job
        placement or hiring success.
      </p>
    </div>
  );
}
