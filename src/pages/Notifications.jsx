
import { useEffect, useState } from "react";

export default function Notifications() {
  const [notifications, setNotifications] = useState(() => {
    try {
      return JSON.parse(
        localStorage.getItem("careerNotifications") || "[]"
      );
    } catch {
      return [];
    }
  });

  useEffect(() => {
    localStorage.setItem(
      "careerNotifications",
      JSON.stringify(notifications)
    );
  }, [notifications]);

  function markAllRead() {
    setNotifications((previous) =>
      previous.map((item) => ({ ...item, read: true }))
    );
  }

  function clearNotifications() {
    setNotifications([]);
  }

  return (
    <div className="page-content">
      <h1>Notifications</h1>
      <p>Keep track of reminders from your career platform.</p>

      <div className="notification-actions">
        <button type="button" onClick={markAllRead}>
          Mark all as read
        </button>
        <button
          type="button"
          className="cancel-button"
          onClick={clearNotifications}
        >
          Clear all
        </button>
      </div>

      {notifications.length === 0 ? (
        <div className="projects-empty">
          <h3>No notifications yet</h3>
          <p>Your opportunity reminders will appear here.</p>
        </div>
      ) : (
        <div className="notification-list">
          {notifications.map((item) => (
            <article
              key={item.id}
              className={`notification-card ${item.read ? "read" : "unread"}`}
            >
              <div>
                <p>{item.message}</p>
                <small>{item.date}</small>
              </div>

              {!item.read && (
                <button
                  type="button"
                  onClick={() =>
                    setNotifications((previous) =>
                      previous.map((notification) =>
                        notification.id === item.id
                          ? { ...notification, read: true }
                          : notification
                      )
                    )
                  }
                >
                  Mark read
                </button>
              )}
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
