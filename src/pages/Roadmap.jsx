import { useEffect, useState } from "react";
import { toast } from "react-toastify";
import api from "../api";

export default function Roadmap() {
  const [careers, setCareers] = useState([]);
  const [careerId, setCareerId] = useState("");
  const [roadmap, setRoadmap] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadCareers() {
      try {
        const response = await api.get("/career-recommendations");
        const recommendations = response.data.recommendations || [];

        const careerIds = {
          "Frontend Developer": 1,
          "Backend Developer": 2,
          "AI Engineer": 3,
        };

        const available = recommendations
          .filter((item) => careerIds[item.career])
          .map((item) => ({
            id: careerIds[item.career],
            name: item.career,
          }));

        setCareers(available);

        if (available.length > 0) {
          setCareerId(String(available[0].id));
        } else {
          setError("No supported careers found.");
          setLoading(false);
        }
      } catch (err) {
        setError(
          err.response?.data?.detail || "Unable to load careers."
        );
        setLoading(false);
      }
    }

    loadCareers();
  }, []);

  useEffect(() => {
    if (!careerId) return;

    let cancelled = false;

    async function loadRoadmap() {
      setLoading(true);
      setError("");

      try {
        const response = await api.get(`/roadmap/${careerId}`);

        if (!cancelled) {
          setRoadmap(response.data.roadmap || []);
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err.response?.data?.detail || "Unable to load roadmap."
          );
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    loadRoadmap();

    return () => {
      cancelled = true;
    };
  }, [careerId]);

  async function toggleStep(step, checked) {
    setSaving(step.step_id);

    try {
      await api.put(`/roadmap/progress/${step.step_id}`, {
        completed: checked,
      });

      setRoadmap((previous) =>
        previous.map((item) =>
          item.step_id === step.step_id
            ? { ...item, completed: checked }
            : item
        )
      );

      toast.success(
        checked ? "Step completed!" : "Step marked incomplete."
      );
    } catch (err) {
      toast.error(
        err.response?.data?.detail || "Unable to save progress."
      );
    } finally {
      setSaving(null);
    }
  }

  const completedCount = roadmap.filter(
    (step) => step.completed
  ).length;

  const percentage = roadmap.length
    ? Math.round((completedCount / roadmap.length) * 100)
    : 0;

  const selectedCareer = careers.find(
    (career) => String(career.id) === careerId
  );

  if (loading && roadmap.length === 0) {
    return <div className="page-content"><p>Loading roadmap...</p></div>;
  }

  return (
    <div className="page-content">
      <h1>Learning Roadmap</h1>
      <p>Follow your learning journey one step at a time.</p>

      {error && <p role="alert">{error}</p>}

      <div className="roadmap-selector">
        <label htmlFor="roadmap-career">Choose your target career</label>
        <select
          id="roadmap-career"
          value={careerId}
          onChange={(event) => setCareerId(event.target.value)}
          disabled={careers.length === 0}
        >
          {careers.map((career) => (
            <option key={career.id} value={career.id}>
              {career.name}
            </option>
          ))}
        </select>
      </div>

      <div className="roadmap-progress-card">
        <div className="roadmap-progress-heading">
          <div>
            <h2>{selectedCareer?.name || "Learning Roadmap"}</h2>
            <p>{completedCount} of {roadmap.length} steps completed</p>
          </div>
          <strong>{percentage}%</strong>
        </div>

        <div className="roadmap-progress-track">
          <div
            className="roadmap-progress-fill"
            style={{ width: `${percentage}%` }}
          />
        </div>
      </div>

      {loading ? (
        <p>Loading selected roadmap...</p>
      ) : (
        <div className="roadmap-steps">
          {roadmap.map((step, index) => {
            const previousStep = roadmap.find(
              (item) => item.step_id === step.prerequisite_step_id
            );

            const unlocked =
              !previousStep || previousStep.completed;

            return (
              <section className="roadmap-step" key={step.step_id}>
                <div
                  className={`roadmap-step-number ${
                    step.completed ? "step-done" : ""
                  }`}
                >
                  {step.completed ? "✓" : index + 1}
                </div>

                <div
                  className={`roadmap-step-content ${
                    !unlocked ? "step-locked" : ""
                  }`}
                >
                  <div className="roadmap-step-heading">
                    <div>
                      <h2>{step.title}</h2>
                      <p>{step.description}</p>
                    </div>

                    {step.completed && (
                      <span className="roadmap-complete">Completed</span>
                    )}
                  </div>

                  {!unlocked && (
                    <p>Complete the prerequisite step to unlock this step.</p>
                  )}

                  <label className="roadmap-task">
                    <input
                      type="checkbox"
                      checked={step.completed}
                      disabled={!unlocked || saving === step.step_id}
                      onChange={(event) =>
                        toggleStep(step, event.target.checked)
                      }
                    />
                    <span>
                      {saving === step.step_id
                        ? "Saving..."
                        : step.completed
                          ? "Completed"
                          : "Mark as completed"}
                    </span>
                  </label>
                </div>
              </section>
            );
          })}
        </div>
      )}

      {percentage === 100 && roadmap.length > 0 && (
        <p className="roadmap-finished">
          Congratulations! You completed this roadmap! 🎉
        </p>
      )}
    </div>
  );
}
