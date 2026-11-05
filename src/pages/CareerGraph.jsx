import { useEffect, useState } from "react";
import api from "../api";

export default function CareerGraph() {
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  const [selectedCareer, setSelectedCareer] = useState("");
  const [selectedSkill, setSelectedSkill] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadGraph() {
      try {
        const response = await api.get("/api/skillbridge/graph");

        const graphNodes = response.data.nodes || [];
        const graphEdges = response.data.edges || [];

        setNodes(graphNodes);
        setEdges(graphEdges);

        const firstCareer = graphNodes.find(
          (node) => node.type === "career_role"
        );

        if (firstCareer) {
          setSelectedCareer(firstCareer.id);
        }
      } catch (err) {
        setError(
          err.response?.data?.detail || "Unable to load career network."
        );
      } finally {
        setLoading(false);
      }
    }

    loadGraph();
  }, []);

  const careers = nodes.filter(
    (node) => node.type === "career_role"
  );

  const skills = nodes.filter(
    (node) => node.type === "skill"
  );

  // Skills connected to the selected career
  const selectedCareerSkills = edges
    .filter(
      (edge) =>
        edge.target === selectedCareer &&
        edge.relation === "required_for"
    )
    .map((edge) => edge.source);

  // Other careers sharing the selected career's skills
  const relatedCareers = careers
    .filter((career) => career.id !== selectedCareer)
    .map((career) => {
      const careerSkills = edges
        .filter(
          (edge) =>
            edge.target === career.id &&
            edge.relation === "required_for"
        )
        .map((edge) => edge.source);

      const sharedSkills = selectedCareerSkills.filter(
        (skillId) => careerSkills.includes(skillId)
      );

      return {
        ...career,
        sharedSkills,
        sharedCount: sharedSkills.length,
      };
    })
    .filter((career) => career.sharedCount > 0)
    .sort((a, b) => b.sharedCount - a.sharedCount);

  const selectedCareerData = careers.find(
    (career) => career.id === selectedCareer
  );

  const selectedSkillData = skills.find(
    (skill) => skill.id === selectedSkill
  );

  // Careers connected to the selected skill
  const skillCareers = selectedSkill
    ? edges
        .filter(
          (edge) =>
            edge.source === selectedSkill &&
            edge.relation === "required_for"
        )
        .map((edge) =>
          careers.find((career) => career.id === edge.target)
        )
        .filter(Boolean)
    : [];

  if (loading) {
    return <div className="page-content">Loading career network...</div>;
  }

  return (
    <div className="page-content">
      <h1>Career Exploration Graph</h1>
      <p>
        Explore different career paths and discover the skills
        connecting them.
      </p>

      {error && <p role="alert">{error}</p>}

      <section className="roadmap-progress-card">
        <label htmlFor="career-network-select">
          Choose a starting career
        </label>

        <select
          id="career-network-select"
          value={selectedCareer}
          onChange={(e) => {
            setSelectedCareer(e.target.value);
            setSelectedSkill(null);
          }}
        >
          {careers.map((career) => (
            <option key={career.id} value={career.id}>
              {career.name}
            </option>
          ))}
        </select>

        {selectedCareerData && (
          <>
            <h2>{selectedCareerData.name}</h2>
            <p>
              {selectedCareerData.description ||
                "Explore the skills and related career opportunities."}
            </p>
            <p>
              <strong>
                {selectedCareerSkills.length} connected skills
              </strong>
            </p>
          </>
        )}
      </section>

      <section className="roadmap-progress-card">
        <h2>Career Network</h2>
        <p>
          These careers share skills with your selected career.
          Select another career to explore its connections.
        </p>

        <div className="skill-gap-grid">
          {relatedCareers.slice(0, 12).map((career) => (
            <button
              key={career.id}
              type="button"
              onClick={() => {
                setSelectedCareer(career.id);
                setSelectedSkill(null);
              }}
              style={{
                padding: "18px",
                margin: "6px",
                border: "1px solid #d9deeb",
                borderRadius: "12px",
                background: "#ffffff",
                color: "#243b70",
                cursor: "pointer",
                textAlign: "left",
              }}
            >
              <strong>{career.name}</strong>
              <p>
                {career.sharedCount} shared skills
              </p>
              <span>Explore career →</span>
            </button>
          ))}
        </div>

        {relatedCareers.length === 0 && (
          <p>No related careers found for this selection.</p>
        )}
      </section>

      <section className="roadmap-progress-card">
        <h2>Skills Connecting Careers</h2>
        <p>Click any skill to discover other careers using it.</p>

        <div className="skill-gap-grid">
          {selectedCareerSkills.map((skillId) => {
            const skill = skills.find(
              (item) => item.id === skillId
            );

            if (!skill) return null;

            return (
              <button
                key={skill.id}
                type="button"
                onClick={() =>
                  setSelectedSkill(
                    selectedSkill === skill.id ? null : skill.id
                  )
                }
                style={{
                  padding: "10px 16px",
                  margin: "5px",
                  borderRadius: "20px",
                  border: "1px solid #b8c7e8",
                  background:
                    selectedSkill === skill.id ? "#dce8ff" : "#ffffff",
                  color: "#243b70",
                  cursor: "pointer",
                }}
              >
                {skill.name}
              </button>
            );
          })}
        </div>
      </section>

      {selectedSkillData && (
        <section className="roadmap-progress-card">
          <h2>{selectedSkillData.name}</h2>
          <p>This skill is connected to these career paths:</p>

          {skillCareers.map((career) => (
            <button
              key={career.id}
              type="button"
              onClick={() => {
                setSelectedCareer(career.id);
                setSelectedSkill(null);
              }}
              style={{
                display: "block",
                padding: "12px",
                margin: "8px 0",
                width: "100%",
                textAlign: "left",
                border: "1px solid #d9deeb",
                borderRadius: "8px",
                background: "white",
                cursor: "pointer",
              }}
            >
              {career.name} →
            </button>
          ))}
        </section>
      )}

      <p>
        Explore {careers.length} career paths and {skills.length} skills
        in the knowledge graph.
      </p>
    </div>
  );
}