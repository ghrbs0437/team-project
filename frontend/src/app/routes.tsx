import { createBrowserRouter } from "react-router";
import Root from "./components/Root";
import Dashboard from "./components/Dashboard";
import Signup from "./components/Signup";
import Profile from "./components/Profile";
import Login from "./components/Login";
import { useAuth } from "./auth";

function ProtectedRoot() {
  const { isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return <Login />;
  }

  return <Root />;
}

export const router = createBrowserRouter([
  { path: "/login", Component: Login },
  { path: "/signup", Component: Signup },
  {
    path: "/",
    Component: ProtectedRoot,
    children: [
      { index: true, Component: Dashboard },
      { path: "profile", Component: Profile },
    ],
  },
]);
