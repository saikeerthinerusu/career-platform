import { useEffect, useState } from "react";
import { toast } from "react-toastify";
import api from "../api";

const levels = {
  Beginner: 1,
  Intermediate: 3,
  Advanced: 5,
};

function getLevel(proficiency) {
  if (proficiency >= 4) return "Advanced";
  if (proficiency >= 2) return "Intermediate";
  return "Beginner";
}

export default function Skills() {
  const [skills, setSkills] = useState([]);
  const [name, setName] = useState("");
  const [level, setLevel] = useState("Beginner");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [deletingId, setDeletingId] = useState(null);

  async function loadSkills() {
    try {
      const response = await api.get("/skills");
      setSkills(response.data);
    } catch (error) {
      toast.error(
        error.response?.data?.detail ||
          "Unable to load skills. Please try again."
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadSkills();
  }, []);

  async function handleSubmit(event) {
    event.preventDefault();

    const trimmedName = name.trim();

    if (!trimmedName) {
      toast.error("Please enter a skill name.");
      return;
    }

    const duplicate = skills.some(
      (skill) =>
        skill.name.toLowerCase() === trimmedName.toLowerCase()
    );

    if (duplicate) {
      toast.error("This skill already exists.");
      return;
    }

    setSaving(true);

    try {
      await api.post("/skills", {
        name: trimmedName,
        proficiency: levels[level],
        verification_status: "self_rated",
      });

      toast.success("Skill added successfully!");
      setName("");
      setLevel("Beginner");
      await loadSkills();
    } catch (error) {
      toast.error(
        error.response?.data?.detail ||
          "Unable to add skill. Please try again."
      );
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete(skillId) {
    setDeletingId(skillId);

    try {
      await api.delete(`/skills/${skillId}`);
      setSkills((previous) =>
        previous.filter((skill) => skill.id !== skillId)
      );
      toast.success("Skill deleted successfully!");
    } catch (error) {
      toast.error(
        error.response?.data?.detail ||
          "Unable to delete skill. Please try again."
      );
    } finally {
      setDeletingId(null);
    }
  }

  return (
    <div className="page-content">
      <h1>My Skills</h1>
      <p>Add and manage the skills you have learned.</p>

      <form className="skills-form" onSubmit={handleSubmit}>
        <div className="skill-input-group">
          <label htmlFor="skill-name">Skill name</label>
          <input
            id="skill-name"
            value={name}
            onChange={(event) => setName(event.target.value)}
            placeholder="Example: Java, React, Python"
            required
          />
        </div>

        <div className="skill-input-group">
          <label htmlFor="skill-level">Proficiency level</label>
          <select
            id="skill-level"
            value={level}
            onChange={(event) => setLevel(event.target.value)}
          >
            <option>Beginner</option>
            <option>Intermediate</option>
            <option>Advanced</option>
          </select>
        </div>

        <button type="submit" disabled={saving}>
          {saving ? "Adding..." : "Add Skill"}
        </button>
      </form>

      <h2 className="skills-heading">
        Your Skills ({skills.length})
      </h2>

      {loading ? (
        <p>Loading skills...</p>
      ) : skills.length === 0 ? (
        <p>No skills added yet. Add your first skill above.</p>
      ) : (
        <div className="skills-list">
          {skills.map((skill) => (
            <div className="skill-card" key={skill.id}>
              <div>
                <h3>{skill.name}</h3>
                <p>Level: {getLevel(skill.proficiency)}</p>
                <span className="skill-status">
                  {skill.verification_status === "verified"
                    ? "Verified"
                    : skill.verification_status === "confirmed"
                    ? "Confirmed"
                    : "Self-rated"}
                </span>
              </div>

              <div className="skill-actions">
                <button
                  type="button"
                  className="delete-skill-button"
                  onClick={() => handleDelete(skill.id)}
                  disabled={deletingId === skill.id}
                >
                  {deletingId === skill.id ? "Deleting..." : "Delete"}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}