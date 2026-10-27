
import { useNavigate, NavLink, Outlet } from "react-router-dom";

const menuItems = [
  { name: "Dashboard", path: "/" },
  { name: "My Profile", path: "/profile" },
  { name: "My Skills", path: "/skills" },
  { name: "Skill Gap", path: "/skill-gap" },
  { name: "Careers", path: "/careers" },
  { name: "Career Preferences", path: "/feedback" },
  { name: "Learning Roadmap", path: "/roadmap" },
  { name: "Projects", path: "/projects" },
  { name: "Opportunities", path: "/opportunities" },
  { name: "Notifications", path: "/notifications" },
  { name: "What-if Analysis", path: "/what-if" },
  { name: "Career Graph", path: "/graph" },
  { name: "Admin", path: "/admin" },
];

export default function Layout() {
  const navigate = useNavigate();

  function handleLogout() {
    localStorage.removeItem("token");
    localStorage.removeItem("accessToken");
    localStorage.removeItem("currentUser");

    navigate("/login", { replace: true });
  }

  return (
    <div className="app-layout">
      <aside className="sidebar">
        <h2 className="brand">CareerPath AI</h2>

        <nav className="sidebar-menu">
          {menuItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.path === "/"}
              className={({ isActive }) =>
                isActive ? "nav-link active" : "nav-link"
              }
            >
              {item.name}
            </NavLink>
          ))}
        </nav>
      </aside>

      <div className="main-area">
        <header className="navbar">
          <div>
            <h3>Career Development</h3>
            <p>Build your future, one skill at a time.</p>
          </div>

          <div className="user-avatar">S</div>

          <button onClick={handleLogout}>Logout</button>
        </header>

        <main className="page-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
