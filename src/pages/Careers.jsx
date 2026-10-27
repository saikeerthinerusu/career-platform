
import { useEffect, useState } from "react";
import api from "../api";

const careerIcons = {
  "AI Engineer": "🤖",
  "Frontend Developer": "🎨",
  "Backend Developer": "⚙️",
  "Data Analyst": "📊",
  "Full Stack Developer": "💻",
};

function getSkillName(skill) {
  if (typeof skill === "string") return skill;
  return skill?.name || skill?.skill_name || String(skill ?? "");
}

export default function Careers() {
  const [recommendations, setRecommendations] = useState([]);
  const [agentAdvice, setAgentAdvice] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchCareers = async () => {
    setLoading(true);
    setError("");

    try {
      const response = await api.get("/career-recommendations");
      setRecommendations(response.data.recommendations || []);
      setAgentAdvice(response.data.agent_advice || null);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Unable to load career recommendations. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCareers();
  }, []);

  if (loading) {
    return (
      <div className="page-content">
        <h1>Career Recommendations</h1>
        <p>Loading your career recommendations...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="page-content">
        <h1>Career Recommendations</h1>
        <p>{error}</p>
        <button onClick={fetchCareers}>Try Again</button>
      </div>
    );
  }

  return (
    <div className="page-content">
      <h1>Career Recommendations</h1>
      <p>
        Explore careers based on your current skills and discover what to learn
        next.
      </p>

      {recommendations.length === 0 ? (
        <div className="career-empty">
          <h3>No career recommendations available</h3>
          <p>
            Add your skills and ensure career data is available in the backend
            database.
          </p>
          <a href="/skills">Go to My Skills →</a>
        </div>
      ) : (
        <div className="career-results">
          {recommendations.map((career, index) => {
            const strongSkills = (career.strong_skills || []).map(getSkillName);
            const partialSkills = (career.partial_skills || []).map(getSkillName);
            const missingSkills = (career.missing_skills || []).map(getSkillName);

            const match = Math.max(
              0,
              Math.min(100, Number(career.match_score ?? 0))
            );

            const careerTitle = career.career || career.title || "Career";

            return (
              <article
                className="career-card"
                key={career.career_id || career.id || careerTitle || index}
              >
                <div className="career-card-top">
                  <div className="career-icon">
                    {careerIcons[careerTitle] || "💼"}
                  </div>
                  <div className="career-match">{match}% match</div>
                </div>

                <h2>{careerTitle}</h2>
                <p className="career-description">
                  {career.description || "Explore this career path."}
                </p>

                <div className="career-progress">
                  <div
                    className="career-progress-fill"
                    style={{ width: `${match}%` }}
                  />
                </div>

                <p className="career-skill-count">
                  {strongSkills.length} strong · {partialSkills.length} to
                  improve · {missingSkills.length} missing
                </p>

                <h3>Matching skills</h3>
                <div className="career-tags">
                  {strongSkills.length > 0 ? (
                    strongSkills.map((skill) => (
                      <span className="career-tag matched" key={skill}>
                        ✓ {skill}
                      </span>
                    ))
                  ) : (
                    <span className="career-muted">No strong matches yet</span>
                  )}
                </div>

                {partialSkills.length > 0 && (
                  <>
                    <h3>Skills to improve</h3>
                    <div className="career-tags">
                      {partialSkills.map((skill) => (
                        <span className="career-tag" key={skill}>
                          ↗ {skill}
                        </span>
                      ))}
                    </div>
                  </>
                )}

                <h3>Skills to learn</h3>
                <div className="career-tags">
                  {missingSkills.length > 0 ? (
                    missingSkills.map((skill) => (
                      <span className="career-tag missing" key={skill}>
                        {skill}
                      </span>
                    ))
                  ) : (
                    <span className="career-muted">
                      No missing skills reported
                    </span>
                  )}
                </div>

                <a className="career-action" href="/skill-gap">
                  Explore skill gaps →
                </a>
              </article>
            );
          })}
        </div>
      )}

      {agentAdvice && (
        <section className="career-advice">
          <h2>Career Agent Advice</h2>
          <p>
            {typeof agentAdvice === "string"
              ? agentAdvice
              : agentAdvice.message || agentAdvice.advice || ""}
          </p>

          {Array.isArray(agentAdvice.suggestions) &&
            agentAdvice.suggestions.length > 0 && (
              <ul>
                {agentAdvice.suggestions.map((suggestion, index) => (
                  <li key={index}>{suggestion}</li>
                ))}
              </ul>
            )}
        </section>
      )}

      <p className="career-disclaimer">
        Recommendations are based on your backend skill data and are intended
        as learning guidance, not a guarantee of employment.
      </p>
    </div>
  );
}
