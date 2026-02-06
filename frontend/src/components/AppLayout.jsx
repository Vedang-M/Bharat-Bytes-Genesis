import { Outlet } from "react-router-dom";
import Navigation from "./Navigation";

const AppLayout = () => {
  return (
    <>
      <Navigation />
      <Outlet />
    </>
  );
};

export default AppLayout;
