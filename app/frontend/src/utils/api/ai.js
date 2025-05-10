import { AI_API_BASE_URL } from "../../config";

export const chatApi = async (request, token) => {
  try {
    
    const response = await fetch(`${AI_API_BASE_URL}/chat/stream`, {
      method: "POST",
      body: JSON.stringify(request),
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    });
    if(!response.body) return {success: false}
    return  response
  } catch (error) {
    return { success: false, error };
  }
};
