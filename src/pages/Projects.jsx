
import { useEffect, useState } from "react";
import { toast } from "react-toastify";
import api from "../api";

export default function Projects() {
  const [projects, setProjects] = useState([]);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [technologies, setTechnologies] = useState("");
  const [skills, setSkills] = useState("");
  const [editingId, setEditingId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    loadProjects();
  }, []);

  async function loadProjects() {
    try {
      const response = await api.get("/projects");

      setProjects(
        response.data.map((project) => ({
          ...project,
          technologies: (project.technologies || "")
            .split(",")
            .map((item) => item.trim())
            .filter(Boolean),
          skills: (project.skills || "")
            .split(",")
            .map((item) => item.trim())
            .filter(Boolean),
        }))
      );
    } catch (error) {
      toast.error(
        error.response?.data?.detail || "Failed to load projects."
      );
    } finally {
      setLoading(false);
    }
  }

  function resetForm() {
    setTitle("");
    setDescription("");
    setTechnologies("");
    setSkills("");
    setEditingId(null);
  }

  async function handleSubmit(event) {
    event.preventDefault();

    if (!title.trim() || !description.trim() || !technologies.trim()) {
      toast.error("Please fill in the required fields.");
      return;
    }

    const projectData = {
      title: title.trim(),
      description: description.trim(),
      technologies: technologies
        .split(",")
        .map((item) => item.trim())
        .filter(Boolean)
        .join(", "),
      skills: skills
        .split(",")
        .map((item) => item.trim())
        .filter(Boolean)
        .join(", "),
    };

    setSaving(true);

    try {
      if (editingId !== null) {
        await api.put(`/projects/${editingId}`, projectData);
        toast.success("Project updated!");
      } else {
        await api.post("/projects", projectData);
        toast.success("Project added!");
      }

      resetForm();
      await loadProjects();
    } catch (error) {
      toast.error(
        error.response?.data?.detail || "Failed to save project."
      );
    } finally {
      setSaving(false);
    }
  }

  function handleEdit(project) {
    setTitle(project.title);
    setDescription(project.description);
    setTechnologies(project.technologies.join(", "));
    setSkills(project.skills.join(", "));
    setEditingId(project.id);

    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  async function handleDelete(id) {
    const confirmed = window.confirm(
      "Are you sure you want to delete this project?"
    );

    if (!confirmed) return;

    try {
      await api.delete(`/projects/${id}`);
      setProjects((previous) =>
        previous.filter((project) => project.id !== id)
      );

      if (editingId === id) resetForm();

      toast.success("Project deleted.");
    } catch (error) {
      toast.error(
        error.response?.data?.detail || "Failed to delete project."
      );
    }
  }

  return (
    <div className="page-content">
      <h1>My Projects</h1>
      <p>Add your projects and connect them with the skills you used.</p>

      <form className="project-form" onSubmit={handleSubmit}>
        <div className="project-field">
          <label htmlFor="project-title">Project title *</label>
          <input
            id="project-title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Example: Weather Web Application"
            required
          />
        </div>

        <div className="project-field">
          <label htmlFor="project-description">Description *</label>
          <textarea
            id="project-description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="What does your project do?"
            rows={3}
            required
          />
        </div>

        <div className="project-field">
          <label htmlFor="project-tech">Technologies *</label>
          <input
            id="project-tech"
            value={technologies}
            onChange={(e) => setTechnologies(e.target.value)}
            placeholder="React, JavaScript, CSS"
            required
          />
          <small>Separate technologies with commas.</small>
        </div>

        <div className="project-field">
          <label htmlFor="project-skills">Related skills</label>
          <input
            id="project-skills"
            value={skills}
            onChange={(e) => setSkills(e.target.value)}
            placeholder="React, API Integration, Problem Solving"
          />
          <small>Separate skills with commas.</small>
        </div>

        <div className="project-form-actions">
          <button type="submit" disabled={saving}>
            {saving
              ? "Saving..."
              : editingId !== null
                ? "Update Project"
                : "Add Project"}
          </button>

          {editingId !== null && (
            <button
              type="button"
              className="cancel-button"
              onClick={resetForm}
              disabled={saving}
            >
              Cancel
            </button>
          )}
        </div>
      </form>

      <h2 className="projects-heading">
        Your Projects ({projects.length})
      </h2>

      {loading ? (
        <p>Loading projects...</p>
      ) : projects.length === 0 ? (
        <div className="projects-empty">
          <h3>No projects yet</h3>
          <p>Add your first project using the form above.</p>
        </div>
      ) : (
        <div className="projects-grid">
          {projects.map((project) => (
            <article className="project-card" key={project.id}>
              <h3>{project.title}</h3>
              <p>{project.description}</p>

              <h4>Technologies</h4>
              <div className="project-tags">
                {project.technologies.map((technology) => (
                  <span key={technology}>{technology}</span>
                ))}
              </div>

              {project.skills.length > 0 && (
                <>
                  <h4>Related Skills</h4>
                  <div className="project-tags skill-tags">
                    {project.skills.map((skill) => (
                      <span key={skill}>{skill}</span>
                    ))}
                  </div>
                </>
              )}

              <div className="project-card-actions">
                <button
                  type="button"
                  onClick={() => handleEdit(project)}
                >
                  Edit
                </button>

                <button
                  type="button"
                  className="delete-skill-button"
                  onClick={() => handleDelete(project.id)}
                >
                  Delete
                </button>
              </div>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
