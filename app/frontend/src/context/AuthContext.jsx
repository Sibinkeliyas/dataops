import { msalConfig } from "@/authConfig";
import { Spinner } from "@/components/ui/Spinner";
import { loginSuccess, logoutSuccess } from "@/state/slices/auth";
import { getUser } from "@/utils/api/login";
import { PublicClientApplication } from "@azure/msal-browser";
import { MsalProvider } from "@azure/msal-react";
import { useEffect, useState } from "react";
import { useDispatch } from "react-redux";

const msalInstance = new PublicClientApplication(msalConfig);

const AuthContext = ({ children }) => {
  const dispatch = useDispatch();
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const initializeAuth = async () => {
      try {
        await msalInstance.initialize();
        const accounts = msalInstance.getAllAccounts();
        if (accounts.length > 0) {
          const res = await getUser(accounts[0].username)
          if(!res.user) {
            await msalInstance.clearCache();
            dispatch(logoutSuccess());
          } else dispatch(loginSuccess({...accounts[0], id: res.user.id, role: res.user.role}));
        } else {
          dispatch(logoutSuccess());
        }
      } catch (error) {
        dispatch(logoutSuccess());
      } finally {
        setIsLoading(false);
      }
    };

    initializeAuth();
  }, []);

  if (isLoading) {
    return (
      <div className="min-h-screen flex justify-center items-center">
        <Spinner size="medium" />
      </div>
    );
  }

  return <MsalProvider instance={msalInstance}>{children}</MsalProvider>;
};

export default AuthContext;
