import { HomeIcon, LayoutDashboardIcon, UserIcon } from "lucide-react";
import Index from "./pages/Index.jsx";
import Management from "./pages/Management.jsx";

export const navItems = [
  {
    title: "Home",
    to: "/",
    icon: <HomeIcon className="h-4 w-4" />,
    page: <Index />,
  },
  {
    title: "Profile",
    to: "/profile",
    icon: <UserIcon className="h-4 w-4" />,
    children: [
      {
        title: "Admin View",
        to: "/management",
        icon: <LayoutDashboardIcon className="h-4 w-4" />,
        page: <Management />,
      },
    ],
  },
];