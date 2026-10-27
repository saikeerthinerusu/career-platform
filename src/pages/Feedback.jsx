import { useEffect, useState } from "react";
import { toast } from "react-toastify";
import api from "../api";

export default function Feedback() {
  const [careers, setCareers] = useState([]);
  const [feedback, setFeedback] = useState({});
  const [loading, setLoading] = useState(true);
  const [savingId, setSavingId] = useState(null);

  useEffect(() => {
    loadFeedbackData();
  }, []);

  async function loadFeedbackData() {
    try {
      const [careerResponse, feedbackResponse] = await Promise.all([
        api.get("/career-recommendations"),
        api.get("/feedback"),
      ]);

      const recommendations = Array.isArray(
        careerResponse.data?.recommendations
      )
        ? careerResponse.data.recommendations
        : [];

      const existingFeedback = Array.isArray(feedbackResponse.data)
        ? feedbackResponse.data
        : [];

      // Career title -> actual database career ID
      // The recommendations API must include career_id.
      const careerList = recommendations.map((career) => ({
        ...career,
        id: career.career_id ?? career.id,
        title: career.career || career.title,
      }));

      const feedbackMap = {};

      existingFeedback.forEach((item) => {
        feedbackMap[item.career_id] = {
          rating: String(item.rating),
          comment: item.comment || "",
        };
      });

      setCareers(careerList);
      setFeedback(feedbackMap);
    } catch (error) {
      console.error(
        "Failed to load feedback data:",
        error.response?.data || error.message
      );

      toast.error(
        error.response?.data?.detail ||
          "Failed to load careers. Please log in again if your session expired."
      );
    } finally {
      setLoading(false);
    }
  }

  function updateFeedback(careerId, field, value) {
    setFeedback((previous) => ({
      ...previous,
      [careerId]: {
        rating: previous[careerId]?.rating || "",
        comment: previous[careerId]?.comment || "",
        [field]: value,
      },
    }));
  }

  async function saveFeedback(careerId) {
    if (!Number.isInteger(careerId) || careerId <= 0) {
      toast.error(
        "Valid career ID is missing. Please update the backend recommendation API."
      );
      return;
    }

    const item = feedback[careerId];

    if (!item?.rating) {
      toast.error("Please select a rating from 1 to 5.");
      return;
    }

    setSavingId(careerId);

    try {
      const response = await api.post("/feedback", {
        career_id: careerId,
        rating: Number(item.rating),
        comment: item.comment || "",
      });

      toast.success(
        `Feedback saved successfully! Reward: ${response.data.reward}`
      );

      // Refresh saved feedback and career data.
      await loadFeedbackData();
    } catch (error) {
      console.error(
        "Feedback submission failed:",
        error.response?.data || error.message
      );

      toast.error(
        error.response?.data?.detail ||
          "Failed to save feedback. Please try again."
      );
    } finally {
      setSavingId(null);
    }
  }

  if (loading) {
    return (
      <div className="page-content">
        <h1>Career Preferences & Feedback</h1>
        <p>Loading career feedback...</p>
      </div>
    );
  }

  return (
    <div className="page-content">
      <h1>Career Preferences & Feedback</h1>

      <p>
        Rate your recommended careers and share your thoughts.
        Your feedback is saved in the backend and used by the reward system.
      </p>

      {careers.length === 0 ? (
        <div className="projects-empty">
          <h3>No career recommendations available</h3>
          <p>
            Check your skills and make sure the backend has careers
            configured. Then refresh this page.
          </p>
          <button type="button" onClick={loadFeedbackData}>
            Retry
          </button>
        </div>
      ) : (
        <div className="feedback-career-list">
          {careers.map((career) => {
            const careerId = career.id;
            const item = feedback[careerId] || {};

            return (
              <article
                className="feedback-career-card"
                key={careerId ?? career.title}
              >
                <h3>{career.title}</h3>

                <p>{career.description || "No description available."}</p>

                <p>
                  Match score: {career.match_score ?? 0}%
                </p>

                {Array.isArray(career.strong_skills) &&
                  career.strong_skills.length > 0 && (
                    <div>
                      <h4>Strong Skills</h4>
                      <div className="project-tags">
                        {career.strong_skills.map((skill) => (
                          <span key={skill}>{skill}</span>
                        ))}
                      </div>
                    </div>
                  )}

                {Array.isArray(career.missing_skills) &&
                  career.missing_skills.length > 0 && (
                    <div>
                      <h4>Skills to Learn</h4>
                      <div className="project-tags">
                        {career.missing_skills.map((skill) => (
                          <span key={skill}>{skill}</span>
                        ))}
                      </div>
                    </div>
                  )}

                <div className="project-field">
                  <label htmlFor={`rating-${careerId}`}>
                    Rating (1–5)
                  </label>

                  <select
                    id={`rating-${careerId}`}
                    value={item.rating || ""}
                    onChange={(event) =>
                      updateFeedback(
                        careerId,
                        "rating",
                        event.target.value
                      )
                    }
                    required
                  >
                    <option value="">Select rating</option>
                    <option value="1">1 - Not interested</option>
                    <option value="2">2 - Low interest</option>
                    <option value="3">3 - Maybe</option>
                    <option value="4">4 - Interested</option>
                    <option value="5">5 - Very interested</option>
                  </select>
                </div>

                <div className="project-field">
                  <label htmlFor={`comment-${careerId}`}>
                    Comments (optional)
                  </label>

                  <textarea
                    id={`comment-${careerId}`}
                    rows={3}
                    maxLength={1000}
                    value={item.comment || ""}
                    onChange={(event) =>
                      updateFeedback(
                        careerId,
                        "comment",
                        event.target.value
                      )
                    }
                    placeholder="Share your thoughts about this career..."
                  />
                </div>

                <button
                  type="button"
                  disabled={savingId === careerId}
                  onClick={() => saveFeedback(careerId)}
                >
                  {savingId === careerId
                    ? "Saving..."
                    : "Submit Feedback"}
                </button>
              </article>
            );
          })}
        </div>
      )}
    </div>
  );
}