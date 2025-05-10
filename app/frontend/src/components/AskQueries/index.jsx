import React, { Fragment, useState } from "react";
import PromptForm from "./PromptForm";
import logo from "../../../public/favicon.ico";
import ScrollToBottom from "react-scroll-to-bottom";

const renderPrompt = (question) => {
  return (
    <div className="p-2 px-4 bg-[#18181b] text-[#fff] max-w-[500px] w-max  rounded-md ml-auto text-wrap text-[14px] lg:text-[16px] mt-10">
      {question}
    </div>
  );
};

const renderResult = (response, isStreaming) => {
  return (
    <div className="flex mt-10">
      <div className="mt-1">
        <img src={logo} alt="logo img" width={"30px"} />
      </div>
      <div className=" px-4 w-full  rounded-md mr-auto text-wrap text-[14px] lg:text-[16px]">
        {response?.message.content}
        {isStreaming && "⚫"}
      </div>
    </div>
  );
};

const analyzing = () => {
  return (
    <div className="min-h-[100px] flex">
      <div className="mt-1">
        <img src={logo} alt="logo img" width={"30px"} />
      </div>
      <div className="px-4 w-full thinking_p rounded-md mr-auto text-wrap text-[14px] lg:text-[16px]">Thinking...</div>
    </div>
  );
};

const renderInitialPage = () => {
  return (
    <div className="h-full flex justify-center items-center">
      <h3 className="font-bold text-[18px] text-[#101010]">Hi, How can i assist you today?</h3>
    </div>
  );
};

const AskQueries = () => {
  const [isStreaming, setIsStreaming] = useState({});
  const [streamedAnswers, setStreamedAnswers] = useState({});
  const [messages, setMessages] = useState([]);

  return (
    <div className=" flex flex-col w-full text-wrap mt-5 ">
      <ScrollToBottom
        scrollViewClassName="lg:px-[15%] "
        className="w-full flex flex-col pb-20 h-[55vh] xl:h-[65vh] overflow-y-auto "
      >
        {messages.length === 0
          ? renderInitialPage()
          : messages.map((message, index) => {
              return (
                <Fragment key={index}>
                  {message.question && renderPrompt(message.question)}
                  {message.isAnalyzing && !isStreaming[message.id] && !streamedAnswers[message.id]
                    ? analyzing()
                    : (message.response || isStreaming[message.id]) &&
                      renderResult(
                        isStreaming[message.id] ? streamedAnswers[message.id] : message.response,
                        isStreaming[message.id]
                      )}
                </Fragment>
              );
            })}
      </ScrollToBottom>
      <PromptForm
        messages={messages}
        setMessages={setMessages}
        setIsStreaming={setIsStreaming}
        streamedAnswers={streamedAnswers}
        setStreamedAnswers={setStreamedAnswers}
      />
    </div>
  );
};

export default AskQueries;
