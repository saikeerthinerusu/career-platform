import { useEffect, useState } from "react";
import api from "../api";

function SkillGap() {
  const [careers, setCareers] = useState([]);
  const [selectedCareer, setSelectedCareer] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchCareers = async () => {
      try {
        const response = await api.get("/career-recommendations");
        const data = response.data.recommendations || [];

        setCareers(data);

        if (data.length > 0) {
          setSelectedCareer(data[0].career);
        }
      } catch (err) {
        setError(
          err.response?.data?.detail ||
            "Could not load skill gap. Please login again and retry."
        );
      } finally {
        setLoading(false);
      }
    };

    fetchCareers();
  }, []);

  const careerData = careers.find(
    (item) => item.career === selectedCareer
  );

  if (loading) return <p>Loading skill gap...</p>;
  if (error) return <p>{error}</p>;

  
  return (
    <div className="page-content skill-gap-page">
      <div className="skill-gap-header">
        <h1>Skill Gap Analysis</h1>
        <p>
          Understand which skills you have and which skills to learn.
        </p>
      </div>

      <div className="gap-selector">
        <label htmlFor="career-select">Select Target Career</label>
        <select
          id="career-select"
          value={selectedCareer}
          onChange={(e) => setSelectedCareer(e.target.value)}
        >
          {careers.map((item) => (
            <option key={item.career} value={item.career}>
              {item.career}
            </option>
          ))}
        </select>
      </div>

      {careerData && (
        <>
          <div className="gap-career-card">
            <h2>{careerData.career}</h2>
            <p>{careerData.description}</p>

            <div className="gap-score">
              <span>Career Match Score</span>
              <strong>{careerData.match_score ?? 0}%</strong>
            </div>

            <div className="gap-progress">
              <div
                className="gap-progress-fill"
                style={{
                  width: `${careerData.match_score ?? 0}%`,
                }}
              />
            </div>
          </div>

          <div className="gap-sections">
            <section className="gap-section strong">
              <h3>✅ Strong Skills</h3>
              {careerData.strong_skills?.length ? (
                <div className="gap-tags">
                  {careerData.strong_skills.map((skill) => (
                    <span key={skill}>{skill}</span>
                  ))}
                </div>
              ) : (
                <p>No strong skills identified yet.</p>
              )}
            </section>

            <section className="gap-section partial">
              <h3>🟡 Partial Skills</h3>
              {careerData.partial_skills?.length ? (
                <div className="gap-tags">
                  {careerData.partial_skills.map((skill) => (
                    <span key={skill}>{skill}</span>
                  ))}
                </div>
              ) : (
                <p>No partial skills identified yet.</p>
              )}
            </section>

            <section className="gap-section missing">
              <h3>📚 Missing Skills</h3>
              {careerData.missing_skills?.length ? (
                <div className="gap-tags">
                  {careerData.missing_skills.map((skill) => (
                    <span key={skill}>{skill}</span>
                  ))}
                </div>
              ) : (
                <p>No missing skills identified.</p>
              )}
            </section>
          </div>
        </>
      )}
    </div>
  );

}

export default SkillGap;
