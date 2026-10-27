
import { useEffect, useState } from "react";
import { toast } from "react-toastify";

const sampleOpportunities = [
  {
    id: 1,
    title: "Frontend Developer Intern",
    company: "Example Tech",
    type: "Internship",
    skills: ["HTML", "CSS", "JavaScript", "React"],
    description: "Build responsive user interfaces and learn from a development team.",
  },
  {
    id: 2,
    title: "AI/ML Intern",
    company: "Example AI Labs",
    type: "Internship",
    skills: ["Python", "Machine Learning", "Statistics"],
    description: "Explore machine learning models and practical AI applications.",
  },
  {
    id: 3,
    title: "Java Developer",
    company: "Example Software",
    type: "Job",
    skills: ["Java", "SQL", "Data Structures"],
    description: "Work on Java applications, databases and backend services.",
  },
];

export default function Opportunities() {
  const [opportunities] = useState(sampleOpportunities);

  const [bookmarks, setBookmarks] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem("careerBookmarks")) || [];
    } catch {
      return [];
    }
  });

  const [filter, setFilter] = useState("All");
  const [showSaved, setShowSaved] = useState(false);

  useEffect(() => {
    localStorage.setItem("careerBookmarks", JSON.stringify(bookmarks));
  }, [bookmarks]);

  const visibleOpportunities = opportunities.filter((item) => {
    const matchesFilter = filter === "All" || item.type === filter;
    const matchesSaved = !showSaved || bookmarks.includes(item.id);
    return matchesFilter && matchesSaved;
  });

  function toggleBookmark(id) {
    const isSaved = bookmarks.includes(id);

    setBookmarks((previous) =>
      isSaved
        ? previous.filter((itemId) => itemId !== id)
        : [...previous, id]
    );

    toast.success(isSaved ? "Bookmark removed." : "Opportunity bookmarked!");
  }

  function applyForOpportunity(item) {
    const existing = JSON.parse(
      localStorage.getItem("careerNotifications") || "[]"
    );

    const notification = {
      id: Date.now(),
      message: `You selected "${item.title}" at ${item.company}. Check the official company website for application details.`,
      date: new Date().toLocaleString(),
      read: false,
    };

    localStorage.setItem(
      "careerNotifications",
      JSON.stringify([notification, ...existing])
    );

    toast.info("Saved to your notifications.");
  }

  return (
    <div className="page-content">
      <h1>Opportunities</h1>
      <p>Explore sample jobs and internships that match your interests.</p>

      <div className="opportunity-controls">
        <label htmlFor="opportunity-filter">Opportunity type</label>
        <select
          id="opportunity-filter"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
        >
          <option>All</option>
          <option>Internship</option>
          <option>Job</option>
        </select>

        <button
          type="button"
          className={showSaved ? "saved-filter active" : "saved-filter"}
          onClick={() => setShowSaved((previous) => !previous)}
        >
          {showSaved ? "Show All" : "Show Bookmarks"} ({bookmarks.length})
        </button>
      </div>

      <div className="opportunities-grid">
        {visibleOpportunities.map((item) => (
          <article className="opportunity-card" key={item.id}>
            <div className="opportunity-card-top">
              <span className="opportunity-type">{item.type}</span>
              <button
                type="button"
                className="bookmark-button"
                onClick={() => toggleBookmark(item.id)}
                aria-label={
                  bookmarks.includes(item.id)
                    ? "Remove bookmark"
                    : "Bookmark opportunity"
                }
              >
                {bookmarks.includes(item.id) ? "★ Saved" : "☆ Save"}
              </button>
            </div>

            <h3>{item.title}</h3>
            <p className="opportunity-company">{item.company}</p>
            <p>{item.description}</p>

            <div className="project-tags">
              {item.skills.map((skill) => (
                <span key={skill}>{skill}</span>
              ))}
            </div>

            <button
              type="button"
              onClick={() => applyForOpportunity(item)}
            >
              View Application Reminder
            </button>
          </article>
        ))}

        {visibleOpportunities.length === 0 && (
          <p>No opportunities found for this filter.</p>
        )}
      </div>

      <p className="opportunity-note">
        Demo data only. These are sample listings, not verified live vacancies.
        The reminder button does not submit a real job application.
      </p>
    </div>
  );
}

