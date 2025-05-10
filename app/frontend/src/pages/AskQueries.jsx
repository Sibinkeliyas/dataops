import AskQueries from "@/components/AskQueries";
import React, { useState } from "react";

const AskQueriesPage = () => {
  return (
    <div className="container mx-auto px-4 py-8 flex justify-center items-center flex-col">
      <div className="w-full">
        <h1 className="text-3xl font-bold mb-6">AI Chatbot</h1>
      </div>
      <section className="mb-12 w-full ">
        <AskQueries />
      </section>
    </div>
  );
};

export default AskQueriesPage;
