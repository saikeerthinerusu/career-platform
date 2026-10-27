
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import api from "../api";

export default function Auth({ mode = "login" }) {
  const isLogin = mode === "login";
  const navigate = useNavigate();

  const [form, setForm] = useState({
    name: "",
    username: "",
    password: "",
    confirmPassword: "",
  });

  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

  function handleChange(event) {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();

    const nextErrors = {};
    const username = form.username.trim().toLowerCase();

    if (!isLogin && !form.name.trim()) {
      nextErrors.name = "Name is required.";
    }

    if (!username) {
      nextErrors.username = "Username or email is required.";
    }

    if (!form.password) {
      nextErrors.password = "Password is required.";
    }

    if (!isLogin && form.password.length < 8) {
      nextErrors.password = "Password must contain at least 8 characters.";
    }

    if (!isLogin && form.password !== form.confirmPassword) {
      nextErrors.confirmPassword = "Passwords do not match.";
    }

    setErrors(nextErrors);
    if (Object.keys(nextErrors).length > 0) return;

    setLoading(true);

    try {
      if (isLogin) {
        // FastAPI OAuth2 password login expects form data.
        const body = new URLSearchParams();
        body.append("username", username);
        body.append("password", form.password);

        const response = await api.post("/auth/login", body, {
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
          },
        });

        const token =
          response.data.access_token || response.data.token;

        if (!token) {
          throw new Error("Backend did not return an access token.");
        }

        localStorage.setItem("token", token);
        localStorage.setItem("accessToken", token);

        try {
          const userResponse = await api.get("/auth/me");
          localStorage.setItem(
            "currentUser",
            JSON.stringify(userResponse.data)
          );
        } catch {
          // Login still succeeds if the optional user-details request fails.
        }

        toast.success("Login successful!");
        navigate("/");
      } else {
        // Register using the backend's expected JSON fields.
        const response = await api.post("/auth/register", {
          username,
          email: username.includes("@") ? username : `${username}@example.com`,
          password: form.password,
        });

        toast.success(
          response.data?.message || "Registration successful! Please log in."
        );
        navigate("/login");
      }
    } catch (error) {
      const detail = error.response?.data?.detail;
      const message =
        typeof detail === "string"
          ? detail
          : error.message || "Something went wrong. Please try again.";

      toast.error(message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <Link to="/" className="auth-brand">
          CareerPath AI
        </Link>

        <h1>{isLogin ? "Welcome back!" : "Create your account"}</h1>

        <p className="auth-description">
          {isLogin
            ? "Continue building your career journey."
            : "Start discovering your career opportunities."}
        </p>

        <form onSubmit={handleSubmit} noValidate>
          {!isLogin && (
            <div className="form-field">
              <label htmlFor="name">Full name</label>
              <input
                id="name"
                name="name"
                value={form.name}
                onChange={handleChange}
                placeholder="Enter your full name"
              />
              {errors.name && (
                <span className="field-error">{errors.name}</span>
              )}
            </div>
          )}

          <div className="form-field">
            <label htmlFor="username">Username or email</label>
            <input
              id="username"
              name="username"
              value={form.username}
              onChange={handleChange}
              placeholder="Enter your username or email"
              autoComplete="username"
            />
            {errors.username && (
              <span className="field-error">{errors.username}</span>
            )}
          </div>

          <div className="form-field">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              name="password"
              type="password"
              value={form.password}
              onChange={handleChange}
              placeholder="Enter your password"
              autoComplete={isLogin ? "current-password" : "new-password"}
            />
            {errors.password && (
              <span className="field-error">{errors.password}</span>
            )}
          </div>

          {!isLogin && (
            <div className="form-field">
              <label htmlFor="confirmPassword">Confirm password</label>
              <input
                id="confirmPassword"
                name="confirmPassword"
                type="password"
                value={form.confirmPassword}
                onChange={handleChange}
                placeholder="Re-enter your password"
                autoComplete="new-password"
              />
              {errors.confirmPassword && (
                <span className="field-error">{errors.confirmPassword}</span>
              )}
            </div>
          )}

          <button className="auth-submit" disabled={loading}>
            {loading
              ? "Please wait..."
              : isLogin
                ? "Log in"
                : "Create account"}
          </button>
        </form>

        <p className="auth-switch">
          {isLogin
            ? "Don't have an account?"
            : "Already have an account?"}{" "}
          <Link to={isLogin ? "/register" : "/login"}>
            {isLogin ? "Register" : "Log in"}
          </Link>
        </p>

        <p className="demo-notice">
          Connected to the CareerPath AI backend.
        </p>
      </div>
    </div>
  );
}
