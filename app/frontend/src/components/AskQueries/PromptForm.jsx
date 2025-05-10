import React, { useState } from "react";
import { Textarea } from "../ui/textarea";
import { Button } from "../ui/button";
import { Send } from "lucide-react";
import readNDJSONStream from "ndjson-readablestream";
import { chatApi } from "@/utils/api/ai";
import { DEFAULT_AI_SETTINGS } from "@/config";
import { useSearchParams } from "react-router-dom";
import { useMsal } from "@azure/msal-react";
import { getToken } from "@/authConfig";
import { useSelector } from "react-redux";

const PromptForm = ({ messages, setMessages, setIsStreaming, streamedAnswers, setStreamedAnswers }) => {
  const [searchParams] = useSearchParams();
  const { instance } = useMsal();
  const threadId = searchParams.get('thread');

  const { isAuthenticated, user } = useSelector((state) => state.authReducer);

  const [question, setQuestion] = useState("");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [conversationId, setConversationId] = useState(threadId || null)

  const handleSend = async () => {
    try {
      const newQuestion = question;
      setQuestion("");
      if(isAnalyzing) return
      setIsAnalyzing(true)
      let id = Date.now();
      setMessages((prev) => [...prev, { id: id, question: newQuestion, answer: "", isAnalyzing: true }]);
      const request = {
        messages: [{ content: newQuestion, role: "user" }],
        context: {
          overrides: DEFAULT_AI_SETTINGS,
        },
        session_state: null,
        conversation_id: conversationId || null,
        group_id: "",
        datetime: new Date(),
      };
      const account = await instance.getAllAccounts()
      const token = await getToken(instance, account[0]);
      const response = await chatApi(request, token);
      
      let answer = "";
      let askResponse = {};
      let messageId;

      const updateState = (newContent) => {
        return new Promise((resolve) => {
          setIsStreaming({ [id]: true });
          setTimeout(() => {
            answer += newContent;
            const latestResponse = {
              ...askResponse,
              message: { content: answer, role: askResponse?.message?.role },
            };
            setStreamedAnswers({ [id]: latestResponse });
            resolve(null);
          }, 33);
        });
      };

      for await (const event of readNDJSONStream(response.body)) {
        if (event["message_id"]) {
          messageId = event["message_id"];
        }
        if(event["conversation_id"]) {
          setConversationId(event["conversation_id"])
          window.history.replaceState(null, null, `?thread=${event["conversation_id"]}`);
        }

        if (event["context"] && event["context"]["data_points"]) {
          event["message"] = event["delta"];
          askResponse = event;
        } else if (event["delta"] && event["delta"]["content"] !== null) {
          await updateState(event["delta"]["content"]);
        } else if (event["context"]) {
          askResponse.context = { ...askResponse.context, ...event["context"] };
        } else if (event["error"]) {
          throw Error(event["error"]);
        }
      }

      const fullResponse = {
        ...askResponse,
        message: { content: answer, role: askResponse?.message?.role },
        id: messageId,
      };

      setMessages((prev) => [
        ...prev.map((message) => (message.id === id ? { ...message, response: fullResponse, isAnalyzing: false } : message)),
      ]);
      setIsStreaming({ [id]: false });
      setIsAnalyzing(false);
      return fullResponse;
    } catch (error) {
      console.log(error);
    }
  };

  return (
    <div className="absolute w-full bottom-4 left-0 px-2 lg:px-[15%] flex">
      <div className=" w-full relative">
        <Textarea
          disabled={isAnalyzing || !isAuthenticated}
          placeholder="Type your message here."
          value={question}
          className="pr-[50px] "
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => {
            if (e.keyCode === 13) {
              e.preventDefault();
              handleSend();
            }
          }}
        />
        <Button
          className="p-0 pt-[11px] hover:bg-transparent pr-[12px] pb-[10px] bg-transparent pl-[10px] absolute right-0 bottom-[0]"
          disabled={!question}
          onClick={handleSend}
        >
          <Send className="text-[#000]" />
        </Button>
      </div>
    </div>
  );
};

export default PromptForm;
