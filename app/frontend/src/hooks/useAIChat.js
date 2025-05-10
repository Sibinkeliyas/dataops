import { useState } from 'react';

export const useAIChat = () => {
  const [isLoading, setIsLoading] = useState(false);

  const sendMessage = async (message) => {
    setIsLoading(true);
    // Simulated API call to AI service
    await new Promise(resolve => setTimeout(resolve, 1000));
    setIsLoading(false);
    // Return a mock response for now
    return `This is a simulated AI response to: "${message}"`;
  };

  return { sendMessage, isLoading };
};