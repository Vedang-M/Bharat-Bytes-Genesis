import { useEffect } from "react";
import { Outlet } from "react-router-dom";
import Navigation from "./Navigation";
import { toast } from "react-toastify";
import { getNotifications } from "../utils/notificationUtils";

const AppLayout = () => {
  useEffect(() => {
    const handleNewNotification = () => {
      const notifications = getNotifications();
      const latest = notifications[notifications.length - 1];
      if (latest) {
        toast.info(latest.message, {
          position: "top-right",
          autoClose: 5000,
          icon: "📢",
        });
      }
    };

    window.addEventListener("new_notification", handleNewNotification);

    // Also listen for storage events (for multiple tabs)
    const handleStorageChange = (e) => {
      if (e.key === "village_notifications") {
        handleNewNotification();
      }
    };
    window.addEventListener("storage", handleStorageChange);

    return () => {
      window.removeEventListener("new_notification", handleNewNotification);
      window.removeEventListener("storage", handleStorageChange);
    };
  }, []);

  return (
    <>
      <Navigation />
      <Outlet />
    </>
  );
};

export default AppLayout;
