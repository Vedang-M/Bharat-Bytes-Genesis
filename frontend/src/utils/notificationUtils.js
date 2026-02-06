// Notification Simulation Utility
const NOTIFICATION_KEY = "village_notifications";

export const broadcastNotification = (message, type = "info") => {
  const notifications = JSON.parse(
    localStorage.getItem(NOTIFICATION_KEY) || "[]",
  );
  const newNotification = {
    id: Date.now(),
    message,
    type,
    timestamp: new Date().toISOString(),
    isRead: false,
  };

  localStorage.setItem(
    NOTIFICATION_KEY,
    JSON.stringify([...notifications, newNotification]),
  );

  // Trigger a custom event for the same tab to listen to
  window.dispatchEvent(new Event("new_notification"));
};

export const getNotifications = () => {
  return JSON.parse(localStorage.getItem(NOTIFICATION_KEY) || "[]");
};

export const clearNotifications = () => {
  localStorage.removeItem(NOTIFICATION_KEY);
};
