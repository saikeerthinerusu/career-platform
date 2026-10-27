import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import api from "../api";

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;

    async function fetchDashboard() {
      try {
        setLoading(true);
        setError("");

        const response = await api.get("/dashboard");

        if (!cancelled) {
          setData(response.data);
        }
      } catch (err) {
        if (!cancelled) {
          const status = err.response?.status;

          if (status === 401 || status === 403) {
            setError("Your session may have expired. Please log in again.");
          } else {
            setError(
              err.response?.data?.detail ||
                "Unable to load dashboard. Please check that the backend is running."
            );
          }
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    fetchDashboard();

    return () => {
      cancelled = true;
    };
  }, []);

  if (loading) {
    return (
      <div className="page-content">
        <h1>Dashboard</h1>
        <p>Loading your career dashboard...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="page-content">
        <h1>Dashboard</h1>
        <p role="alert">{error}</p>

        <button onClick={() => window.location.reload()}>
          Try Again
        </button>

        <p>
          <Link to="/login">Go to Login</Link>
        </p>
      </div>
    );
  }

  const statistics = data?.statistics || {};
  const student = data?.student || {};
  const profile = student.profile || {};
  const skillGap = data?.skill_gap || {
    strong_skills: [],
    partial_skills: [],
    missing_skills: [],
  };

  const recommendations = data?.all_recommendations || [];
  const topCareer = data?.top_recommendation;

  const chartData = [
    {
      name: "Strong Skills",
      value: skillGap.strong_skills?.length || 0,
    },
    {
      name: "Partial Skills",
      value: skillGap.partial_skills?.length || 0,
    },
    {
      name: "Missing Skills",
      value: skillGap.missing_skills?.length || 0,
    },
  ];

  const chartColors = ["#16a34a", "#f59e0b", "#ef4444"];

  return (
    <div className="page-content">
      <h1>Dashboard</h1>

      <p>
        Welcome{profile.name ? `, ${profile.name}` : student.username ? `, ${student.username}` : ""}!
        Track your career development progress in one place.
      </p>

      <div className="dashboard-stats">
        <div className="dashboard-stat-card">
          <span>My Skills</span>
          <h2>{statistics.total_skills ?? 0}</h2>
          <Link to="/skills">Manage skills →</Link>
        </div>

        <div className="dashboard-stat-card">
          <span>Career Recommendations</span>
          <h2>{recommendations.length}</h2>
          <Link to="/careers">Explore careers →</Link>
        </div>

        <div className="dashboard-stat-card">
          <span>Roadmap Progress</span>
          <h2>
            {statistics.roadmap_progress_percentage ?? 0}%
          </h2>
          <Link to="/roadmap">Continue learning →</Link>
        </div>

        <div className="dashboard-stat-card">
          <span>Feedback Submitted</span>
          <h2>{statistics.total_feedback ?? 0}</h2>
          <Link to="/feedback">Share feedback →</Link>
        </div>
      </div>

      <div className="dashboard-panels">
        <section className="dashboard-panel">
          <h2>Skill Gap Analysis</h2>
          <p>
            Your skills compared with the requirements of your top
            recommended career.
          </p>

          {chartData.every((item) => item.value === 0) ? (
            <p>
              Add your skills and explore career recommendations to see
              your skill gap.
            </p>
          ) : (
            <div className="dashboard-chart">
              <ResponsiveContainer width="100%" height={240}>
                <PieChart>
                  <Pie
                    data={chartData}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    label
                  >
                    {chartData.map((entry, index) => (
                      <Cell
                        key={entry.name}
                        fill={chartColors[index]}
                      />
                    ))}
                  </Pie>

                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          )}

          <div>
            <p>
              <strong>Strong skills:</strong>{" "}
              {skillGap.strong_skills?.join(", ") || "None yet"}
            </p>

            <p>
              <strong>Partial skills:</strong>{" "}
              {skillGap.partial_skills?.join(", ") || "None yet"}
            </p>

            <p>
              <strong>Missing skills:</strong>{" "}
              {skillGap.missing_skills?.join(", ") || "None"}
            </p>
          </div>

          <Link to="/skill-gap">View complete skill gap →</Link>
        </section>

        <section className="dashboard-panel">
          <h2>Top Career Recommendation</h2>

          {topCareer ? (
            <>
              <h3>{topCareer.career || topCareer.title}</h3>

              <p>
                {topCareer.description ||
                  "Explore this career and build the required skills."}
              </p>

              <p>
                <strong>Match score:</strong>{" "}
                {topCareer.match_score ?? 0}%
              </p>

              <Link to="/careers">View all recommendations →</Link>
            </>
          ) : (
            <p>
              No career recommendations are available yet. Add your
              skills to get started.
            </p>
          )}
        </section>

        <section className="dashboard-panel">
          <h2>Quick Actions</h2>
          <p>Choose what you want to work on next.</p>

          <div className="dashboard-quick-links">
            <Link to="/profile">Update My Profile</Link>
            <Link to="/skills">+ Manage Skills</Link>
            <Link to="/skill-gap">Analyze Skill Gap</Link>
            <Link to="/careers">Explore Careers</Link>
            <Link to="/roadmap">View Learning Roadmap</Link>
            <Link to="/feedback">Submit Feedback</Link>
          </div>
        </section>
      </div>
    </div>
  );
}