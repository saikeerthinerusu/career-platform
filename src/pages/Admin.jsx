
import { useEffect, useState } from "react";
import { toast } from "react-toastify";

const defaultRoles = [
  {
    id: 1,
    title: "Frontend Developer",
    description: "Build responsive user interfaces.",
    skills: ["HTML", "CSS", "JavaScript", "React"],
  },
  {
    id: 2,
    title: "AI Engineer",
    description: "Develop AI and machine learning solutions.",
    skills: ["Python", "Machine Learning", "Statistics"],
  },
];

const defaultOpportunities = [
  {
    id: 1,
    title: "Frontend Developer Intern",
    company: "Example Tech",
    type: "Internship",
    description: "Work on frontend development.",
    skills: ["HTML", "CSS", "JavaScript", "React"],
  },
];

function loadData(key, defaults) {
  try {
    const saved = localStorage.getItem(key);
    return saved === null ? defaults : JSON.parse(saved);
  } catch {
    return defaults;
  }
}

export default function Admin() {
  const [section, setSection] = useState("roles");
  const [roles, setRoles] = useState(() =>
    loadData("adminCareerRoles", defaultRoles)
  );
  const [opportunities, setOpportunities] = useState(() =>
    loadData("adminOpportunities", defaultOpportunities)
  );

  const emptyForm = {
    title: "",
    description: "",
    skills: "",
    company: "",
    type: "Internship",
  };

  const [form, setForm] = useState(emptyForm);
  const [editingId, setEditingId] = useState(null);

  useEffect(() => {
    localStorage.setItem("adminCareerRoles", JSON.stringify(roles));
  }, [roles]);

  useEffect(() => {
    localStorage.setItem(
      "adminOpportunities",
      JSON.stringify(opportunities)
    );
  }, [opportunities]);

  function handleChange(event) {
    setForm({ ...form, [event.target.name]: event.target.value });
  }

  function resetForm() {
    setForm(emptyForm);
    setEditingId(null);
  }

  function handleSubmit(event) {
    event.preventDefault();

    if (!form.title.trim() || !form.description.trim()) {
      toast.error("Enter a title and description.");
      return;
    }

    const commonData = {
      title: form.title.trim(),
      description: form.description.trim(),
      skills: form.skills
        .split(",")
        .map((skill) => skill.trim())
        .filter(Boolean),
    };

    if (section === "roles") {
      if (editingId !== null) {
        setRoles((previous) =>
          previous.map((item) =>
            item.id === editingId ? { ...item, ...commonData } : item
          )
        );
        toast.success("Career role updated!");
      } else {
        setRoles((previous) => [
          ...previous,
          { id: Date.now(), ...commonData },
        ]);
        toast.success("Career role added!");
      }
    } else {
      if (!form.company.trim()) {
        toast.error("Enter the company name.");
        return;
      }

      const opportunityData = {
        ...commonData,
        company: form.company.trim(),
        type: form.type,
      };

      if (editingId !== null) {
        setOpportunities((previous) =>
          previous.map((item) =>
            item.id === editingId
              ? { ...item, ...opportunityData }
              : item
          )
        );
        toast.success("Opportunity updated!");
      } else {
        setOpportunities((previous) => [
          ...previous,
          { id: Date.now(), ...opportunityData },
        ]);
        toast.success("Opportunity added!");
      }
    }

    resetForm();
  }

  function handleEdit(item) {
    setEditingId(item.id);
    setForm({
      title: item.title,
      description: item.description,
      skills: item.skills.join(", "),
      company: item.company || "",
      type: item.type || "Internship",
    });
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function handleDelete(id) {
    const confirmed = window.confirm("Delete this item?");
    if (!confirmed) return;

    if (section === "roles") {
      setRoles((previous) => previous.filter((item) => item.id !== id));
    } else {
      setOpportunities((previous) =>
        previous.filter((item) => item.id !== id)
      );
    }

    if (editingId === id) resetForm();
    toast.success("Item deleted.");
  }

  const items = section === "roles" ? roles : opportunities;

  return (
    <div className="admin-page">
      <div className="admin-heading">
        <div>
          <h1>Admin Panel</h1>
          <p>Manage career roles and job opportunities.</p>
        </div>
        <span className="admin-badge">Demo Admin</span>
      </div>

      <div className="admin-stats">
        <div className="admin-stat-card">
          <span>Total Career Roles</span>
          <h2>{roles.length}</h2>
        </div>
        <div className="admin-stat-card">
          <span>Total Opportunities</span>
          <h2>{opportunities.length}</h2>
        </div>
      </div>

      <div className="admin-tabs">
        <button
          className={section === "roles" ? "admin-tab active" : "admin-tab"}
          onClick={() => {
            setSection("roles");
            resetForm();
          }}
        >
          Career Roles
        </button>
        <button
          className={
            section === "opportunities" ? "admin-tab active" : "admin-tab"
          }
          onClick={() => {
            setSection("opportunities");
            resetForm();
          }}
        >
          Jobs & Internships
        </button>
      </div>

      <form className="admin-form" onSubmit={handleSubmit}>
        <h2>
          {editingId !== null ? "Edit" : "Add"}{" "}
          {section === "roles" ? "Career Role" : "Opportunity"}
        </h2>

        <label>Title</label>
        <input
          name="title"
          value={form.title}
          onChange={handleChange}
          placeholder={
            section === "roles"
              ? "e.g. Data Analyst"
              : "e.g. Software Developer Intern"
          }
          required
        />

        {section === "opportunities" && (
          <>
            <label>Company</label>
            <input
              name="company"
              value={form.company}
              onChange={handleChange}
              placeholder="Company name"
              required
            />

            <label>Opportunity Type</label>
            <select name="type" value={form.type} onChange={handleChange}>
              <option>Internship</option>
              <option>Full-time Job</option>
              <option>Part-time Job</option>
            </select>
          </>
        )}

        <label>Description</label>
        <textarea
          name="description"
          value={form.description}
          onChange={handleChange}
          placeholder="Write a short description"
          required
        />

        <label>Required Skills (comma-separated)</label>
        <input
          name="skills"
          value={form.skills}
          onChange={handleChange}
          placeholder="Python, SQL, Communication"
        />

        <div className="admin-form-actions">
          <button type="submit" className="admin-primary-button">
            {editingId !== null ? "Save Changes" : "Add Item"}
          </button>
          {editingId !== null && (
            <button
              type="button"
              className="admin-cancel-button"
              onClick={resetForm}
            >
              Cancel
            </button>
          )}
        </div>
      </form>

      <div className="admin-list">
        <h2>
          {section === "roles" ? "Career Roles" : "Jobs & Internships"} (
          {items.length})
        </h2>

        {items.length === 0 ? (
          <p>No items yet. Use the form above to add one.</p>
        ) : (
          items.map((item) => (
            <div className="admin-item" key={item.id}>
              <div className="admin-item-content">
                <h3>{item.title}</h3>
                {item.company && <p>Company: {item.company}</p>}
                {item.type && <p>Type: {item.type}</p>}
                <p>{item.description}</p>
                <div className="admin-skills">
                  {item.skills.map((skill) => (
                    <span key={skill}>{skill}</span>
                  ))}
                </div>
              </div>
              <div className="admin-item-actions">
                <button onClick={() => handleEdit(item)}>Edit</button>
                <button
                  className="admin-delete-button"
                  onClick={() => handleDelete(item.id)}
                >
                  Delete
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
