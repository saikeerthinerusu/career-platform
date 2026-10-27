
const careerSkills = {
  "AI Engineer": ["Python", "Machine Learning", "Statistics", "Deep Learning"],
  "Frontend Developer": ["HTML", "CSS", "JavaScript", "React"],
  "Backend Developer": ["Java", "SQL", "REST APIs", "Data Structures"],
  "Data Analyst": ["Python", "SQL", "Statistics", "Excel"],
};

export default function CareerGraph() {
  const skills = (() => {
    try {
      return JSON.parse(localStorage.getItem("careerSkills") || "[]");
    } catch {
      return [];
    }
  })();

  const userSkills = skills.map((skill) => skill.name.toLowerCase());

  return (
    <div className="page-content">
      <h1>Career Graph</h1>
      <p>Explore the connection between career paths and required skills.</p>

      <div className="career-graph-grid">
        {Object.entries(careerSkills).map(([career, required]) => {
          const matched = required.filter((skill) =>
            userSkills.includes(skill.toLowerCase())
          );

          return (
            <section className="graph-career-card" key={career}>
              <div className="graph-career-node">{career}</div>

              <div className="graph-connector">↓ Required skills</div>

              <div className="graph-skill-list">
                {required.map((skill) => {
                  const hasSkill = userSkills.includes(skill.toLowerCase());

                  return (
                    <div
                      key={skill}
                      className={
                        hasSkill
                          ? "graph-skill-node graph-skill-owned"
                          : "graph-skill-node"
                      }
                    >
                      <span>{hasSkill ? "✓" : "○"}</span>
                      {skill}
                    </div>
                  );
                })}
              </div>

              <p className="graph-match">
                {matched.length}/{required.length} skills matched
              </p>
            </section>
          );
        })}
      </div>

      <p className="whatif-note">
        Green-style highlighted skills indicate name matches with your saved
        skills. This graph uses sample career-skill relationships.
      </p>
    </div>
  );
}
