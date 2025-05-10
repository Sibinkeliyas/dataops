import { LogLevel } from "@azure/msal-browser";
import { AI_API_BASE_URL, API_BASE_URL } from "./config";
const appServicesAuthTokenUrl = ".auth/me";

async function fetchAuthSetup() {
    const response = await fetch(`${AI_API_BASE_URL}/auth_setup`);
    if (!response.ok) {
        throw new Error(`auth setup response was not ok: ${response.status}`);
    }
    return await response.json();
}

const authSetup = await fetchAuthSetup();

export const msalConfig = authSetup.msalConfig

export const tokenRequest = authSetup.tokenRequest

export const getRedirectUri = () => {
    return window.location.origin + msalConfig.auth.redirectUri;
};



export const getToken = async (client, account) => {
    return client
        .acquireTokenSilent({
            ...tokenRequest,
            account,
            redirectUri: getRedirectUri()
        })
        .then(r => r.accessToken)
        .catch(error => {
            console.log(error);
            return undefined;
        });
};

/**
 * Scopes you add here will be prompted for user consent during sign-in.
 * By default, MSAL.js will add OIDC scopes (openid, profile, email) to any login request.
 */
export const loginRequest = {
    scopes: ["Files.Read"],
};