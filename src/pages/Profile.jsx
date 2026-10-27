import { useEffect, useState } from "react";
import { toast } from "react-toastify";
import api from "../api";

export default function Profile() {
  const savedUser = JSON.parse(
    localStorage.getItem("currentUser") || "{}"
  );

  const [username] = useState(savedUser.username || "");

  const [form, setForm] = useState({
    full_name: "",
    college: "",
    year_of_study: 3,
    target_role: "",
    interests: "",
    weekly_availability: 5,
  });

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    async function loadProfile() {
      try {
        const response = await api.get("/profile");
        const data = response.data;

        setForm({
          full_name: data.full_name || "",
          college: data.college || "",
          year_of_study: data.year_of_study ?? 3,
          target_role: data.target_role || "",
          interests: data.interests || "",
          weekly_availability: data.weekly_availability ?? 5,
        });
      } catch (error) {
        toast.error(
          error.response?.data?.detail ||
            "Unable to load profile. Please try again."
        );
      } finally {
        setLoading(false);
      }
    }

    loadProfile();
  }, []);

  function handleChange(event) {
    const { name, value } = event.target;

    setForm((previous) => ({
      ...previous,
      [name]:
        name === "year_of_study" ||
        name === "weekly_availability"
          ? Number(value)
          : value,
    }));
  }

  async function handleSubmit(event) {
    event.preventDefault();

    if (!form.full_name.trim()) {
      toast.error("Please enter your full name.");
      return;
    }

    if (!form.college.trim()) {
      toast.error("Please enter your college name.");
      return;
    }

    if (!form.target_role.trim()) {
      toast.error("Please enter your target career role.");
      return;
    }

    setSaving(true);

    try {
      const payload = {
        ...form,
        full_name: form.full_name.trim(),
        college: form.college.trim(),
        target_role: form.target_role.trim(),
        interests: form.interests.trim(),
      };

      const response = await api.put("/profile", payload);

      const updatedUser = {
        ...savedUser,
        name: payload.full_name,
        full_name: payload.full_name,
        username,
      };

      localStorage.setItem(
        "currentUser",
        JSON.stringify(updatedUser)
      );

      toast.success(
        response.data?.message || "Profile updated successfully!"
      );
    } catch (error) {
      const detail = error.response?.data?.detail;

      toast.error(
        typeof detail === "string"
          ? detail
          : "Unable to save profile. Please check the details and try again."
      );
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return (
      <div className="page-content">
        <h1>My Profile</h1>
        <p>Loading your profile...</p>
      </div>
    );
  }

  return (
    <div className="page-content">
      <h1>My Profile</h1>
      <p>Manage your career profile information.</p>

      <form className="profile-form" onSubmit={handleSubmit}>
        <label htmlFor="profile-name">Full Name</label>
        <input
          id="profile-name"
          name="full_name"
          value={form.full_name}
          onChange={handleChange}
          placeholder="Enter your full name"
          maxLength={100}
          required
        />

        <label htmlFor="profile-username">Username / Email</label>
        <input
          id="profile-username"
          value={username}
          readOnly
        />

        <label htmlFor="profile-college">College Name</label>
        <input
          id="profile-college"
          name="college"
          value={form.college}
          onChange={handleChange}
          placeholder="Enter your college name"
          maxLength={150}
          required
        />

        <label htmlFor="profile-year">Year of Study</label>
        <select
          id="profile-year"
          name="year_of_study"
          value={form.year_of_study}
          onChange={handleChange}
        >
          {[1, 2, 3, 4, 5, 6].map((year) => (
            <option key={year} value={year}>
              {year}
              {year === 1
                ? "st"
                : year === 2
                ? "nd"
                : year === 3
                ? "rd"
                : "th"}{" "}
              Year
            </option>
          ))}
        </select>

        <label htmlFor="profile-role">Target Career Role</label>
        <input
          id="profile-role"
          name="target_role"
          value={form.target_role}
          onChange={handleChange}
          placeholder="e.g. Frontend Developer, AI Engineer"
          maxLength={100}
          required
        />

        <label htmlFor="profile-interests">Interests</label>
        <textarea
          id="profile-interests"
          name="interests"
          value={form.interests}
          onChange={handleChange}
          placeholder="e.g. Web Development, AI, Data Structures"
          rows={4}
        />

        <label htmlFor="profile-availability">
          Weekly Learning Availability (hours)
        </label>
        <input
          id="profile-availability"
          type="number"
          name="weekly_availability"
          value={form.weekly_availability}
          onChange={handleChange}
          min={0}
          max={100}
        />

        <button type="submit" disabled={saving}>
          {saving ? "Saving..." : "Save Changes"}
        </button>
      </form>
    </div>
  );
}