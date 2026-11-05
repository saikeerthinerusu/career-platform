import { useEffect, useState } from "react";
import api from "../api";

export default function SkillGap() {
  const [careers, setCareers] = useState([]);
  const [careerId, setCareerId] = useState("");
  const [skills, setSkills] = useState([]);
  const [graph, setGraph] = useState({ nodes: [], edges: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadData() {
      try {
        const [graphResponse, skillsResponse] = await Promise.all([
          api.get("/api/skillbridge/graph"),
          api.get("/skills"),
        ]);

        const nodes = graphResponse.data.nodes || [];
        setGraph({
          nodes,
          edges: graphResponse.data.edges || [],
        });

        setSkills(skillsResponse.data || []);

        const available = nodes.filter(
          (node) => node.type === "career_role"
        );

        setCareers(available);

        if (available.length) {
          setCareerId(available[0].id);
        }
      } catch (err) {
        setError(
          err.response?.data?.detail || "Unable to load skill gap data."
        );
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, []);

  const selectedCareer = careers.find(
    (career) => career.id === careerId
  );

  const requiredSkills = graph.edges
    .filter(
      (edge) =>
        edge.target === careerId &&
        edge.relation === "required_for"
    )
    .map((edge) =>
      graph.nodes.find((node) => node.id === edge.source)
    )
    .filter(Boolean);

  const studentSkillNames = new Set(
    skills.map((skill) => skill.name.trim().toLowerCase())
  );

  const matchedSkills = requiredSkills.filter((skill) =>
    studentSkillNames.has(skill.name.trim().toLowerCase())
  );

  const missingSkills = requiredSkills.filter(
    (skill) =>
      !studentSkillNames.has(skill.name.trim().toLowerCase())
  );

  const percentage = requiredSkills.length
    ? Math.round(
        (matchedSkills.length / requiredSkills.length) * 100
      )
    : 0;

  if (loading) return <div className="page-content">Loading skill gap...</div>;

  return (
    <div className="page-content">
      <h1>Skill Gap Analysis</h1>
      <p>Compare your saved skills with your target career requirements.</p>

      {error && <p role="alert">{error}</p>}

      <div className="roadmap-selector">
        <label htmlFor="career-select">Choose Career</label>
        <select
          id="career-select"
          value={careerId}
          onChange={(e) => setCareerId(e.target.value)}
        >
          {careers.map((career) => (
            <option key={career.id} value={career.id}>
              {career.name}
            </option>
          ))}
        </select>
      </div>

      {selectedCareer && (
        <>
          <div className="roadmap-progress-card">
            <h2>{selectedCareer.name}</h2>
            <h2>{percentage}% Career Skill Match</h2>
            <p>
              {matchedSkills.length} of {requiredSkills.length} skills matched
            </p>
            <div className="roadmap-progress-track">
              <div
                className="roadmap-progress-fill"
                style={{ width: `${percentage}%` }}
              />
            </div>
          </div>

          <div className="skill-gap-grid">
            <section className="roadmap-progress-card">
              <h2>✅ Skills You Have ({matchedSkills.length})</h2>
              {matchedSkills.length ? (
                matchedSkills.map((skill) => (
                  <p key={skill.id}>🟢 {skill.name}</p>
                ))
              ) : (
                <p>No matching saved skills yet.</p>
              )}
            </section>

            <section className="roadmap-progress-card">
              <h2>📚 Skills to Learn ({missingSkills.length})</h2>
              {missingSkills.map((skill) => (
                <p key={skill.id}>🔴 {skill.name}</p>
              ))}
            </section>
          </div>
        </>
      )}
    </div>
  );
}