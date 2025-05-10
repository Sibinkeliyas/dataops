import React from "react";
import { NavLink, useLocation } from "react-router-dom";
import {
  Home,
  Database,
  BarChart2,
  Brain,
  Cog,
  MessageSquare,
  Glasses,
  GitBranch,
  HelpCircle,
  Menu,
  LayoutDashboard,
  ChartArea,
  Users,
} from "lucide-react";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { useSelector } from "react-redux";

const navItems = [
  { icon: Home, label: "Home", path: "/" },
  { icon: LayoutDashboard, label: "Dashboard", path: "/dashboard" },
  { icon: Users, label: "Users", path: "/admin", role: "admin" },
  { icon: Database, label: "Data Catalog", path: "/data-catalog" },
  { icon: BarChart2, label: "BI & Analytics", path: "/bi-analytics" },
  { icon: Brain, label: "Machine Learning & AI", path: "/machine-learning-ai" },
  { icon: Cog, label: "Data Engineering", path: "/data-engineering" },
  { icon: MessageSquare, label: "AI Copilot", path: "/ai-copilot" },
  { icon: Glasses, label: "AR Solutions", path: "/ar-solutions" },
  { icon: GitBranch, label: "DataOps Portal", path: "/dataops-portal" },
  { icon: HelpCircle, label: "Support & Resources", path: "/support-resources" },
  { icon: ChartArea, label: "Ask Query", path: "/ask-queries" },
];

const Sidebar = ({ isExpanded, toggleSidebar }) => {
  const location = useLocation();
  const { isAuthenticated, user } = useSelector((state) => state.authReducer);

  const sidebarClasses = `
    bg-gray-800 text-white transition-all duration-300 ease-in-out flex flex-col
    ${isExpanded ? "w-48" : "w-16"}
  `;

  const iconClasses = `
    filter drop-shadow-[0_0_2px_rgba(255,255,255,0.8)]
  `;

  return (
    <aside className={sidebarClasses}>
      <div className="p-4">
        <button
          onClick={toggleSidebar}
          className="w-full flex justify-center items-center p-2 rounded-lg hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <Menu size={24} className={iconClasses} />
        </button>
      </div>
      <nav className="flex-1 overflow-y-auto">
        <ul className="space-y-2">
          {navItems.map((item) => {
            if (!item.role || (isAuthenticated && item.role?.toLowerCase() === user.role?.role?.toLowerCase())) {
              return (
                <li key={item.path}>
                  <TooltipProvider>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <NavLink
                          to={item.path}
                          className={({ isActive }) => `
                        flex flex-col items-center justify-center p-2 rounded-lg hover:bg-gray-700
                        ${isActive ? "bg-gray-700" : ""}
                        ${isExpanded ? "h-16" : "h-16"}
                      `}
                        >
                          <item.icon className={`${isExpanded ? "h-6 w-6 mb-1" : "h-6 w-6"} ${iconClasses}`} />
                          {isExpanded && <span className="text-xs text-center">{item.label}</span>}
                        </NavLink>
                      </TooltipTrigger>
                      {!isExpanded && (
                        <TooltipContent side="right">
                          <p>{item.label}</p>
                        </TooltipContent>
                      )}
                    </Tooltip>
                  </TooltipProvider>
                </li>
              );
            }
            return null;
          })}
        </ul>
      </nav>
    </aside>
  );
};

export default Sidebar;
