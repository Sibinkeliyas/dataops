import React, { useState, useRef, useEffect } from "react";
import { Bell, Search } from "lucide-react";
import { Input } from "@/components/ui/input";
import ProfileMenu from "./ProfileMenu";
import { cn } from "@/lib/utils";
import { useMsal } from "@azure/msal-react";
import { API_BASE_URL } from "@/config";
import { getToken, loginRequest } from "@/authConfig";
import { Button } from "./ui/button";
import { useDispatch, useSelector } from "react-redux";
import { loginSuccess, logoutSuccess } from "@/state/slices/auth";
import { getUser, loginUser } from "@/utils/api/login";
import { toast } from "sonner";
import allnexLogo from "../../public/allnex_AX_AI_Data_Platform_Logo_RGB.png";

const Header = ({ userEmail }) => {
  const { instance } = useMsal();
  const dispatch = useDispatch();

  const [isSearchExpanded, setIsSearchExpanded] = useState(false);
  const searchRef = useRef(null);

  const { isAuthenticated, user } = useSelector((state) => state.authReducer);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (searchRef.current && !searchRef.current.contains(event.target)) {
        setIsSearchExpanded(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  const iconStyle = "filter drop-shadow(0 0 2px rgba(255, 255, 255, 0.8))";

  const handleLoginPopup = async () => {
    try {
      const response = await instance.loginPopup({
        ...loginRequest,
      });
      const res = await getUser(response.account.username);
      if(!res.success || !res.user || !Object.values(res.user).length) {
        // await instance.clearCache();
        // toast.error("You don't have access to login");
        dispatch(loginSuccess({...response.account }));
      } else dispatch(loginSuccess({...response.account, role: res.user.role, id: res.user.id}));
    } catch (error) {
      console.log(error);
    }
  };

  const handleLogoutPopup = async () => {
    await instance.logoutPopup();
    dispatch(logoutSuccess());
  };

  return (
    <header className="fixed top-0 right-0 z-50 bg-transparent">
      <div className="px-4 sm:px-6 lg:px-8">
        <div className="flex justify-end items-center py-4 pb-6">
          <div className="flex items-center space-x-4 max-w-3xl">
            <img src={allnexLogo} alt="Mithril Logo" className={`h-16 w-auto ${iconStyle}`} />
            <div
              ref={searchRef}
              className={cn("relative transition-all duration-300 ease-in-out", isSearchExpanded ? "w-64" : "w-8")}
            >
              <Input
                type="text"
                placeholder={isSearchExpanded ? "Search..." : ""}
                className={cn(
                  "pl-8 pr-4 py-2 w-full rounded-md border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white transition-all duration-300 ease-in-out",
                  isSearchExpanded ? "opacity-100" : "opacity-0"
                )}
                onFocus={() => setIsSearchExpanded(true)}
              />
              <Search
                className={`absolute left-2 top-1/2 transform -translate-y-1/2 text-gray-400 cursor-pointer ${iconStyle}`}
                size={18}
                onClick={() => setIsSearchExpanded(!isSearchExpanded)}
              />
            </div>
            <div className="flex items-center space-x-2">
              <button
                className={`p-2 rounded-full hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 ${iconStyle}`}
              >
                <Bell size={20} />
              </button>
              {isAuthenticated ? (
                <ProfileMenu iconStyle={iconStyle} userEmail={userEmail} />
              ) : (
                <Button
                  className="bg-[#101010] text-[#fff] hover:bg-[#101010]"
                  // text={loggedIn ? `Logout\n${username}` : "Login"}
                  onClick={isAuthenticated ? handleLogoutPopup : handleLoginPopup}
                >
                  {isAuthenticated ? user.name : "Login"}
                </Button>
              )}
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
